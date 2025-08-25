"""
Meal Planner Service
Constraint-based meal planning with macro targets, allergens, and preferences.
"""
import structlog
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass
import random

logger = structlog.get_logger()

@dataclass
class Meal:
    """Represents a single meal."""
    name: str
    foods: List[Dict[str, Any]]
    total_kcal: int
    total_protein_g: int
    total_carbs_g: int
    total_fat_g: int
    prep_time_min: int
    difficulty: str
    allergens: List[str]
    tags: List[str]

@dataclass
class MealPlan:
    """Represents a daily meal plan."""
    day_of_week: int
    meals: Dict[str, Meal]  # breakfast, lunch, dinner, snacks
    total_kcal: int
    total_protein_g: int
    total_carbs_g: int
    total_fat_g: int

class MealPlanner:
    """Constraint-based meal planner."""
    
    def __init__(self):
        # Meal type targets (percentage of daily calories)
        self.meal_distributions = {
            'breakfast': 0.25,
            'lunch': 0.30,
            'dinner': 0.30,
            'snacks': 0.15,
        }
        
        # Difficulty levels
        self.difficulty_levels = ['beginner', 'intermediate', 'advanced']
        
        # Sample food database (in production, this would come from a database)
        self.food_database = {
            'chicken_breast': {
                'name': 'Chicken Breast',
                'kcal_per_100g': 165,
                'protein_g_per_100g': 31,
                'carbs_g_per_100g': 0,
                'fat_g_per_100g': 3.6,
                'allergens': [],
                'tags': ['protein', 'lean', 'dinner'],
                'prep_time_min': 20,
                'difficulty': 'beginner',
            },
            'brown_rice': {
                'name': 'Brown Rice',
                'kcal_per_100g': 111,
                'protein_g_per_100g': 2.6,
                'carbs_g_per_100g': 23,
                'fat_g_per_100g': 0.9,
                'allergens': [],
                'tags': ['carbs', 'grain', 'side'],
                'prep_time_min': 45,
                'difficulty': 'beginner',
            },
            'broccoli': {
                'name': 'Broccoli',
                'kcal_per_100g': 34,
                'protein_g_per_100g': 2.8,
                'carbs_g_per_100g': 7,
                'fat_g_per_100g': 0.4,
                'allergens': [],
                'tags': ['vegetable', 'fiber', 'side'],
                'prep_time_min': 10,
                'difficulty': 'beginner',
            },
            'salmon': {
                'name': 'Salmon',
                'kcal_per_100g': 208,
                'protein_g_per_100g': 25,
                'carbs_g_per_100g': 0,
                'fat_g_per_100g': 12,
                'allergens': ['fish'],
                'tags': ['protein', 'omega3', 'dinner'],
                'prep_time_min': 25,
                'difficulty': 'intermediate',
            },
            'quinoa': {
                'name': 'Quinoa',
                'kcal_per_100g': 120,
                'protein_g_per_100g': 4.4,
                'carbs_g_per_100g': 22,
                'fat_g_per_100g': 1.9,
                'allergens': [],
                'tags': ['protein', 'grain', 'gluten_free'],
                'prep_time_min': 20,
                'difficulty': 'beginner',
            },
            'sweet_potato': {
                'name': 'Sweet Potato',
                'kcal_per_100g': 86,
                'protein_g_per_100g': 1.6,
                'carbs_g_per_100g': 20,
                'fat_g_per_100g': 0.1,
                'allergens': [],
                'tags': ['carbs', 'vegetable', 'vitamin_a'],
                'prep_time_min': 45,
                'difficulty': 'beginner',
            },
            'greek_yogurt': {
                'name': 'Greek Yogurt',
                'kcal_per_100g': 59,
                'protein_g_per_100g': 10,
                'carbs_g_per_100g': 3.6,
                'fat_g_per_100g': 0.4,
                'allergens': ['dairy'],
                'tags': ['protein', 'dairy', 'breakfast'],
                'prep_time_min': 0,
                'difficulty': 'beginner',
            },
            'oats': {
                'name': 'Oats',
                'kcal_per_100g': 389,
                'protein_g_per_100g': 17,
                'carbs_g_per_100g': 66,
                'fat_g_per_100g': 7,
                'allergens': ['gluten'],
                'tags': ['carbs', 'fiber', 'breakfast'],
                'prep_time_min': 10,
                'difficulty': 'beginner',
            },
            'almonds': {
                'name': 'Almonds',
                'kcal_per_100g': 579,
                'protein_g_per_100g': 21,
                'carbs_g_per_100g': 22,
                'fat_g_per_100g': 50,
                'allergens': ['nuts'],
                'tags': ['protein', 'healthy_fats', 'snack'],
                'prep_time_min': 0,
                'difficulty': 'beginner',
            },
            'spinach': {
                'name': 'Spinach',
                'kcal_per_100g': 23,
                'protein_g_per_100g': 2.9,
                'carbs_g_per_100g': 3.6,
                'fat_g_per_100g': 0.4,
                'allergens': [],
                'tags': ['vegetable', 'iron', 'salad'],
                'prep_time_min': 5,
                'difficulty': 'beginner',
            },
        }
    
    def plan_meals(self, profile: Dict[str, Any], macro_targets: Dict[str, int], 
                   day_of_week: int = 1) -> MealPlan:
        """
        Plan meals for a single day based on constraints.
        
        Args:
            profile: User health profile
            macro_targets: Daily macro targets
            day_of_week: Day of week (1-7)
            
        Returns:
            MealPlan for the day
        """
        logger.info("Planning meals", 
                   user_id=profile.get("user_id"),
                   day_of_week=day_of_week)
        
        try:
            # Extract constraints
            allergies = profile.get("allergies", [])
            experience_level = profile.get("experience_level", "beginner")
            equipment_access = profile.get("equipment_access", [])
            
            # Calculate meal targets
            daily_kcal = macro_targets.get("kcal", 2000)
            meal_targets = self._calculate_meal_targets(daily_kcal)
            
            # Plan each meal
            meals = {}
            total_kcal = 0
            total_protein = 0
            total_carbs = 0
            total_fat = 0
            
            for meal_type, target_kcal in meal_targets.items():
                meal = self._plan_single_meal(
                    meal_type=meal_type,
                    target_kcal=target_kcal,
                    allergies=allergies,
                    experience_level=experience_level,
                    equipment_access=equipment_access,
                    day_of_week=day_of_week
                )
                
                meals[meal_type] = meal
                total_kcal += meal.total_kcal
                total_protein += meal.total_protein_g
                total_carbs += meal.total_carbs_g
                total_fat += meal.total_fat_g
            
            meal_plan = MealPlan(
                day_of_week=day_of_week,
                meals=meals,
                total_kcal=total_kcal,
                total_protein_g=total_protein,
                total_carbs_g=total_carbs,
                total_fat_g=total_fat
            )
            
            logger.info("Meal planning completed", 
                       user_id=profile.get("user_id"),
                       total_kcal=total_kcal)
            
            return meal_plan
            
        except Exception as e:
            logger.error("Meal planning failed", 
                        user_id=profile.get("user_id"),
                        error=str(e))
            raise
    
    def _calculate_meal_targets(self, daily_kcal: int) -> Dict[str, int]:
        """Calculate calorie targets for each meal type."""
        targets = {}
        for meal_type, percentage in self.meal_distributions.items():
            targets[meal_type] = int(daily_kcal * percentage)
        return targets
    
    def _plan_single_meal(self, meal_type: str, target_kcal: int, 
                         allergies: List[str], experience_level: str,
                         equipment_access: List[str], day_of_week: int) -> Meal:
        """Plan a single meal based on constraints."""
        
        # Filter foods based on constraints
        available_foods = self._filter_foods_by_constraints(
            allergies=allergies,
            experience_level=experience_level,
            equipment_access=equipment_access,
            meal_type=meal_type
        )
        
        # Select foods for the meal
        selected_foods = self._select_foods_for_meal(
            available_foods=available_foods,
            target_kcal=target_kcal,
            meal_type=meal_type
        )
        
        # Calculate totals
        total_kcal = sum(food['kcal'] for food in selected_foods)
        total_protein = sum(food['protein_g'] for food in selected_foods)
        total_carbs = sum(food['carbs_g'] for food in selected_foods)
        total_fat = sum(food['fat_g'] for food in selected_foods)
        
        # Calculate prep time and difficulty
        prep_time = max(food['prep_time_min'] for food in selected_foods)
        difficulty = self._calculate_meal_difficulty(selected_foods)
        
        # Collect allergens and tags
        allergens = list(set(allergen for food in selected_foods for allergen in food['allergens']))
        tags = list(set(tag for food in selected_foods for tag in food['tags']))
        
        # Generate meal name
        meal_name = self._generate_meal_name(selected_foods, meal_type)
        
        return Meal(
            name=meal_name,
            foods=selected_foods,
            total_kcal=total_kcal,
            total_protein_g=total_protein,
            total_carbs_g=total_carbs,
            total_fat_g=total_fat,
            prep_time_min=prep_time,
            difficulty=difficulty,
            allergens=allergens,
            tags=tags
        )
    
    def _filter_foods_by_constraints(self, allergies: List[str], 
                                   experience_level: str, equipment_access: List[str],
                                   meal_type: str) -> List[Dict[str, Any]]:
        """Filter foods based on user constraints."""
        available_foods = []
        
        for food_id, food_data in self.food_database.items():
            # Check allergens
            if any(allergen in food_data['allergens'] for allergen in allergies):
                continue
            
            # Check difficulty level
            if experience_level == "beginner" and food_data['difficulty'] == "advanced":
                continue
            
            # Check equipment requirements (simplified)
            if 'barbell' in food_data.get('tags', []) and 'barbell' not in equipment_access:
                continue
            
            # Check meal type appropriateness
            if meal_type in food_data.get('tags', []):
                available_foods.append({
                    'id': food_id,
                    **food_data
                })
        
        return available_foods
    
    def _select_foods_for_meal(self, available_foods: List[Dict[str, Any]], 
                              target_kcal: int, meal_type: str) -> List[Dict[str, Any]]:
        """Select foods to meet the meal target."""
        selected_foods = []
        remaining_kcal = target_kcal
        
        # Sort foods by priority for this meal type
        if meal_type == "breakfast":
            priority_tags = ['breakfast', 'protein', 'carbs']
        elif meal_type == "lunch":
            priority_tags = ['protein', 'vegetable', 'grain']
        elif meal_type == "dinner":
            priority_tags = ['protein', 'vegetable', 'grain']
        else:  # snacks
            priority_tags = ['snack', 'protein', 'healthy_fats']
        
        # Score foods by priority
        scored_foods = []
        for food in available_foods:
            score = 0
            for tag in priority_tags:
                if tag in food.get('tags', []):
                    score += 1
            scored_foods.append((score, food))
        
        scored_foods.sort(reverse=True)
        
        # Select foods
        for score, food in scored_foods:
            if remaining_kcal <= 0:
                break
            
            # Calculate portion size
            food_kcal_per_100g = food['kcal_per_100g']
            max_portion_g = min(200, int(remaining_kcal / food_kcal_per_100g * 100))
            
            if max_portion_g >= 50:  # Minimum reasonable portion
                portion_g = max_portion_g
                food_kcal = int((portion_g / 100) * food_kcal_per_100g)
                food_protein = int((portion_g / 100) * food['protein_g_per_100g'])
                food_carbs = int((portion_g / 100) * food['carbs_g_per_100g'])
                food_fat = int((portion_g / 100) * food['fat_g_per_100g'])
                
                selected_foods.append({
                    'name': food['name'],
                    'portion_g': portion_g,
                    'kcal': food_kcal,
                    'protein_g': food_protein,
                    'carbs_g': food_carbs,
                    'fat_g': food_fat,
                    'prep_time_min': food['prep_time_min'],
                    'difficulty': food['difficulty'],
                    'allergens': food['allergens'],
                    'tags': food['tags'],
                })
                
                remaining_kcal -= food_kcal
        
        return selected_foods
    
    def _calculate_meal_difficulty(self, foods: List[Dict[str, Any]]) -> str:
        """Calculate overall meal difficulty."""
        difficulties = [food['difficulty'] for food in foods]
        
        if 'advanced' in difficulties:
            return 'advanced'
        elif 'intermediate' in difficulties:
            return 'intermediate'
        else:
            return 'beginner'
    
    def _generate_meal_name(self, foods: List[Dict[str, Any]], meal_type: str) -> str:
        """Generate a descriptive meal name."""
        if not foods:
            return f"{meal_type.title()}"
        
        # Get main protein source
        proteins = [f for f in foods if 'protein' in f.get('tags', [])]
        if proteins:
            main_protein = proteins[0]['name']
        else:
            main_protein = foods[0]['name']
        
        # Get main carb source
        carbs = [f for f in foods if 'carbs' in f.get('tags', []) or 'grain' in f.get('tags', [])]
        if carbs:
            main_carb = carbs[0]['name']
        else:
            main_carb = ""
        
        # Get vegetables
        vegetables = [f['name'] for f in foods if 'vegetable' in f.get('tags', [])]
        
        # Build name
        name_parts = [main_protein]
        if main_carb and main_carb != main_protein:
            name_parts.append(f"with {main_carb}")
        if vegetables:
            name_parts.append(f"& {', '.join(vegetables[:2])}")
        
        return " ".join(name_parts)
    
    def suggest_swaps(self, original_food: Dict[str, Any], target_macros: Dict[str, int],
                     allergies: List[str], available_foods: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Suggest food swaps based on macro targets."""
        suggestions = []
        
        for food in available_foods:
            if food['id'] == original_food['id']:
                continue
            
            # Calculate macro differences
            macro_deltas = {
                'kcal': food['kcal_per_100g'] - original_food['kcal_per_100g'],
                'protein_g': food['protein_g_per_100g'] - original_food['protein_g_per_100g'],
                'carbs_g': food['carbs_g_per_100g'] - original_food['carbs_g_per_100g'],
                'fat_g': food['fat_g_per_100g'] - original_food['fat_g_per_100g'],
            }
            
            # Score the swap based on how well it matches target macros
            score = 0
            for macro, target in target_macros.items():
                if macro in macro_deltas:
                    delta = macro_deltas[macro]
                    if abs(delta) <= abs(target):
                        score += 1
            
            if score > 0:
                suggestions.append({
                    'food': food,
                    'macro_deltas': macro_deltas,
                    'score': score
                })
        
        # Sort by score and return top suggestions
        suggestions.sort(key=lambda x: x['score'], reverse=True)
        return suggestions[:5]
