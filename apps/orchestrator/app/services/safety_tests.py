"""
Safety Regression Tests Service
Validates PAR-Q screening, contraindications, and deload triggers for safety compliance.
"""
import structlog
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import asyncio
import json
from dataclasses import asdict

logger = structlog.get_logger()

class TestType(Enum):
    PAR_Q_SCREENING = "par_q_screening"
    CONTRAINDICATIONS = "contraindications"
    DELOAD_TRIGGERS = "deload_triggers"
    SAFETY_GATES = "safety_gates"

class TestStatus(Enum):
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    SKIPPED = "skipped"

class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class SafetyTestResult:
    """Result of a safety test."""
    test_type: TestType
    test_name: str
    status: TestStatus
    risk_level: RiskLevel
    description: str
    details: Dict[str, Any]
    timestamp: datetime
    user_id: Optional[str] = None
    program_id: Optional[str] = None

@dataclass
class PARQTestData:
    """PAR-Q test data for validation."""
    chest_pain: bool
    chest_pain_activity: bool
    chest_pain_recent: bool
    balance_problems: bool
    bone_problems: bool
    blood_pressure_meds: bool
    other_reasons: bool
    age: int
    medical_conditions: List[str]
    medications: List[str]

@dataclass
class ContraindicationTestData:
    """Contraindication test data."""
    exercise_name: str
    user_injuries: List[str]
    user_conditions: List[str]
    user_medications: List[str]
    exercise_contraindications: List[str]
    exercise_modifications: List[str]

@dataclass
class DeloadTriggerTestData:
    """Deload trigger test data."""
    fatigue_level: int  # 1-10
    sleep_quality: int  # 1-10
    stress_level: int  # 1-10
    workout_adherence: float  # 0-1
    performance_trend: str  # "improving", "plateau", "declining"
    recent_injuries: List[str]
    recovery_indicators: Dict[str, Any]

