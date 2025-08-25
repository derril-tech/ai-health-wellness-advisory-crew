"""
Unit tests for TDEE and macro calculations.
"""
import pytest
from datetime import datetime
from apps.orchestrator.app.services.tdee_macro_engine import (
    TDEEMacroEngine, 
    ActivityLevel, 
    Goal, 
    MacroTargets
)

class TestTDEECalculations:
    """Test TDEE calculation accuracy and edge cases."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.engine = TDEEMacroEngine()
    
    def test_mifflin_st_jeor_male(self):
        """Test Mifflin-St Jeor equation for males."""
        # Test case: 30-year-old male, 180cm, 80kg, moderate activity
        bmr = self.engine._calculate_bmr_mifflin_st_jeor(
            weight_kg=80,
            height_cm=180,
            age=30,
            is_male=True
        )
        
        # Expected BMR: (10 × 80) + (6.25 × 180) - (5 × 30) + 5 = 800 + 1125 - 150 + 5 = 1780
        expected_bmr = 1780
        assert abs(bmr - expected_bmr) < 1, f"BMR calculation error: {bmr} vs {expected_bmr}"
    
    def test_mifflin_st_jeor_female(self):
        """Test Mifflin-St Jeor equation for females."""
        # Test case: 25-year-old female, 165cm, 60kg, moderate activity
        bmr = self.engine._calculate_bmr_mifflin_st_jeor(
            weight_kg=60,
            height_cm=165,
            age=25,
            is_male=False
        )
        
        # Expected BMR: (10 × 60) + (6.25 × 165) - (5 × 25) - 161 = 600 + 1031.25 - 125 - 161 = 1345.25
        expected_bmr = 1345.25
        assert abs(bmr - expected_bmr) < 1, f"BMR calculation error: {bmr} vs {expected_bmr}"
    
    def test_activity_multipliers(self):
        """Test activity level multipliers."""
        bmr = 1500  # Base BMR for testing
        
        multipliers = {
            ActivityLevel.SEDENTARY: 1.2,
            ActivityLevel.LIGHTLY_ACTIVE: 1.375,
            ActivityLevel.MODERATELY_ACTIVE: 1.55,
            ActivityLevel.VERY_ACTIVE: 1.725,
            ActivityLevel.EXTREMELY_ACTIVE: 1.9
        }
        
        for activity_level, expected_multiplier in multipliers.items():
            tdee = self.engine._apply_activity_multiplier(bmr, activity_level)
            expected_tdee = bmr * expected_multiplier
            assert abs(tdee - expected_tdee) < 1, f"Activity multiplier error for {activity_level}"
    
    def test_goal_adjustments(self):
        """Test goal-based calorie adjustments."""
        base_tdee = 2000
        
        # Test weight loss (deficit)
        weight_loss_tdee = self.engine._apply_goal_adjustment(base_tdee, Goal.WEIGHT_LOSS)
        assert weight_loss_tdee < base_tdee, "Weight loss should reduce calories"
        assert weight_loss_tdee >= base_tdee * 0.85, "Deficit should not exceed 15%"
        
        # Test weight gain (surplus)
        weight_gain_tdee = self.engine._apply_goal_adjustment(base_tdee, Goal.WEIGHT_GAIN)
        assert weight_gain_tdee > base_tdee, "Weight gain should increase calories"
        assert weight_gain_tdee <= base_tdee * 1.15, "Surplus should not exceed 15%"
        
        # Test maintenance
        maintenance_tdee = self.engine._apply_goal_adjustment(base_tdee, Goal.MAINTENANCE)
        assert abs(maintenance_tdee - base_tdee) < 50, "Maintenance should be close to base TDEE"
    
    def test_macro_distribution(self):
        """Test macro distribution calculations."""
        calories = 2000
        weight_kg = 70
        
        macros = self.engine._calculate_macro_distribution(calories, weight_kg, Goal.WEIGHT_LOSS)
        
        # Check protein (1.6-2.2 g/kg for weight loss)
        protein_calories = macros.protein_g * 4
        protein_percentage = protein_calories / calories
        assert 0.25 <= protein_percentage <= 0.35, f"Protein percentage {protein_percentage} out of range"
        
        # Check fats (minimum 0.6 g/kg)
        fat_calories = macros.fats_g * 9
        fat_percentage = fat_calories / calories
        assert fat_percentage >= 0.20, f"Fat percentage {fat_percentage} below minimum"
        
        # Check carbs (remainder)
        carb_calories = macros.carbs_g * 4
        carb_percentage = carb_calories / calories
        assert 0.30 <= carb_percentage <= 0.50, f"Carb percentage {carb_percentage} out of range"
        
        # Check total calories
        total_calories = protein_calories + fat_calories + carb_calories
        assert abs(total_calories - calories) < 50, f"Total calories {total_calories} don't match {calories}"
    
    def test_edge_cases(self):
        """Test edge cases and boundary conditions."""
        # Very low weight
        bmr_low = self.engine._calculate_bmr_mifflin_st_jeor(40, 150, 25, True)
        assert bmr_low > 0, "BMR should be positive for low weight"
        
        # Very high weight
        bmr_high = self.engine._calculate_bmr_mifflin_st_jeor(150, 190, 25, True)
        assert bmr_high > 0, "BMR should be positive for high weight"
        
        # Very young age
        bmr_young = self.engine._calculate_bmr_mifflin_st_jeor(60, 170, 18, True)
        assert bmr_young > 0, "BMR should be positive for young age"
        
        # Very old age
        bmr_old = self.engine._calculate_bmr_mifflin_st_jeor(70, 170, 80, True)
        assert bmr_old > 0, "BMR should be positive for old age"
    
    def test_invalid_inputs(self):
        """Test handling of invalid inputs."""
        with pytest.raises(ValueError):
            self.engine._calculate_bmr_mifflin_st_jeor(-50, 170, 25, True)  # Negative weight
        
        with pytest.raises(ValueError):
            self.engine._calculate_bmr_mifflin_st_jeor(70, -170, 25, True)  # Negative height
        
        with pytest.raises(ValueError):
            self.engine._calculate_bmr_mifflin_st_jeor(70, 170, -25, True)  # Negative age
        
        with pytest.raises(ValueError):
            self.engine._calculate_bmr_mifflin_st_jeor(0, 170, 25, True)  # Zero weight
        
        with pytest.raises(ValueError):
            self.engine._calculate_bmr_mifflin_st_jeor(70, 0, 25, True)  # Zero height

class TestMacroCalculations:
    """Test macro calculation accuracy and edge cases."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.engine = TDEEMacroEngine()
    
    def test_protein_calculation_weight_loss(self):
        """Test protein calculation for weight loss goal."""
        weight_kg = 70
        calories = 1800
        
        macros = self.engine._calculate_macro_distribution(calories, weight_kg, Goal.WEIGHT_LOSS)
        
        # Protein should be 1.6-2.2 g/kg for weight loss
        protein_g_per_kg = macros.protein_g / weight_kg
        assert 1.6 <= protein_g_per_kg <= 2.2, f"Protein {protein_g_per_kg} g/kg out of range"
    
    def test_protein_calculation_maintenance(self):
        """Test protein calculation for maintenance goal."""
        weight_kg = 70
        calories = 2000
        
        macros = self.engine._calculate_macro_distribution(calories, weight_kg, Goal.MAINTENANCE)
        
        # Protein should be 1.4-1.8 g/kg for maintenance
        protein_g_per_kg = macros.protein_g / weight_kg
        assert 1.4 <= protein_g_per_kg <= 1.8, f"Protein {protein_g_per_kg} g/kg out of range"
    
    def test_protein_calculation_weight_gain(self):
        """Test protein calculation for weight gain goal."""
        weight_kg = 70
        calories = 2200
        
        macros = self.engine._calculate_macro_distribution(calories, weight_kg, Goal.WEIGHT_GAIN)
        
        # Protein should be 1.6-2.2 g/kg for weight gain
        protein_g_per_kg = macros.protein_g / weight_kg
        assert 1.6 <= protein_g_per_kg <= 2.2, f"Protein {protein_g_per_kg} g/kg out of range"
    
    def test_fat_minimum(self):
        """Test minimum fat requirements."""
        weight_kg = 70
        calories = 1500  # Low calorie diet
        
        macros = self.engine._calculate_macro_distribution(calories, weight_kg, Goal.WEIGHT_LOSS)
        
        # Minimum fat should be 0.6 g/kg
        fat_g_per_kg = macros.fats_g / weight_kg
        assert fat_g_per_kg >= 0.6, f"Fat {fat_g_per_kg} g/kg below minimum"
    
    def test_fiber_calculation(self):
        """Test fiber calculation."""
        calories = 2000
        
        macros = self.engine._calculate_macro_distribution(calories, 70, Goal.MAINTENANCE)
        
        # Fiber should be 14g per 1000 calories
        expected_fiber = (calories / 1000) * 14
        assert abs(macros.fiber_g - expected_fiber) < 1, f"Fiber calculation error: {macros.fiber_g} vs {expected_fiber}"
    
    def test_sodium_calculation(self):
        """Test sodium calculation."""
        calories = 2000
        
        macros = self.engine._calculate_macro_distribution(calories, 70, Goal.MAINTENANCE)
        
        # Sodium should be 2300mg (standard recommendation)
        assert macros.sodium_mg == 2300, f"Sodium should be 2300mg, got {macros.sodium_mg}"

