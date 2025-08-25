from celery import shared_task
from typing import Dict, Any, List
import structlog

logger = structlog.get_logger()

@shared_task(bind=True, name="tdee_macro_engine.calculate_tdee")
def calculate_tdee(self, profile: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate Total Daily Energy Expenditure using Mifflin-St Jeor formula.
    
    Args:
        profile: User health profile with height, weight, age, sex, activity
        
    Returns:
        TDEE calculation and macro targets
    """
    logger.info("Starting TDEE calculation", task_id=self.request.id)
    
    try:
        # Extract profile data
        weight_kg = profile.get("weight_kg")
        height_cm = profile.get("height_cm") 
        age = profile.get("age")
        sex = profile.get("sex_at_birth")
        activity_level = profile.get("activity_level", "moderate")
        goal = profile.get("goal", "maintain")
        
        # Activity multipliers
        activity_multipliers = {
            "sedentary": 1.2,
            "light": 1.375,
            "moderate": 1.55,
            "active": 1.725,
            "very_active": 1.9
        }
        
        # Mifflin-St Jeor BMR calculation
        if sex == "male":
            bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
        else:
            bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161
            
        # Calculate TDEE
        tdee = bmr * activity_multipliers.get(activity_level, 1.55)
        
        # Apply goal adjustments
        goal_adjustments = {
            "lose": 0.85,  # 15% deficit
            "maintain": 1.0,
            "gain": 1.15   # 15% surplus
        }
        
        target_calories = int(tdee * goal_adjustments.get(goal, 1.0))
        
        # Calculate macros (protein 1.6-2.2g/kg, fats ≥0.6g/kg, carbs fill remainder)
        protein_g = int(weight_kg * 2.0)  # 2g/kg for most goals
        fat_g = int(weight_kg * 0.8)      # 0.8g/kg minimum
        carb_g = int((target_calories - (protein_g * 4) - (fat_g * 9)) / 4)
        
        result = {
            "tdee": int(tdee),
            "target_calories": target_calories,
            "macros": {
                "protein_g": protein_g,
                "fat_g": fat_g,
                "carb_g": carb_g,
                "fiber_g": int(target_calories * 0.014),  # 14g per 1000 kcal
                "sodium_mg": 2300,  # Default sodium target
                "water_ml": int(weight_kg * 35)  # 35ml/kg baseline
            },
            "goal": goal,
            "activity_level": activity_level
        }
        
        logger.info("TDEE calculation completed", 
                   task_id=self.request.id, 
                   tdee=result["tdee"],
                   target_calories=result["target_calories"])
        
        return result
        
    except Exception as e:
        logger.error("TDEE calculation failed", 
                    task_id=self.request.id, 
                    error=str(e))
        raise

@shared_task(bind=True, name="tdee_macro_engine.plan_macros")
def plan_macros(self, profile: Dict[str, Any], timeline_weeks: int = 12) -> List[Dict[str, Any]]:
    """
    Create week-by-week macro periodization plan.
    
    Args:
        profile: User health profile
        timeline_weeks: Number of weeks for the plan
        
    Returns:
        List of weekly macro targets
    """
    logger.info("Starting macro planning", task_id=self.request.id, weeks=timeline_weeks)
    
    try:
        # Get base TDEE calculation
        tdee_result = calculate_tdee(profile)
        
        weekly_plans = []
        for week in range(1, timeline_weeks + 1):
            # TODO: Implement periodization logic
            # - Gradual adjustments based on progress
            # - Refeed weeks for weight loss
            # - Deload weeks for training
            # - Holiday/special event adjustments
            
            weekly_plans.append({
                "week": week,
                "kcal": tdee_result["target_calories"],
                "macros": tdee_result["macros"].copy(),
                "refeed": False,  # TODO: Determine refeed weeks
                "notes": f"Week {week} macro targets"
            })
        
        logger.info("Macro planning completed", 
                   task_id=self.request.id, 
                   weeks_planned=len(weekly_plans))
        
        return weekly_plans
        
    except Exception as e:
        logger.error("Macro planning failed", 
                    task_id=self.request.id, 
                    error=str(e))
        raise