class SafetyTestsService:
    """Service for running safety regression tests."""
    
    def __init__(self):
        self.logger = structlog.get_logger()
        self.test_results: List[SafetyTestResult] = []
        
        # Load test configurations
        self.parq_rules = self._load_parq_rules()
        self.contraindication_rules = self._load_contraindication_rules()
        self.deload_rules = self._load_deload_rules()
    
    def _load_parq_rules(self) -> Dict[str, Any]:
        """Load PAR-Q screening rules."""
        return {
            "critical_flags": [
                "chest_pain",
                "chest_pain_activity",
                "chest_pain_recent"
            ],
            "high_risk_flags": [
                "balance_problems",
                "bone_problems"
            ],
            "medium_risk_flags": [
                "blood_pressure_meds",
                "other_reasons"
            ],
            "age_risk_thresholds": {
                "low": 18,
                "medium": 45,
                "high": 65
            },
            "medical_condition_risks": {
                "diabetes": "medium",
                "heart_disease": "high",
                "hypertension": "medium",
                "asthma": "medium",
                "arthritis": "medium",
                "osteoporosis": "high"
            }
        }
    
    def _load_contraindication_rules(self) -> Dict[str, Any]:
        """Load contraindication rules."""
        return {
            "injury_exercise_mapping": {
                "lower_back_pain": ["deadlift", "squat", "bent_over_row"],
                "knee_pain": ["squat", "lunge", "leg_press"],
                "shoulder_pain": ["bench_press", "overhead_press", "pull_up"],
                "wrist_pain": ["push_up", "plank", "handstand"],
                "ankle_pain": ["jump", "sprint", "box_jump"]
            },
            "condition_exercise_mapping": {
                "hypertension": ["heavy_lifting", "isometric_holds"],
                "diabetes": ["high_intensity_interval"],
                "asthma": ["endurance_running", "high_intensity"],
                "heart_condition": ["heavy_lifting", "high_intensity"]
            },
            "medication_exercise_mapping": {
                "blood_thinners": ["contact_sports", "high_impact"],
                "beta_blockers": ["high_intensity", "rapid_heart_rate"],
                "diuretics": ["endurance_activities", "dehydration_risk"]
            }
        }
    
    def _load_deload_rules(self) -> Dict[str, Any]:
        """Load deload trigger rules."""
        return {
            "fatigue_threshold": 7,  # 1-10 scale
            "sleep_quality_threshold": 5,  # 1-10 scale
            "stress_threshold": 7,  # 1-10 scale
            "adherence_threshold": 0.7,  # 0-1 scale
            "performance_decline_threshold": 0.8,  # 0-1 scale
            "recovery_indicators": {
                "hrv_decline": 0.2,  # 20% decline
                "sleep_decline": 1.0,  # 1 hour less
                "mood_decline": 2,  # 2 points on 1-10 scale
                "energy_decline": 2  # 2 points on 1-10 scale
            }
        }
    
    async def run_all_safety_tests(self, user_id: str, program_id: str, 
                                 test_data: Dict[str, Any]) -> List[SafetyTestResult]:
        """Run all safety tests for a user."""
        self.logger.info("Running safety tests", user_id=user_id, program_id=program_id)
        
        results = []
        
        # Run PAR-Q tests
        if "parq_data" in test_data:
            parq_results = await self.run_parq_tests(user_id, program_id, test_data["parq_data"])
            results.extend(parq_results)
        
        # Run contraindication tests
        if "contraindication_data" in test_data:
            contraindication_results = await self.run_contraindication_tests(
                user_id, program_id, test_data["contraindication_data"]
            )
            results.extend(contraindication_results)
        
        # Run deload trigger tests
        if "deload_data" in test_data:
            deload_results = await self.run_deload_trigger_tests(
                user_id, program_id, test_data["deload_data"]
            )
            results.extend(deload_results)
        
        # Run safety gate tests
        safety_gate_results = await self.run_safety_gate_tests(user_id, program_id, results)
        results.extend(safety_gate_results)
        
        # Store results
        self.test_results.extend(results)
        
        return results
    
    async def run_parq_tests(self, user_id: str, program_id: str, 
                           parq_data: Dict[str, Any]) -> List[SafetyTestResult]:
        """Run PAR-Q screening tests."""
        results = []
        timestamp = datetime.now()
        
        # Test critical flags
        critical_flags = []
        for flag in self.parq_rules["critical_flags"]:
            if parq_data.get(flag, False):
                critical_flags.append(flag)
        
        if critical_flags:
            results.append(SafetyTestResult(
                test_type=TestType.PAR_Q_SCREENING,
                test_name="Critical Health Flags",
                status=TestStatus.FAILED,
                risk_level=RiskLevel.CRITICAL,
                description=f"Critical health flags detected: {', '.join(critical_flags)}",
                details={
                    "flags": critical_flags,
                    "recommendation": "Immediate medical consultation required before exercise"
                },
                timestamp=timestamp,
                user_id=user_id,
                program_id=program_id
            ))
        else:
            results.append(SafetyTestResult(
                test_type=TestType.PAR_Q_SCREENING,
                test_name="Critical Health Flags",
                status=TestStatus.PASSED,
                risk_level=RiskLevel.LOW,
                description="No critical health flags detected",
                details={"flags": []},
                timestamp=timestamp,
                user_id=user_id,
                program_id=program_id
            ))
        
        # Test high risk flags
        high_risk_flags = []
        for flag in self.parq_rules["high_risk_flags"]:
            if parq_data.get(flag, False):
                high_risk_flags.append(flag)
        
        if high_risk_flags:
            results.append(SafetyTestResult(
                test_type=TestType.PAR_Q_SCREENING,
                test_name="High Risk Health Flags",
                status=TestStatus.WARNING,
                risk_level=RiskLevel.HIGH,
                description=f"High risk health flags detected: {', '.join(high_risk_flags)}",
                details={
                    "flags": high_risk_flags,
                    "recommendation": "Medical clearance recommended before starting program"
                },
                timestamp=timestamp,
                user_id=user_id,
                program_id=program_id
            ))
        
        # Test age-based risk
        age = parq_data.get("age", 0)
        if age >= self.parq_rules["age_risk_thresholds"]["high"]:
            results.append(SafetyTestResult(
                test_type=TestType.PAR_Q_SCREENING,
                test_name="Age Risk Assessment",
                status=TestStatus.WARNING,
                risk_level=RiskLevel.HIGH,
                description=f"High age risk: {age} years old",
                details={
                    "age": age,
                    "threshold": self.parq_rules["age_risk_thresholds"]["high"],
                    "recommendation": "Medical consultation recommended"
                },
                timestamp=timestamp,
                user_id=user_id,
                program_id=program_id
            ))
        
        # Test medical conditions
        medical_conditions = parq_data.get("medical_conditions", [])
        high_risk_conditions = []
        for condition in medical_conditions:
            if condition in self.parq_rules["medical_condition_risks"]:
                risk_level = self.parq_rules["medical_condition_risks"][condition]
                if risk_level == "high":
                    high_risk_conditions.append(condition)
        
        if high_risk_conditions:
            results.append(SafetyTestResult(
                test_type=TestType.PAR_Q_SCREENING,
                test_name="Medical Conditions Risk",
                status=TestStatus.WARNING,
                risk_level=RiskLevel.HIGH,
                description=f"High risk medical conditions: {', '.join(high_risk_conditions)}",
                details={
                    "conditions": high_risk_conditions,
                    "recommendation": "Medical clearance required"
                },
                timestamp=timestamp,
                user_id=user_id,
                program_id=program_id
            ))
        
        return results
    
    async def run_contraindication_tests(self, user_id: str, program_id: str, 
                                       contraindication_data: List[Dict[str, Any]]) -> List[SafetyTestResult]:
        """Run contraindication tests for exercises."""
        results = []
        timestamp = datetime.now()
        
        for exercise_data in contraindication_data:
            exercise_name = exercise_data["exercise_name"]
            user_injuries = exercise_data.get("user_injuries", [])
            user_conditions = exercise_data.get("user_conditions", [])
            user_medications = exercise_data.get("user_medications", [])
            exercise_contraindications = exercise_data.get("exercise_contraindications", [])
            
            # Check injury contraindications
            injury_conflicts = []
            for injury in user_injuries:
                if injury in self.contraindication_rules["injury_exercise_mapping"]:
                    contraindicated_exercises = self.contraindication_rules["injury_exercise_mapping"][injury]
                    if exercise_name in contraindicated_exercises:
                        injury_conflicts.append(injury)
            
            # Check condition contraindications
            condition_conflicts = []
            for condition in user_conditions:
                if condition in self.contraindication_rules["condition_exercise_mapping"]:
                    contraindicated_exercises = self.contraindication_rules["condition_exercise_mapping"][condition]
                    if exercise_name in contraindicated_exercises:
                        condition_conflicts.append(condition)
            
            # Check medication contraindications
            medication_conflicts = []
            for medication in user_medications:
                if medication in self.contraindication_rules["medication_exercise_mapping"]:
                    contraindicated_exercises = self.contraindication_rules["medication_exercise_mapping"][medication]
                    if exercise_name in contraindicated_exercises:
                        medication_conflicts.append(medication)
            
            # Determine overall risk level
            total_conflicts = len(injury_conflicts) + len(condition_conflicts) + len(medication_conflicts)
            
            if total_conflicts > 0:
                risk_level = RiskLevel.HIGH if total_conflicts > 1 else RiskLevel.MEDIUM
                status = TestStatus.FAILED if total_conflicts > 1 else TestStatus.WARNING
                
                results.append(SafetyTestResult(
                    test_type=TestType.CONTRAINDICATIONS,
                    test_name=f"Exercise Contraindication: {exercise_name}",
                    status=status,
                    risk_level=risk_level,
                    description=f"Contraindications found for {exercise_name}",
                    details={
                        "exercise": exercise_name,
                        "injury_conflicts": injury_conflicts,
                        "condition_conflicts": condition_conflicts,
                        "medication_conflicts": medication_conflicts,
                        "total_conflicts": total_conflicts,
                        "recommendation": "Consider exercise modification or substitution"
                    },
                    timestamp=timestamp,
                    user_id=user_id,
                    program_id=program_id
                ))
            else:
                results.append(SafetyTestResult(
                    test_type=TestType.CONTRAINDICATIONS,
                    test_name=f"Exercise Contraindication: {exercise_name}",
                    status=TestStatus.PASSED,
                    risk_level=RiskLevel.LOW,
                    description=f"No contraindications for {exercise_name}",
                    details={"exercise": exercise_name},
                    timestamp=timestamp,
                    user_id=user_id,
                    program_id=program_id
                ))
        
        return results
    
    async def run_deload_trigger_tests(self, user_id: str, program_id: str, 
                                     deload_data: Dict[str, Any]) -> List[SafetyTestResult]:
        """Run deload trigger tests."""
        results = []
        timestamp = datetime.now()
        
        # Test fatigue threshold
        fatigue_level = deload_data.get("fatigue_level", 5)
        if fatigue_level >= self.deload_rules["fatigue_threshold"]:
            results.append(SafetyTestResult(
                test_type=TestType.DELOAD_TRIGGERS,
                test_name="Fatigue Level Check",
                status=TestStatus.WARNING,
                risk_level=RiskLevel.MEDIUM,
                description=f"High fatigue level detected: {fatigue_level}/10",
                details={
                    "fatigue_level": fatigue_level,
                    "threshold": self.deload_rules["fatigue_threshold"],
                    "recommendation": "Consider deload week or reduced intensity"
                },
                timestamp=timestamp,
                user_id=user_id,
                program_id=program_id
            ))
        
        # Test sleep quality
        sleep_quality = deload_data.get("sleep_quality", 5)
        if sleep_quality <= self.deload_rules["sleep_quality_threshold"]:
            results.append(SafetyTestResult(
                test_type=TestType.DELOAD_TRIGGERS,
                test_name="Sleep Quality Check",
                status=TestStatus.WARNING,
                risk_level=RiskLevel.MEDIUM,
                description=f"Poor sleep quality detected: {sleep_quality}/10",
                details={
                    "sleep_quality": sleep_quality,
                    "threshold": self.deload_rules["sleep_quality_threshold"],
                    "recommendation": "Focus on sleep hygiene and recovery"
                },
                timestamp=timestamp,
                user_id=user_id,
                program_id=program_id
            ))
        
        # Test stress level
        stress_level = deload_data.get("stress_level", 5)
        if stress_level >= self.deload_rules["stress_threshold"]:
            results.append(SafetyTestResult(
                test_type=TestType.DELOAD_TRIGGERS,
                test_name="Stress Level Check",
                status=TestStatus.WARNING,
                risk_level=RiskLevel.MEDIUM,
                description=f"High stress level detected: {stress_level}/10",
                details={
                    "stress_level": stress_level,
                    "threshold": self.deload_rules["stress_threshold"],
                    "recommendation": "Consider stress management and reduced training load"
                },
                timestamp=timestamp,
                user_id=user_id,
                program_id=program_id
            ))
        
        # Test workout adherence
        workout_adherence = deload_data.get("workout_adherence", 1.0)
        if workout_adherence < self.deload_rules["adherence_threshold"]:
            results.append(SafetyTestResult(
                test_type=TestType.DELOAD_TRIGGERS,
                test_name="Workout Adherence Check",
                status=TestStatus.WARNING,
                risk_level=RiskLevel.MEDIUM,
                description=f"Low workout adherence: {workout_adherence:.1%}",
                details={
                    "adherence": workout_adherence,
                    "threshold": self.deload_rules["adherence_threshold"],
                    "recommendation": "Consider program modification or reduced complexity"
                },
                timestamp=timestamp,
                user_id=user_id,
                program_id=program_id
            ))
        
        # Test performance trend
        performance_trend = deload_data.get("performance_trend", "improving")
        if performance_trend == "declining":
            results.append(SafetyTestResult(
                test_type=TestType.DELOAD_TRIGGERS,
                test_name="Performance Trend Check",
                status=TestStatus.WARNING,
                risk_level=RiskLevel.MEDIUM,
                description="Performance declining trend detected",
                details={
                    "trend": performance_trend,
                    "recommendation": "Consider deload week or program adjustment"
                },
                timestamp=timestamp,
                user_id=user_id,
                program_id=program_id
            ))
        
        # Test recovery indicators
        recovery_indicators = deload_data.get("recovery_indicators", {})
        recovery_issues = []
        
        for indicator, threshold in self.deload_rules["recovery_indicators"].items():
            if indicator in recovery_indicators:
                current_value = recovery_indicators[indicator]
                if indicator.endswith("_decline") and current_value >= threshold:
                    recovery_issues.append(indicator)
        
        if recovery_issues:
            results.append(SafetyTestResult(
                test_type=TestType.DELOAD_TRIGGERS,
                test_name="Recovery Indicators Check",
                status=TestStatus.WARNING,
                risk_level=RiskLevel.MEDIUM,
                description=f"Recovery issues detected: {', '.join(recovery_issues)}",
                details={
                    "issues": recovery_issues,
                    "indicators": recovery_indicators,
                    "recommendation": "Focus on recovery and consider deload"
                },
                timestamp=timestamp,
                user_id=user_id,
                program_id=program_id
            ))
        
        return results
    
    async def run_safety_gate_tests(self, user_id: str, program_id: str, 
                                  previous_results: List[SafetyTestResult]) -> List[SafetyTestResult]:
        """Run safety gate tests based on previous results."""
        results = []
        timestamp = datetime.now()
        
        # Check for critical failures
        critical_failures = [
            result for result in previous_results
            if result.risk_level == RiskLevel.CRITICAL and result.status == TestStatus.FAILED
        ]
        
        if critical_failures:
            results.append(SafetyTestResult(
                test_type=TestType.SAFETY_GATES,
                test_name="Critical Safety Gate",
                status=TestStatus.FAILED,
                risk_level=RiskLevel.CRITICAL,
                description="Critical safety issues detected - program blocked",
                details={
                    "critical_failures": len(critical_failures),
                    "failures": [result.test_name for result in critical_failures],
                    "recommendation": "Program cannot proceed until critical issues are resolved"
                },
                timestamp=timestamp,
                user_id=user_id,
                program_id=program_id
            ))
        
        # Check for high risk warnings
        high_risk_warnings = [
            result for result in previous_results
            if result.risk_level == RiskLevel.HIGH and result.status == TestStatus.WARNING
        ]
        
        if high_risk_warnings:
            results.append(SafetyTestResult(
                test_type=TestType.SAFETY_GATES,
                test_name="High Risk Safety Gate",
                status=TestStatus.WARNING,
                risk_level=RiskLevel.HIGH,
                description="High risk warnings detected - medical clearance recommended",
                details={
                    "high_risk_warnings": len(high_risk_warnings),
                    "warnings": [result.test_name for result in high_risk_warnings],
                    "recommendation": "Medical clearance recommended before program start"
                },
                timestamp=timestamp,
                user_id=user_id,
                program_id=program_id
            ))
        
        # Check overall safety status
        total_tests = len(previous_results)
        passed_tests = len([r for r in previous_results if r.status == TestStatus.PASSED])
        safety_score = passed_tests / total_tests if total_tests > 0 else 1.0
        
        if safety_score >= 0.9:
            results.append(SafetyTestResult(
                test_type=TestType.SAFETY_GATES,
                test_name="Overall Safety Assessment",
                status=TestStatus.PASSED,
                risk_level=RiskLevel.LOW,
                description=f"Safety assessment passed: {safety_score:.1%}",
                details={
                    "safety_score": safety_score,
                    "total_tests": total_tests,
                    "passed_tests": passed_tests,
                    "recommendation": "Program can proceed with standard protocols"
                },
                timestamp=timestamp,
                user_id=user_id,
                program_id=program_id
            ))
        elif safety_score >= 0.7:
            results.append(SafetyTestResult(
                test_type=TestType.SAFETY_GATES,
                test_name="Overall Safety Assessment",
                status=TestStatus.WARNING,
                risk_level=RiskLevel.MEDIUM,
                description=f"Safety assessment warning: {safety_score:.1%}",
                details={
                    "safety_score": safety_score,
                    "total_tests": total_tests,
                    "passed_tests": passed_tests,
                    "recommendation": "Program can proceed with modifications and monitoring"
                },
                timestamp=timestamp,
                user_id=user_id,
                program_id=program_id
            ))
        else:
            results.append(SafetyTestResult(
                test_type=TestType.SAFETY_GATES,
                test_name="Overall Safety Assessment",
                status=TestStatus.FAILED,
                risk_level=RiskLevel.HIGH,
                description=f"Safety assessment failed: {safety_score:.1%}",
                details={
                    "safety_score": safety_score,
                    "total_tests": total_tests,
                    "passed_tests": passed_tests,
                    "recommendation": "Program cannot proceed - safety issues must be resolved"
                },
                timestamp=timestamp,
                user_id=user_id,
                program_id=program_id
            ))
        
        return results
    
    async def get_test_summary(self, user_id: str, program_id: str) -> Dict[str, Any]:
        """Get summary of safety test results for a user/program."""
        user_results = [
            result for result in self.test_results
            if result.user_id == user_id and result.program_id == program_id
        ]
        
        if not user_results:
            return {"message": "No test results found"}
        
        # Group by test type
        results_by_type = {}
        for result in user_results:
            test_type = result.test_type.value
            if test_type not in results_by_type:
                results_by_type[test_type] = []
            results_by_type[test_type].append(result)
        
        # Calculate statistics
        total_tests = len(user_results)
        passed_tests = len([r for r in user_results if r.status == TestStatus.PASSED])
        failed_tests = len([r for r in user_results if r.status == TestStatus.FAILED])
        warning_tests = len([r for r in user_results if r.status == TestStatus.WARNING])
        
        # Risk level breakdown
        risk_breakdown = {}
        for risk_level in RiskLevel:
            risk_breakdown[risk_level.value] = len([
                r for r in user_results if r.risk_level == risk_level
            ])
        
        return {
            "user_id": user_id,
            "program_id": program_id,
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "warning_tests": warning_tests,
            "safety_score": passed_tests / total_tests if total_tests > 0 else 0,
            "risk_breakdown": risk_breakdown,
            "results_by_type": {
                test_type: [asdict(result) for result in results]
                for test_type, results in results_by_type.items()
            },
            "latest_tests": [
                asdict(result) for result in sorted(
                    user_results, key=lambda x: x.timestamp, reverse=True
                )[:10]
            ]
        }
    
    async def export_test_results(self, format: str = "json") -> str:
        """Export all test results."""
        if format == "json":
            return json.dumps([asdict(result) for result in self.test_results], indent=2)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    async def cleanup_old_results(self, days_to_keep: int = 90):
        """Clean up old test results."""
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        original_count = len(self.test_results)
        
        self.test_results = [
            result for result in self.test_results
            if result.timestamp >= cutoff_date
        ]
        
        removed_count = original_count - len(self.test_results)
        self.logger.info("Cleaned up old test results", 
                        removed_count=removed_count, 
                        remaining_count=len(self.test_results))
