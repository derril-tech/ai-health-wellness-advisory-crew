"""
TDEE & Macro Calculation Engine
Deterministic algorithms for calculating Total Daily Energy Expenditure and macro targets.
"""
import structlog
from typing import Dict, Any, List, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass

logger = structlog.get_logger()

@dataclass
class MacroTargets:
    """Macro targets for a specific period."""
    kcal: int
    protein_g: int
    carbs_g: int
    fat_g: int
    fiber_g: int
    sodium_mg: int
    water_ml: int
    refeed: bool = False

@dataclass
class TDEEProfile:
    """TDEE calculation results."""
    bmr: int  # Basal Metabolic Rate
    tdee: int  # Total Daily Energy Expenditure
    activity_multiplier: float
    goal_adjustment: int
    final_target: int

class TDEEMacroEngine:
    """Engine for calculating TDEE and macro targets."""
    
    def __init__(self):
        # Activity level multipliers (Mifflin-St Jeor)
        self.activity_multipliers = {
            'sedentary': 1.2,      # Little to no exercise
            'light': 1.375,        # Light exercise 1-3 days/week
            'moderate': 1.55,      # Moderate exercise 3-5 days/week
            'active': 1.725,       # Hard exercise 6-7 days/week
            'very_active': 1.9,    # Very hard exercise, physical job
        }
        
        # Goal-based calorie adjustments
        self.goal_adjustments = {
            'lose_weight': -500,      # 0.5kg/week loss
            'lose_weight_aggressive': -750,  # 0.75kg/week loss
            'gain_muscle': 300,       # 0.3kg/week gain
            'maintain': 0,
            'improve_fitness': -200,  # Slight deficit for recomposition
            'sports_performance': 100,  # Slight surplus for performance
        }
        
        # Macro ratios by goal
        self.macro_ratios = {
            'lose_weight': {'protein': 0.35, 'carbs': 0.35, 'fat': 0.30},
            'lose_weight_aggressive': {'protein': 0.40, 'carbs': 0.30, 'fat': 0.30},
            'gain_muscle': {'protein': 0.30, 'carbs': 0.45, 'fat': 0.25},
            'maintain': {'protein': 0.30, 'carbs': 0.40, 'fat': 0.30},
            'improve_fitness': {'protein': 0.30, 'carbs': 0.40, 'fat': 0.30},
            'sports_performance': {'protein': 0.25, 'carbs': 0.50, 'fat': 0.25},
        }
    
    def calculate_tdee(self, profile: Dict[str, Any]) -> TDEEProfile:
        """
        Calculate Total Daily Energy Expenditure using Mifflin-St Jeor equation.
        
        Args:
            profile: Health profile with age, weight, height, sex, activity_level
            
        Returns:
            TDEEProfile with BMR, TDEE, and final target
        """
        logger.info("Calculating TDEE", user_id=profile.get("user_id"))
        
        try:
            # Extract profile data
            age = profile.get("age")
            weight_kg = profile.get("weight_kg")
            height_cm = profile.get("height_cm")
            sex = profile.get("sex_at_birth")
            activity_level = profile.get("activity_level", "moderate")
            goal = profile.get("goal", "maintain")
            
            if not all([age, weight_kg, height_cm, sex]):
                raise ValueError("Missing required profile data for TDEE calculation")
            
            # Calculate BMR using Mifflin-St Jeor equation
            if sex == "male":
                bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) + 5
            else:
                bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) - 161
            
            bmr = int(bmr)
            
            # Apply activity multiplier
            activity_multiplier = self.activity_multipliers.get(activity_level, 1.55)
            tdee = int(bmr * activity_multiplier)
            
            # Apply goal-based adjustment
            goal_adjustment = self.goal_adjustments.get(goal, 0)
            final_target = tdee + goal_adjustment
            
            # Ensure minimum safe calorie intake
            min_calories = 1200 if sex == "female" else 1500
            if final_target < min_calories:
                logger.warning("Target calories below minimum, adjusting", 
                             user_id=profile.get("user_id"),
                             target=final_target,
                             min_calories=min_calories)
                final_target = min_calories
            
            result = TDEEProfile(
                bmr=bmr,
                tdee=tdee,
                activity_multiplier=activity_multiplier,
                goal_adjustment=goal_adjustment,
                final_target=final_target
            )
            
            logger.info("TDEE calculation completed", 
                       user_id=profile.get("user_id"),
                       bmr=bmr,
                       tdee=tdee,
                       final_target=final_target)
            
            return result
            
        except Exception as e:
            logger.error("TDEE calculation failed", 
                        user_id=profile.get("user_id"),
                        error=str(e))
            raise
    
    def plan_macros(self, profile: Dict[str, Any], program_weeks: int = 12) -> List[MacroTargets]:
        """
        Plan macro targets for the entire program with periodization.
        
        Args:
            profile: Health profile
            program_weeks: Number of weeks in the program
            
        Returns:
            List of MacroTargets for each week
        """
        logger.info("Planning macros", 
                   user_id=profile.get("user_id"),
                   program_weeks=program_weeks)
        
        try:
            # Calculate base TDEE
            tdee_profile = self.calculate_tdee(profile)
            goal = profile.get("goal", "maintain")
            experience_level = profile.get("experience_level", "beginner")
            
            # Get base macro ratios
            base_ratios = self.macro_ratios.get(goal, self.macro_ratios["maintain"])
            
            # Calculate protein needs (g/kg bodyweight)
            weight_kg = profile.get("weight_kg")
            if goal in ["lose_weight", "lose_weight_aggressive"]:
                protein_g_per_kg = 2.2  # Higher protein for weight loss
            elif goal == "gain_muscle":
                protein_g_per_kg = 2.0  # High protein for muscle building
            else:
                protein_g_per_kg = 1.8  # Moderate protein for maintenance
            
            base_protein_g = int(weight_kg * protein_g_per_kg)
            
            macro_plan = []
            
            for week in range(1, program_weeks + 1):
                # Calculate weekly adjustments
                weekly_kcal = self._calculate_weekly_kcal(
                    tdee_profile.final_target, 
                    week, 
                    program_weeks, 
                    goal,
                    experience_level
                )
                
                # Calculate macros
                protein_g = self._calculate_protein(weekly_kcal, base_protein_g, goal)
                fat_g = self._calculate_fat(weekly_kcal, goal)
                carbs_g = self._calculate_carbs(weekly_kcal, protein_g, fat_g)
                
                # Calculate additional nutrients
                fiber_g = self._calculate_fiber(profile, carbs_g)
                sodium_mg = self._calculate_sodium(profile)
                water_ml = self._calculate_water(profile, weekly_kcal)
                
                # Determine if refeed week
                refeed = self._should_refeed(week, goal, experience_level)
                
                macro_targets = MacroTargets(
                    kcal=weekly_kcal,
                    protein_g=protein_g,
                    carbs_g=carbs_g,
                    fat_g=fat_g,
                    fiber_g=fiber_g,
                    sodium_mg=sodium_mg,
                    water_ml=water_ml,
                    refeed=refeed
                )
                
                macro_plan.append(macro_targets)
            
            logger.info("Macro planning completed", 
                       user_id=profile.get("user_id"),
                       weeks_planned=len(macro_plan))
            
            return macro_plan
            
        except Exception as e:
            logger.error("Macro planning failed", 
                        user_id=profile.get("user_id"),
                        error=str(e))
            raise
    
    def _calculate_weekly_kcal(self, base_kcal: int, week: int, total_weeks: int, 
                              goal: str, experience_level: str) -> int:
        """Calculate weekly calorie target with periodization."""
        
        # Base weekly calories
        weekly_kcal = base_kcal
        
        # Apply experience-based adjustments
        if experience_level == "beginner":
            # Beginners get more conservative adjustments
            adjustment_factor = 0.8
        elif experience_level == "intermediate":
            adjustment_factor = 1.0
        else:  # advanced
            adjustment_factor = 1.2
        
        # Apply goal-specific periodization
        if goal in ["lose_weight", "lose_weight_aggressive"]:
            # Progressive deficit for weight loss
            if week <= 4:
                weekly_kcal = int(base_kcal * (1 - 0.1 * adjustment_factor))
            elif week <= 8:
                weekly_kcal = int(base_kcal * (1 - 0.15 * adjustment_factor))
            else:
                weekly_kcal = int(base_kcal * (1 - 0.2 * adjustment_factor))
                
        elif goal == "gain_muscle":
            # Progressive surplus for muscle gain
            if week <= 4:
                weekly_kcal = int(base_kcal * (1 + 0.05 * adjustment_factor))
            elif week <= 8:
                weekly_kcal = int(base_kcal * (1 + 0.1 * adjustment_factor))
            else:
                weekly_kcal = int(base_kcal * (1 + 0.15 * adjustment_factor))
        
        # Apply deload week adjustments (every 4th week)
        if week % 4 == 0 and experience_level != "beginner":
            weekly_kcal = int(weekly_kcal * 0.9)  # 10% reduction for deload
        
        return weekly_kcal
    
    def _calculate_protein(self, kcal: int, base_protein_g: int, goal: str) -> int:
        """Calculate protein target in grams."""
        # Ensure minimum protein based on bodyweight
        min_protein = base_protein_g
        
        # Calculate protein from kcal ratio
        if goal in ["lose_weight", "lose_weight_aggressive"]:
            protein_ratio = 0.35
        elif goal == "gain_muscle":
            protein_ratio = 0.30
        else:
            protein_ratio = 0.30
        
        protein_from_kcal = int((kcal * protein_ratio) / 4)  # 4 kcal per gram
        
        return max(min_protein, protein_from_kcal)
    
    def _calculate_fat(self, kcal: int, goal: str) -> int:
        """Calculate fat target in grams."""
        if goal in ["lose_weight", "lose_weight_aggressive"]:
            fat_ratio = 0.30
        elif goal == "gain_muscle":
            fat_ratio = 0.25
        else:
            fat_ratio = 0.30
        
        return int((kcal * fat_ratio) / 9)  # 9 kcal per gram
    
    def _calculate_carbs(self, kcal: int, protein_g: int, fat_g: int) -> int:
        """Calculate remaining calories as carbs."""
        protein_kcal = protein_g * 4
        fat_kcal = fat_g * 9
        remaining_kcal = kcal - protein_kcal - fat_kcal
        
        return max(0, int(remaining_kcal / 4))  # 4 kcal per gram
    
    def _calculate_fiber(self, profile: Dict[str, Any], carbs_g: int) -> int:
        """Calculate fiber target based on carbs and profile."""
        # Base fiber: 14g per 1000 kcal
        base_fiber = int((profile.get("weight_kg", 70) * 0.5) + 14)
        
        # Additional fiber based on carbs
        fiber_from_carbs = int(carbs_g * 0.1)  # 10% of carbs as fiber
        
        return min(base_fiber + fiber_from_carbs, 50)  # Cap at 50g
    
    def _calculate_sodium(self, profile: Dict[str, Any]) -> int:
        """Calculate sodium target based on profile."""
        base_sodium = 2300  # mg (US RDA)
        
        # Adjust for activity level
        activity_level = profile.get("activity_level", "moderate")
        if activity_level in ["active", "very_active"]:
            base_sodium += 500  # Additional sodium for high activity
        
        return base_sodium
    
    def _calculate_water(self, profile: Dict[str, Any], kcal: int) -> int:
        """Calculate water target based on profile and calories."""
        weight_kg = profile.get("weight_kg", 70)
        activity_level = profile.get("activity_level", "moderate")
        
        # Base water: 30ml per kg bodyweight
        base_water = weight_kg * 30
        
        # Additional water for activity
        activity_water = {
            'sedentary': 0,
            'light': 500,
            'moderate': 1000,
            'active': 1500,
            'very_active': 2000,
        }.get(activity_level, 1000)
        
        # Additional water for calories (1ml per kcal)
        calorie_water = int(kcal * 0.5)
        
        return int(base_water + activity_water + calorie_water)
    
    def _should_refeed(self, week: int, goal: str, experience_level: str) -> bool:
        """Determine if this should be a refeed week."""
        if goal not in ["lose_weight", "lose_weight_aggressive"]:
            return False
        
        if experience_level == "beginner":
            return week % 6 == 0  # Every 6 weeks for beginners
        else:
            return week % 4 == 0  # Every 4 weeks for intermediate/advanced
