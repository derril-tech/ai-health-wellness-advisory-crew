"""
Intake Normalizer Service
Handles questionnaire normalization, PAR-Q screening, and risk assessment.
"""
import structlog
from typing import Dict, Any, List, Tuple
from datetime import datetime

logger = structlog.get_logger()

class IntakeNormalizer:
    """Normalizes intake questionnaire data and performs safety screening."""
    
    def __init__(self):
        self.parq_questions = [
            "Has your doctor ever said that you have a heart condition?",
            "Do you feel pain in your chest when you do physical activity?",
            "In the past month, have you had chest pain when you were not doing physical activity?",
            "Do you lose your balance because of dizziness or do you ever lose consciousness?",
            "Do you have a bone or joint problem that could be made worse by a change in your physical activity?",
            "Is your doctor currently prescribing drugs for your blood pressure or heart condition?",
            "Do you know of any other reason why you should not do physical activity?"
        ]
        
        self.risk_factors = {
            "age": {"high": 65, "medium": 45},
            "bmi": {"high": 35, "medium": 30},
            "blood_pressure": {"high": 140, "medium": 130},
            "heart_rate": {"high": 100, "medium": 90},
        }
    
    def normalize_profile(self, questionnaire_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize questionnaire data into a structured health profile.
        
        Args:
            questionnaire_data: Raw questionnaire responses
            
        Returns:
            Normalized health profile with risk assessment
        """
        logger.info("Starting intake normalization", user_id=questionnaire_data.get("user_id"))
        
        try:
            # Extract basic information
            profile = {
                "user_id": questionnaire_data.get("user_id"),
                "height_cm": self._extract_height(questionnaire_data),
                "weight_kg": self._extract_weight(questionnaire_data),
                "age": self._extract_age(questionnaire_data),
                "sex_at_birth": questionnaire_data.get("sex_at_birth"),
                "activity_level": questionnaire_data.get("activity_level", "moderate"),
                "goal": questionnaire_data.get("goal"),
                "experience_level": questionnaire_data.get("experience_level", "beginner"),
                "equipment_access": questionnaire_data.get("equipment_access", []),
                "allergies": questionnaire_data.get("allergies", []),
                "injuries": self._normalize_injuries(questionnaire_data.get("injuries", [])),
                "medications": self._normalize_medications(questionnaire_data.get("medications", [])),
            }
            
            # Calculate derived metrics
            profile["bmi"] = self._calculate_bmi(profile["height_cm"], profile["weight_kg"])
            profile["parq_flags"] = self._assess_parq(questionnaire_data)
            profile["risk_level"] = self._assess_risk_level(profile)
            profile["cleared"] = self._determine_clearance(profile)
            profile["normalized_at"] = datetime.utcnow().isoformat()
            
            logger.info("Intake normalization completed", 
                       user_id=profile["user_id"],
                       risk_level=profile["risk_level"],
                       cleared=profile["cleared"])
            
            return profile
            
        except Exception as e:
            logger.error("Intake normalization failed", 
                        user_id=questionnaire_data.get("user_id"),
                        error=str(e))
            raise
    
    def _extract_height(self, data: Dict[str, Any]) -> int:
        """Extract and normalize height in centimeters."""
        height = data.get("height_cm")
        if not height:
            # Try to convert from feet/inches
            feet = data.get("height_feet")
            inches = data.get("height_inches")
            if feet and inches:
                height = (feet * 12 + inches) * 2.54
        return int(height) if height else None
    
    def _extract_weight(self, data: Dict[str, Any]) -> float:
        """Extract and normalize weight in kilograms."""
        weight = data.get("weight_kg")
        if not weight:
            # Try to convert from pounds
            lbs = data.get("weight_lbs")
            if lbs:
                weight = lbs * 0.453592
        return float(weight) if weight else None
    
    def _extract_age(self, data: Dict[str, Any]) -> int:
        """Extract age from various formats."""
        age = data.get("age")
        if not age:
            # Try to calculate from birth date
            birth_date = data.get("birth_date")
            if birth_date:
                try:
                    birth_dt = datetime.fromisoformat(birth_date.replace('Z', '+00:00'))
                    age = (datetime.now() - birth_dt).days // 365
                except:
                    pass
        return int(age) if age else None
    
    def _calculate_bmi(self, height_cm: int, weight_kg: float) -> float:
        """Calculate BMI from height and weight."""
        if not height_cm or not weight_kg:
            return None
        height_m = height_cm / 100
        return round(weight_kg / (height_m ** 2), 1)
    
    def _normalize_injuries(self, injuries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Normalize injury data."""
        normalized = []
        for injury in injuries:
            normalized.append({
                "type": injury.get("type"),
                "location": injury.get("location"),
                "severity": injury.get("severity", "mild"),
                "recovery_status": injury.get("recovery_status", "recovered"),
                "date": injury.get("date"),
                "notes": injury.get("notes"),
            })
        return normalized
    
    def _normalize_medications(self, medications: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Normalize medication data."""
        normalized = []
        for med in medications:
            normalized.append({
                "name": med.get("name"),
                "dosage": med.get("dosage"),
                "frequency": med.get("frequency"),
                "purpose": med.get("purpose"),
                "start_date": med.get("start_date"),
                "notes": med.get("notes"),
            })
        return normalized
    
    def _assess_parq(self, data: Dict[str, Any]) -> List[str]:
        """Assess PAR-Q responses and return flags."""
        flags = []
        
        # Check PAR-Q responses
        parq_responses = data.get("parq_responses", {})
        for i, question in enumerate(self.parq_questions):
            response = parq_responses.get(f"parq_{i+1}")
            if response == "yes":
                flags.append(f"PAR-Q_{i+1}: {question}")
        
        # Check additional health conditions
        health_conditions = data.get("health_conditions", [])
        for condition in health_conditions:
            if condition.get("severity") in ["moderate", "severe"]:
                flags.append(f"Health condition: {condition.get('name')}")
        
        return flags
    
    def _assess_risk_level(self, profile: Dict[str, Any]) -> str:
        """Assess overall risk level based on profile data."""
        risk_score = 0
        
        # Age risk
        if profile.get("age"):
            if profile["age"] >= self.risk_factors["age"]["high"]:
                risk_score += 3
            elif profile["age"] >= self.risk_factors["age"]["medium"]:
                risk_score += 1
        
        # BMI risk
        if profile.get("bmi"):
            if profile["bmi"] >= self.risk_factors["bmi"]["high"]:
                risk_score += 3
            elif profile["bmi"] >= self.risk_factors["bmi"]["medium"]:
                risk_score += 1
        
        # PAR-Q flags
        risk_score += len(profile.get("parq_flags", [])) * 2
        
        # Injury risk
        active_injuries = [i for i in profile.get("injuries", []) 
                          if i.get("recovery_status") != "recovered"]
        risk_score += len(active_injuries) * 2
        
        # Medication risk
        medications = profile.get("medications", [])
        risk_score += len(medications) * 1
        
        # Determine risk level
        if risk_score >= 6:
            return "high"
        elif risk_score >= 3:
            return "medium"
        else:
            return "low"
    
    def _determine_clearance(self, profile: Dict[str, Any]) -> bool:
        """Determine if user is cleared for exercise."""
        # High risk requires medical clearance
        if profile.get("risk_level") == "high":
            return False
        
        # PAR-Q flags require medical clearance
        if profile.get("parq_flags"):
            return False
        
        # Active injuries require medical clearance
        active_injuries = [i for i in profile.get("injuries", []) 
                          if i.get("recovery_status") != "recovered"]
        if active_injuries:
            return False
        
        return True
    
    def generate_safety_warnings(self, profile: Dict[str, Any]) -> List[str]:
        """Generate safety warnings based on profile."""
        warnings = []
        
        if profile.get("risk_level") == "high":
            warnings.append("High risk profile detected. Medical clearance required before starting any exercise program.")
        
        if profile.get("parq_flags"):
            warnings.append("PAR-Q screening indicates potential health risks. Please consult with a healthcare provider.")
        
        if profile.get("bmi") and profile["bmi"] >= 35:
            warnings.append("High BMI detected. Consider consulting with a healthcare provider before starting exercise.")
        
        active_injuries = [i for i in profile.get("injuries", []) 
                          if i.get("recovery_status") != "recovered"]
        if active_injuries:
            warnings.append("Active injuries detected. Medical clearance recommended before exercise.")
        
        medications = profile.get("medications", [])
        if medications:
            warnings.append("Medications detected. Consult with healthcare provider about exercise interactions.")
        
        return warnings