class TestPeriodization:
    """Test macro periodization calculations."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.engine = TDEEMacroEngine()
    
    def test_weekly_periodization(self):
        """Test weekly macro periodization."""
        base_macros = MacroTargets(
            calories=2000,
            protein_g=150,
            carbs_g=200,
            fats_g=67,
            fiber_g=28,
            sodium_mg=2300
        )
        
        weekly_macros = self.engine._generate_weekly_periodization(base_macros, 4)
        
        assert len(weekly_macros) == 4, "Should generate 4 weeks of macros"
        
        for week, macros in weekly_macros.items():
            assert macros.calories > 0, f"Week {week} calories should be positive"
            assert macros.protein_g > 0, f"Week {week} protein should be positive"
            assert macros.carbs_g > 0, f"Week {week} carbs should be positive"
            assert macros.fats_g > 0, f"Week {week} fats should be positive"
    
    def test_deload_week_calculation(self):
        """Test deload week macro adjustments."""
        base_macros = MacroTargets(
            calories=2000,
            protein_g=150,
            carbs_g=200,
            fats_g=67,
            fiber_g=28,
            sodium_mg=2300
        )
        
        deload_macros = self.engine._calculate_deload_macros(base_macros)
        
        # Deload should reduce calories by 10-15%
        assert deload_macros.calories < base_macros.calories
        assert deload_macros.calories >= base_macros.calories * 0.85
        assert deload_macros.calories <= base_macros.calories * 0.90
        
        # Protein should remain high during deload
        protein_percentage = (deload_macros.protein_g * 4) / deload_macros.calories
        assert protein_percentage >= 0.25, "Protein should remain high during deload"
    
    def test_refeed_day_calculation(self):
        """Test refeed day macro adjustments."""
        base_macros = MacroTargets(
            calories=1800,  # Deficit diet
            protein_g=150,
            carbs_g=150,
            fats_g=60,
            fiber_g=25,
            sodium_mg=2300
        )
        
        refeed_macros = self.engine._calculate_refeed_macros(base_macros)
        
        # Refeed should increase calories
        assert refeed_macros.calories > base_macros.calories
        
        # Refeed should increase carbs
        assert refeed_macros.carbs_g > base_macros.carbs_g
        
        # Protein should remain similar
        assert abs(refeed_macros.protein_g - base_macros.protein_g) < 10
        
        # Fats should decrease to accommodate carb increase
        assert refeed_macros.fats_g < base_macros.fats_g

class TestIntegration:
    """Test integration of TDEE and macro calculations."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.engine = TDEEMacroEngine()
    
    def test_complete_calculation_flow(self):
        """Test complete calculation flow from profile to weekly macros."""
        profile = {
            "weight_kg": 75,
            "height_cm": 175,
            "age": 30,
            "is_male": True,
            "activity_level": ActivityLevel.MODERATELY_ACTIVE,
            "goal": Goal.WEIGHT_LOSS
        }
        
        # Calculate TDEE
        tdee = self.engine.calculate_tdee(profile)
        assert tdee > 0, "TDEE should be positive"
        
        # Calculate base macros
        base_macros = self.engine.calculate_macro_targets(profile)
        assert base_macros.calories > 0, "Base macros calories should be positive"
        
        # Generate weekly periodization
        weekly_macros = self.engine.generate_weekly_macro_targets(profile, 4)
        assert len(weekly_macros) == 4, "Should generate 4 weeks of macros"
        
        # Verify consistency
        for week, macros in weekly_macros.items():
            assert macros.calories <= tdee, f"Week {week} calories should not exceed TDEE"
            assert macros.protein_g >= 1.6 * profile["weight_kg"], f"Week {week} protein too low"
    
    def test_real_world_scenarios(self):
        """Test real-world calculation scenarios."""
        scenarios = [
            {
                "name": "Young male weight loss",
                "profile": {
                    "weight_kg": 85,
                    "height_cm": 180,
                    "age": 25,
                    "is_male": True,
                    "activity_level": ActivityLevel.LIGHTLY_ACTIVE,
                    "goal": Goal.WEIGHT_LOSS
                }
            },
            {
                "name": "Middle-aged female maintenance",
                "profile": {
                    "weight_kg": 65,
                    "height_cm": 165,
                    "age": 45,
                    "is_male": False,
                    "activity_level": ActivityLevel.MODERATELY_ACTIVE,
                    "goal": Goal.MAINTENANCE
                }
            },
            {
                "name": "Active male weight gain",
                "profile": {
                    "weight_kg": 70,
                    "height_cm": 175,
                    "age": 20,
                    "is_male": True,
                    "activity_level": ActivityLevel.VERY_ACTIVE,
                    "goal": Goal.WEIGHT_GAIN
                }
            }
        ]
        
        for scenario in scenarios:
            profile = scenario["profile"]
            
            # Calculate TDEE
            tdee = self.engine.calculate_tdee(profile)
            assert tdee > 0, f"TDEE should be positive for {scenario['name']}"
            
            # Calculate macros
            macros = self.engine.calculate_macro_targets(profile)
            assert macros.calories > 0, f"Macros calories should be positive for {scenario['name']}"
            
            # Verify macro ratios
            protein_calories = macros.protein_g * 4
            fat_calories = macros.fats_g * 9
            carb_calories = macros.carbs_g * 4
            
            total_calories = protein_calories + fat_calories + carb_calories
            assert abs(total_calories - macros.calories) < 50, f"Calorie mismatch for {scenario['name']}"
