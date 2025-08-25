"""
Progress Analyzer Service
Analyzes user progress and generates adjustment recommendations based on multiple data sources.
"""
import structlog
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import math

logger = structlog.get_logger()

class AdjustmentType(Enum):
    """Types of adjustments that can be recommended."""
    CALORIE_INCREASE = "calorie_increase"
    CALORIE_DECREASE = "calorie_decrease"
    PROTEIN_INCREASE = "protein_increase"
    CARBS_ADJUSTMENT = "carbs_adjustment"
    FAT_ADJUSTMENT = "fat_adjustment"
    WORKOUT_VOLUME_INCREASE = "workout_volume_increase"
    WORKOUT_VOLUME_DECREASE = "workout_volume_decrease"
    DELOAD_WEEK = "deload_week"
    HABIT_ADJUSTMENT = "habit_adjustment"
    MINDSET_FOCUS = "mindset_focus"

class ProgressTrend(Enum):
    """Trend indicators for progress analysis."""
    IMPROVING = "improving"
    STABLE = "stable"
    DECLINING = "declining"
    PLATEAUED = "plateaued"

@dataclass
class ProgressMetrics:
    """Progress metrics for analysis."""
    weight_trend: ProgressTrend
    weight_change_kg: float
    body_fat_percentage: Optional[float] = None
    muscle_mass_kg: Optional[float] = None
    workout_adherence_rate: float = 0.0
    nutrition_adherence_rate: float = 0.0
    habit_completion_rate: float = 0.0
    sleep_quality_score: Optional[float] = None
    stress_level: Optional[float] = None
    energy_level: Optional[float] = None
    recovery_score: Optional[float] = None

@dataclass
class AdjustmentRecommendation:
    """A recommended adjustment for the user."""
    type: AdjustmentType
    title: str
    description: str
    rationale: str
    priority: str  # "low", "medium", "high", "urgent"
    confidence: float  # 0.0 to 1.0
    estimated_impact: str
    implementation_notes: List[str]
    data_sources: List[str]

@dataclass
class ProgressAnalysis:
    """Complete progress analysis results."""
    user_id: str
    analysis_date: datetime
    metrics: ProgressMetrics
    recommendations: List[AdjustmentRecommendation]
    summary: str
    next_check_in_date: datetime
    risk_factors: List[str]
    positive_trends: List[str]

class ProgressAnalyzer:
    """Service for analyzing user progress and generating recommendations."""
    
    def __init__(self):
        # Thresholds for different adjustments
        self.thresholds = {
            "weight_loss_stall": 2.0,  # weeks without weight loss
            "weight_gain_stall": 2.0,  # weeks without weight gain
            "low_adherence": 0.7,  # below 70% adherence
            "high_fatigue": 0.3,  # recovery score below 30%
            "stress_threshold": 7.0,  # stress level above 7/10
            "sleep_threshold": 6.0,  # sleep quality below 6/10
        }
        
        # Adjustment confidence weights
        self.confidence_weights = {
            "weight_data": 0.3,
            "workout_data": 0.25,
            "nutrition_data": 0.25,
            "sleep_data": 0.1,
            "stress_data": 0.1,
        }
    
    def analyze_progress(self, user_id: str, user_data: Dict[str, Any]) -> ProgressAnalysis:
        """
        Analyze user progress and generate recommendations.
        
        Args:
            user_id: User ID
            user_data: User's progress data
            
        Returns:
            ProgressAnalysis object with recommendations
        """
        logger.info("Starting progress analysis", user_id=user_id)
        
        try:
            # Extract and calculate metrics
            metrics = self._calculate_metrics(user_data)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(user_id, user_data, metrics)
            
            # Generate summary
            summary = self._generate_summary(metrics, recommendations)
            
            # Identify risk factors and positive trends
            risk_factors = self._identify_risk_factors(metrics, user_data)
            positive_trends = self._identify_positive_trends(metrics, user_data)
            
            # Calculate next check-in date
            next_check_in = self._calculate_next_check_in(user_data, recommendations)
            
            analysis = ProgressAnalysis(
                user_id=user_id,
                analysis_date=datetime.utcnow(),
                metrics=metrics,
                recommendations=recommendations,
                summary=summary,
                next_check_in_date=next_check_in,
                risk_factors=risk_factors,
                positive_trends=positive_trends,
            )
            
            logger.info("Progress analysis completed", 
                       user_id=user_id,
                       recommendations_count=len(recommendations),
                       risk_factors_count=len(risk_factors))
            
            return analysis
            
        except Exception as e:
            logger.error("Failed to analyze progress", 
                        user_id=user_id,
                        error=str(e))
            raise
    
    def _calculate_metrics(self, user_data: Dict[str, Any]) -> ProgressMetrics:
        """Calculate progress metrics from user data."""
        try:
            # Weight trend analysis
            weight_data = user_data.get("weight_logs", [])
            weight_trend, weight_change = self._analyze_weight_trend(weight_data)
            
            # Adherence rates
            workout_adherence = self._calculate_workout_adherence(user_data.get("workout_logs", []))
            nutrition_adherence = self._calculate_nutrition_adherence(user_data.get("nutrition_logs", []))
            habit_adherence = self._calculate_habit_adherence(user_data.get("habit_logs", []))
            
            # Health metrics
            sleep_quality = self._calculate_sleep_quality(user_data.get("sleep_data", []))
            stress_level = self._calculate_stress_level(user_data.get("stress_logs", []))
            energy_level = self._calculate_energy_level(user_data.get("energy_logs", []))
            recovery_score = self._calculate_recovery_score(user_data)
            
            return ProgressMetrics(
                weight_trend=weight_trend,
                weight_change_kg=weight_change,
                workout_adherence_rate=workout_adherence,
                nutrition_adherence_rate=nutrition_adherence,
                habit_completion_rate=habit_adherence,
                sleep_quality_score=sleep_quality,
                stress_level=stress_level,
                energy_level=energy_level,
                recovery_score=recovery_score,
            )
            
        except Exception as e:
            logger.error("Failed to calculate metrics", error=str(e))
            raise
    
    def _analyze_weight_trend(self, weight_logs: List[Dict[str, Any]]) -> Tuple[ProgressTrend, float]:
        """Analyze weight trend over time."""
        if len(weight_logs) < 2:
            return ProgressTrend.STABLE, 0.0
        
        # Sort by date
        sorted_logs = sorted(weight_logs, key=lambda x: x.get("date", ""))
        
        # Calculate weekly averages for the last 4 weeks
        recent_logs = sorted_logs[-28:] if len(sorted_logs) >= 28 else sorted_logs
        
        if len(recent_logs) < 7:
            return ProgressTrend.STABLE, 0.0
        
        # Calculate weekly averages
        weekly_averages = []
        for i in range(0, len(recent_logs), 7):
            week_logs = recent_logs[i:i+7]
            if week_logs:
                avg_weight = sum(log.get("weight_kg", 0) for log in week_logs) / len(week_logs)
                weekly_averages.append(avg_weight)
        
        if len(weekly_averages) < 2:
            return ProgressTrend.STABLE, 0.0
        
        # Calculate trend
        total_change = weekly_averages[-1] - weekly_averages[0]
        weekly_change = total_change / (len(weekly_averages) - 1)
        
        # Determine trend
        if abs(weekly_change) < 0.2:  # Less than 0.2kg per week
            if len(weekly_averages) >= 4:
                return ProgressTrend.PLATEAUED, total_change
            else:
                return ProgressTrend.STABLE, total_change
        elif weekly_change > 0.2:
            return ProgressTrend.IMPROVING, total_change
        else:
            return ProgressTrend.DECLINING, total_change
    
    def _calculate_workout_adherence(self, workout_logs: List[Dict[str, Any]]) -> float:
        """Calculate workout adherence rate."""
        if not workout_logs:
            return 0.0
        
        # Get user's workout schedule
        scheduled_workouts = 0
        completed_workouts = 0
        
        # This would typically come from the user's program
        # For now, assume 4 workouts per week
        weeks_analyzed = 2  # Analyze last 2 weeks
        scheduled_workouts = weeks_analyzed * 4
        completed_workouts = len(workout_logs)
        
        return min(1.0, completed_workouts / scheduled_workouts) if scheduled_workouts > 0 else 0.0
    
    def _calculate_nutrition_adherence(self, nutrition_logs: List[Dict[str, Any]]) -> float:
        """Calculate nutrition adherence rate."""
        if not nutrition_logs:
            return 0.0
        
        # Calculate how often user logs meals
        days_with_logs = len(set(log.get("date", "") for log in nutrition_logs))
        total_days = 14  # Analyze last 2 weeks
        
        return min(1.0, days_with_logs / total_days)
    
    def _calculate_habit_adherence(self, habit_logs: List[Dict[str, Any]]) -> float:
        """Calculate habit adherence rate."""
        if not habit_logs:
            return 0.0
        
        # Calculate completion rate for active habits
        total_expected = 0
        total_completed = 0
        
        # This would typically come from the user's active habits
        # For now, assume 3 daily habits
        days_analyzed = 14  # Analyze last 2 weeks
        total_expected = days_analyzed * 3
        total_completed = len(habit_logs)
        
        return min(1.0, total_completed / total_expected) if total_expected > 0 else 0.0
    
    def _calculate_sleep_quality(self, sleep_data: List[Dict[str, Any]]) -> Optional[float]:
        """Calculate average sleep quality score."""
        if not sleep_data:
            return None
        
        scores = [log.get("quality_score", 0) for log in sleep_data if log.get("quality_score")]
        return sum(scores) / len(scores) if scores else None
    
    def _calculate_stress_level(self, stress_logs: List[Dict[str, Any]]) -> Optional[float]:
        """Calculate average stress level."""
        if not stress_logs:
            return None
        
        levels = [log.get("stress_level", 0) for log in stress_logs if log.get("stress_level")]
        return sum(levels) / len(levels) if levels else None
    
    def _calculate_energy_level(self, energy_logs: List[Dict[str, Any]]) -> Optional[float]:
        """Calculate average energy level."""
        if not energy_logs:
            return None
        
        levels = [log.get("energy_level", 0) for log in energy_logs if log.get("energy_level")]
        return sum(levels) / len(levels) if levels else None
    
    def _calculate_recovery_score(self, user_data: Dict[str, Any]) -> Optional[float]:
        """Calculate overall recovery score."""
        sleep_quality = self._calculate_sleep_quality(user_data.get("sleep_data", []))
        stress_level = self._calculate_stress_level(user_data.get("stress_logs", []))
        energy_level = self._calculate_energy_level(user_data.get("energy_logs", []))
        
        if sleep_quality is None and stress_level is None and energy_level is None:
            return None
        
        # Calculate weighted recovery score
        score = 0
        weight_sum = 0
        
        if sleep_quality is not None:
            score += sleep_quality * 0.4
            weight_sum += 0.4
        
        if stress_level is not None:
            # Invert stress level (lower stress = higher recovery)
            score += (10 - stress_level) * 0.3
            weight_sum += 0.3
        
        if energy_level is not None:
            score += energy_level * 0.3
            weight_sum += 0.3
        
        return score / weight_sum if weight_sum > 0 else None
    
    def _generate_recommendations(self, user_id: str, user_data: Dict[str, Any], 
                                metrics: ProgressMetrics) -> List[AdjustmentRecommendation]:
        """Generate adjustment recommendations based on metrics."""
        recommendations = []
        
        try:
            # Weight-based recommendations
            if metrics.weight_trend == ProgressTrend.PLATEAUED:
                if user_data.get("goal") == "lose_weight":
                    recommendations.append(self._create_calorie_decrease_recommendation(metrics))
                elif user_data.get("goal") == "gain_muscle":
                    recommendations.append(self._create_calorie_increase_recommendation(metrics))
            
            # Adherence-based recommendations
            if metrics.workout_adherence_rate < self.thresholds["low_adherence"]:
                recommendations.append(self._create_workout_adherence_recommendation(metrics))
            
            if metrics.nutrition_adherence_rate < self.thresholds["low_adherence"]:
                recommendations.append(self._create_nutrition_adherence_recommendation(metrics))
            
            # Recovery-based recommendations
            if metrics.recovery_score and metrics.recovery_score < self.thresholds["high_fatigue"]:
                recommendations.append(self._create_deload_recommendation(metrics))
            
            # Stress-based recommendations
            if metrics.stress_level and metrics.stress_level > self.thresholds["stress_threshold"]:
                recommendations.append(self._create_stress_management_recommendation(metrics))
            
            # Sleep-based recommendations
            if metrics.sleep_quality_score and metrics.sleep_quality_score < self.thresholds["sleep_threshold"]:
                recommendations.append(self._create_sleep_improvement_recommendation(metrics))
            
            # Habit-based recommendations
            if metrics.habit_completion_rate < self.thresholds["low_adherence"]:
                recommendations.append(self._create_habit_adjustment_recommendation(metrics))
            
            # Sort by priority and confidence
            recommendations.sort(key=lambda r: (self._priority_to_score(r.priority), r.confidence), reverse=True)
            
            return recommendations[:5]  # Return top 5 recommendations
            
        except Exception as e:
            logger.error("Failed to generate recommendations", error=str(e))
            return []
    
    def _create_calorie_decrease_recommendation(self, metrics: ProgressMetrics) -> AdjustmentRecommendation:
        """Create calorie decrease recommendation."""
        return AdjustmentRecommendation(
            type=AdjustmentType.CALORIE_DECREASE,
            title="Reduce Daily Calories",
            description="Slightly reduce your daily calorie intake to break through the plateau",
            rationale=f"Your weight has plateaued for the past few weeks. A small calorie reduction of 100-200 calories per day can help restart weight loss.",
            priority="medium",
            confidence=0.8,
            estimated_impact="0.2-0.4kg weight loss per week",
            implementation_notes=[
                "Reduce portion sizes slightly",
                "Choose lower-calorie alternatives",
                "Monitor hunger levels",
                "Maintain protein intake"
            ],
            data_sources=["weight_trend", "nutrition_logs"]
        )
    
    def _create_calorie_increase_recommendation(self, metrics: ProgressMetrics) -> AdjustmentRecommendation:
        """Create calorie increase recommendation."""
        return AdjustmentRecommendation(
            type=AdjustmentType.CALORIE_INCREASE,
            title="Increase Daily Calories",
            description="Gradually increase your daily calorie intake to support muscle growth",
            rationale="Your weight has plateaued, which may indicate insufficient calories for muscle building. A small increase can help restart progress.",
            priority="medium",
            confidence=0.7,
            estimated_impact="0.1-0.3kg weight gain per week",
            implementation_notes=[
                "Add 100-200 calories per day",
                "Focus on protein-rich foods",
                "Monitor body composition",
                "Maintain workout intensity"
            ],
            data_sources=["weight_trend", "nutrition_logs"]
        )
    
    def _create_workout_adherence_recommendation(self, metrics: ProgressMetrics) -> AdjustmentRecommendation:
        """Create workout adherence recommendation."""
        return AdjustmentRecommendation(
            type=AdjustmentType.WORKOUT_VOLUME_DECREASE,
            title="Simplify Workout Routine",
            description="Reduce workout complexity to improve consistency",
            rationale=f"Your workout adherence rate is {metrics.workout_adherence_rate:.1%}. Simplifying your routine can help build consistency.",
            priority="high",
            confidence=0.9,
            estimated_impact="Improved workout consistency",
            implementation_notes=[
                "Reduce workout duration",
                "Focus on compound movements",
                "Simplify exercise selection",
                "Set realistic frequency goals"
            ],
            data_sources=["workout_logs", "adherence_metrics"]
        )
    
    def _create_deload_recommendation(self, metrics: ProgressMetrics) -> AdjustmentRecommendation:
        """Create deload week recommendation."""
        return AdjustmentRecommendation(
            type=AdjustmentType.DELOAD_WEEK,
            title="Take a Deload Week",
            description="Reduce training intensity to allow for recovery",
            rationale=f"Your recovery score is {metrics.recovery_score:.1f}/10, indicating high fatigue. A deload week can help restore energy and prevent overtraining.",
            priority="high",
            confidence=0.85,
            estimated_impact="Improved recovery and performance",
            implementation_notes=[
                "Reduce weights by 20-30%",
                "Maintain exercise form",
                "Focus on mobility work",
                "Prioritize sleep and nutrition"
            ],
            data_sources=["recovery_score", "sleep_data", "stress_logs"]
        )
    
    def _create_stress_management_recommendation(self, metrics: ProgressMetrics) -> AdjustmentRecommendation:
        """Create stress management recommendation."""
        return AdjustmentRecommendation(
            type=AdjustmentType.MINDSET_FOCUS,
            title="Focus on Stress Management",
            description="Implement stress reduction techniques to improve recovery",
            rationale=f"Your stress level is {metrics.stress_level:.1f}/10, which can negatively impact progress and recovery.",
            priority="medium",
            confidence=0.8,
            estimated_impact="Improved recovery and adherence",
            implementation_notes=[
                "Practice daily meditation",
                "Implement breathing exercises",
                "Prioritize sleep hygiene",
                "Consider reducing training volume"
            ],
            data_sources=["stress_logs", "recovery_score"]
        )
    
    def _create_sleep_improvement_recommendation(self, metrics: ProgressMetrics) -> AdjustmentRecommendation:
        """Create sleep improvement recommendation."""
        return AdjustmentRecommendation(
            type=AdjustmentType.MINDSET_FOCUS,
            title="Improve Sleep Quality",
            description="Focus on sleep hygiene to enhance recovery and performance",
            rationale=f"Your sleep quality score is {metrics.sleep_quality_score:.1f}/10. Better sleep can significantly improve progress and recovery.",
            priority="medium",
            confidence=0.9,
            estimated_impact="Improved recovery and performance",
            implementation_notes=[
                "Establish consistent sleep schedule",
                "Create relaxing bedtime routine",
                "Optimize sleep environment",
                "Limit screen time before bed"
            ],
            data_sources=["sleep_data", "recovery_score"]
        )
    
    def _create_nutrition_adherence_recommendation(self, metrics: ProgressMetrics) -> AdjustmentRecommendation:
        """Create nutrition adherence recommendation."""
        return AdjustmentRecommendation(
            type=AdjustmentType.HABIT_ADJUSTMENT,
            title="Improve Nutrition Tracking",
            description="Focus on consistent meal logging to better understand your nutrition",
            rationale=f"Your nutrition adherence rate is {metrics.nutrition_adherence_rate:.1%}. Better tracking can help optimize your nutrition plan.",
            priority="medium",
            confidence=0.8,
            estimated_impact="Better nutrition optimization",
            implementation_notes=[
                "Log meals immediately after eating",
                "Use food scale for accuracy",
                "Plan meals in advance",
                "Set meal reminders"
            ],
            data_sources=["nutrition_logs", "adherence_metrics"]
        )
    
    def _create_habit_adjustment_recommendation(self, metrics: ProgressMetrics) -> AdjustmentRecommendation:
        """Create habit adjustment recommendation."""
        return AdjustmentRecommendation(
            type=AdjustmentType.HABIT_ADJUSTMENT,
            title="Simplify Daily Habits",
            description="Reduce habit complexity to improve consistency",
            rationale=f"Your habit completion rate is {metrics.habit_completion_rate:.1%}. Simplifying habits can help build momentum.",
            priority="medium",
            confidence=0.85,
            estimated_impact="Improved habit consistency",
            implementation_notes=[
                "Focus on 1-2 key habits",
                "Set specific, achievable goals",
                "Create clear triggers",
                "Track progress daily"
            ],
            data_sources=["habit_logs", "adherence_metrics"]
        )
    
    def _generate_summary(self, metrics: ProgressMetrics, 
                         recommendations: List[AdjustmentRecommendation]) -> str:
        """Generate a summary of the analysis."""
        summary_parts = []
        
        # Overall progress
        if metrics.weight_trend == ProgressTrend.IMPROVING:
            summary_parts.append("You're making good progress toward your goals.")
        elif metrics.weight_trend == ProgressTrend.PLATEAUED:
            summary_parts.append("Your progress has plateaued, which is normal and expected.")
        elif metrics.weight_trend == ProgressTrend.DECLINING:
            summary_parts.append("Your progress has slowed recently.")
        
        # Adherence
        if metrics.workout_adherence_rate >= 0.8:
            summary_parts.append("Your workout consistency is excellent!")
        elif metrics.workout_adherence_rate >= 0.6:
            summary_parts.append("Your workout consistency is good, with room for improvement.")
        else:
            summary_parts.append("Focus on improving workout consistency.")
        
        # Recovery
        if metrics.recovery_score and metrics.recovery_score < 0.5:
            summary_parts.append("Your recovery needs attention - consider reducing training intensity.")
        
        # Recommendations
        if recommendations:
            priority_recs = [r for r in recommendations if r.priority in ["high", "urgent"]]
            if priority_recs:
                summary_parts.append(f"Focus on {len(priority_recs)} high-priority adjustments to optimize your progress.")
        
        return " ".join(summary_parts) if summary_parts else "Continue with your current plan and monitor progress."
    
    def _identify_risk_factors(self, metrics: ProgressMetrics, user_data: Dict[str, Any]) -> List[str]:
        """Identify potential risk factors."""
        risks = []
        
        if metrics.recovery_score and metrics.recovery_score < 0.3:
            risks.append("High fatigue levels - risk of overtraining")
        
        if metrics.stress_level and metrics.stress_level > 8:
            risks.append("High stress levels - may impact progress")
        
        if metrics.sleep_quality_score and metrics.sleep_quality_score < 5:
            risks.append("Poor sleep quality - may impair recovery")
        
        if metrics.workout_adherence_rate < 0.5:
            risks.append("Low workout adherence - may slow progress")
        
        return risks
    
    def _identify_positive_trends(self, metrics: ProgressMetrics, user_data: Dict[str, Any]) -> List[str]:
        """Identify positive trends."""
        trends = []
        
        if metrics.workout_adherence_rate >= 0.8:
            trends.append("Excellent workout consistency")
        
        if metrics.nutrition_adherence_rate >= 0.8:
            trends.append("Strong nutrition tracking")
        
        if metrics.habit_completion_rate >= 0.8:
            trends.append("Great habit formation")
        
        if metrics.recovery_score and metrics.recovery_score >= 0.7:
            trends.append("Good recovery management")
        
        if metrics.sleep_quality_score and metrics.sleep_quality_score >= 7:
            trends.append("Quality sleep habits")
        
        return trends
    
    def _calculate_next_check_in(self, user_data: Dict[str, Any], 
                               recommendations: List[AdjustmentRecommendation]) -> datetime:
        """Calculate when the next check-in should be scheduled."""
        base_days = 7  # Default 1 week
        
        # Adjust based on recommendations
        if any(r.priority == "urgent" for r in recommendations):
            base_days = 3  # Check in sooner for urgent issues
        elif any(r.priority == "high" for r in recommendations):
            base_days = 5  # Check in sooner for high priority issues
        
        return datetime.utcnow() + timedelta(days=base_days)
    
    def _priority_to_score(self, priority: str) -> int:
        """Convert priority string to numeric score for sorting."""
        priority_scores = {
            "urgent": 4,
            "high": 3,
            "medium": 2,
            "low": 1,
        }
        return priority_scores.get(priority, 0)
