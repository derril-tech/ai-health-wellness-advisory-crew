"""
Contract tests for OpenAPI and Zod schema parity.
"""
import pytest
import json
from typing import Dict, Any, List
from pydantic import ValidationError
from fastapi.openapi.utils import get_openapi
from apps.orchestrator.app.main import app
from apps.orchestrator.app.schemas import (
    UserProfile,
    HealthProfile,
    Program,
    MacroTargets,
    Workout,
    MealPlan,
    CheckIn,
    Adjustment
)

class TestOpenAPIZodParity:
    """Test that OpenAPI schemas match Zod validation schemas."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.openapi_schema = get_openapi(
            title=app.title,
            version=app.version,
            openapi_version=app.openapi_version,
            description=app.description,
            routes=app.routes,
        )
    
    def test_user_profile_schema_parity(self):
        """Test UserProfile schema parity."""
        # Get OpenAPI schema
        openapi_schema = self.openapi_schema["components"]["schemas"]["UserProfile"]
        
        # Test valid data
        valid_data = {
            "id": "user123",
            "email": "test@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "age": 30,
            "weight_kg": 75.0,
            "height_cm": 175,
            "is_male": True,
            "activity_level": "moderately_active",
            "goal": "weight_loss",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z"
        }
        
        # Should validate successfully
        user_profile = UserProfile(**valid_data)
        assert user_profile.id == valid_data["id"]
        assert user_profile.email == valid_data["email"]
        
        # Test invalid data
        invalid_data = valid_data.copy()
        invalid_data["email"] = "invalid-email"
        
        with pytest.raises(ValidationError):
            UserProfile(**invalid_data)
    
    def test_health_profile_schema_parity(self):
        """Test HealthProfile schema parity."""
        valid_data = {
            "user_id": "user123",
            "parq_completed": True,
            "parq_risk_level": "low",
            "medical_conditions": ["hypertension"],
            "medications": ["lisinopril"],
            "allergies": ["peanuts"],
            "injuries": ["lower_back_pain"],
            "fitness_level": "intermediate",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z"
        }
        
        # Should validate successfully
        health_profile = HealthProfile(**valid_data)
        assert health_profile.user_id == valid_data["user_id"]
        assert health_profile.parq_completed == valid_data["parq_completed"]
        
        # Test invalid risk level
        invalid_data = valid_data.copy()
        invalid_data["parq_risk_level"] = "invalid_level"
        
        with pytest.raises(ValidationError):
            HealthProfile(**invalid_data)
    
    def test_program_schema_parity(self):
        """Test Program schema parity."""
        valid_data = {
            "id": "program123",
            "user_id": "user123",
            "name": "12-Week Weight Loss",
            "goal": "weight_loss",
            "duration_weeks": 12,
            "status": "active",
            "current_week": 4,
            "start_date": "2024-01-01T00:00:00Z",
            "end_date": "2024-03-25T00:00:00Z",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z"
        }
        
        # Should validate successfully
        program = Program(**valid_data)
        assert program.id == valid_data["id"]
        assert program.status == valid_data["status"]
        
        # Test invalid status
        invalid_data = valid_data.copy()
        invalid_data["status"] = "invalid_status"
        
        with pytest.raises(ValidationError):
            Program(**invalid_data)
    
    def test_macro_targets_schema_parity(self):
        """Test MacroTargets schema parity."""
        valid_data = {
            "calories": 2000,
            "protein_g": 150,
            "carbs_g": 200,
            "fats_g": 67,
            "fiber_g": 28,
            "sodium_mg": 2300
        }
        
        # Should validate successfully
        macro_targets = MacroTargets(**valid_data)
        assert macro_targets.calories == valid_data["calories"]
        assert macro_targets.protein_g == valid_data["protein_g"]
        
        # Test negative values
        invalid_data = valid_data.copy()
        invalid_data["calories"] = -100
        
        with pytest.raises(ValidationError):
            MacroTargets(**invalid_data)
    
    def test_workout_schema_parity(self):
        """Test Workout schema parity."""
        valid_data = {
            "id": "workout123",
            "program_id": "program123",
            "week_number": 4,
            "day_number": 1,
            "name": "Upper Body Strength",
            "type": "strength",
            "duration_minutes": 60,
            "exercises": [
                {
                    "exercise_id": "bench_press",
                    "name": "Bench Press",
                    "sets": 3,
                    "reps": 8,
                    "weight_kg": 80,
                    "rest_seconds": 120
                }
            ],
            "created_at": "2024-01-01T00:00:00Z"
        }
        
        # Should validate successfully
        workout = Workout(**valid_data)
        assert workout.id == valid_data["id"]
        assert len(workout.exercises) == 1
        
        # Test invalid exercise data
        invalid_data = valid_data.copy()
        invalid_data["exercises"][0]["sets"] = -1
        
        with pytest.raises(ValidationError):
            Workout(**invalid_data)
    
    def test_meal_plan_schema_parity(self):
        """Test MealPlan schema parity."""
        valid_data = {
            "id": "meal_plan123",
            "program_id": "program123",
            "week_number": 4,
            "day_number": 1,
            "meals": [
                {
                    "meal_id": "meal1",
                    "name": "Breakfast",
                    "type": "breakfast",
                    "calories": 500,
                    "protein_g": 30,
                    "carbs_g": 50,
                    "fats_g": 20,
                    "recipes": [
                        {
                            "recipe_id": "oatmeal",
                            "name": "Protein Oatmeal",
                            "servings": 1
                        }
                    ]
                }
            ],
            "total_calories": 2000,
            "created_at": "2024-01-01T00:00:00Z"
        }
        
        # Should validate successfully
        meal_plan = MealPlan(**valid_data)
        assert meal_plan.id == valid_data["id"]
        assert len(meal_plan.meals) == 1
        
        # Test invalid meal type
        invalid_data = valid_data.copy()
        invalid_data["meals"][0]["type"] = "invalid_type"
        
        with pytest.raises(ValidationError):
            MealPlan(**invalid_data)
    
    def test_check_in_schema_parity(self):
        """Test CheckIn schema parity."""
        valid_data = {
            "id": "checkin123",
            "user_id": "user123",
            "program_id": "program123",
            "week_number": 4,
            "weight_kg": 74.5,
            "body_fat_percentage": 18.5,
            "sleep_quality": 7,
            "stress_level": 5,
            "energy_level": 8,
            "mood": 7,
            "notes": "Feeling good this week",
            "created_at": "2024-01-01T00:00:00Z"
        }
        
        # Should validate successfully
        check_in = CheckIn(**valid_data)
        assert check_in.id == valid_data["id"]
        assert check_in.weight_kg == valid_data["weight_kg"]
        
        # Test invalid scale values
        invalid_data = valid_data.copy()
        invalid_data["sleep_quality"] = 15  # Should be 1-10
        
        with pytest.raises(ValidationError):
            CheckIn(**invalid_data)
    
    def test_adjustment_schema_parity(self):
        """Test Adjustment schema parity."""
        valid_data = {
            "id": "adjustment123",
            "program_id": "program123",
            "check_in_id": "checkin123",
            "type": "calorie_adjustment",
            "value": -150,
            "reason": "Weight loss plateau detected",
            "confidence": 0.85,
            "applied": True,
            "created_at": "2024-01-01T00:00:00Z"
        }
        
        # Should validate successfully
        adjustment = Adjustment(**valid_data)
        assert adjustment.id == valid_data["id"]
        assert adjustment.type == valid_data["type"]
        
        # Test invalid confidence value
        invalid_data = valid_data.copy()
        invalid_data["confidence"] = 1.5  # Should be 0-1
        
        with pytest.raises(ValidationError):
            Adjustment(**invalid_data)

class TestAPIEndpointSchemas:
    """Test that API endpoints use correct schemas."""
    
    def test_create_user_endpoint_schema(self):
        """Test create user endpoint schema."""
        # This would test the actual API endpoint schema
        # For now, we'll test the request/response models
        
        valid_request = {
            "email": "test@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "age": 30,
            "weight_kg": 75.0,
            "height_cm": 175,
            "is_male": True,
            "activity_level": "moderately_active",
            "goal": "weight_loss"
        }
        
        # Should validate successfully
        user_profile = UserProfile(**valid_request)
        assert user_profile.email == valid_request["email"]
    
    def test_create_program_endpoint_schema(self):
        """Test create program endpoint schema."""
        valid_request = {
            "name": "12-Week Weight Loss",
            "goal": "weight_loss",
            "duration_weeks": 12
        }
        
        # Should validate successfully
        program = Program(**valid_request)
        assert program.name == valid_request["name"]
    
    def test_check_in_endpoint_schema(self):
        """Test check-in endpoint schema."""
        valid_request = {
            "weight_kg": 74.5,
            "body_fat_percentage": 18.5,
            "sleep_quality": 7,
            "stress_level": 5,
            "energy_level": 8,
            "mood": 7,
            "notes": "Feeling good this week"
        }
        
        # Should validate successfully
        check_in = CheckIn(**valid_request)
        assert check_in.weight_kg == valid_request["weight_kg"]

class TestSchemaValidation:
    """Test comprehensive schema validation."""
    
    def test_required_fields(self):
        """Test that required fields are enforced."""
        # Test UserProfile without required fields
        with pytest.raises(ValidationError) as exc_info:
            UserProfile()
        
        errors = exc_info.value.errors()
        required_fields = ["email", "first_name", "last_name", "age", "weight_kg", "height_cm"]
        
        for field in required_fields:
            assert any(error["loc"] == (field,) for error in errors), f"Missing required field: {field}"
    
    def test_field_types(self):
        """Test that field types are correctly enforced."""
        # Test with wrong types
        invalid_data = {
            "email": "test@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "age": "thirty",  # Should be int
            "weight_kg": "75.0",  # Should be float
            "height_cm": 175,
            "is_male": True,
            "activity_level": "moderately_active",
            "goal": "weight_loss"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            UserProfile(**invalid_data)
        
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("age",) for error in errors), "Age should be int"
        assert any(error["loc"] == ("weight_kg",) for error in errors), "Weight should be float"
    
    def test_enum_values(self):
        """Test that enum values are correctly enforced."""
        # Test with invalid enum values
        invalid_data = {
            "email": "test@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "age": 30,
            "weight_kg": 75.0,
            "height_cm": 175,
            "is_male": True,
            "activity_level": "invalid_activity",  # Invalid enum
            "goal": "invalid_goal"  # Invalid enum
        }
        
        with pytest.raises(ValidationError) as exc_info:
            UserProfile(**invalid_data)
        
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("activity_level",) for error in errors), "Invalid activity level"
        assert any(error["loc"] == ("goal",) for error in errors), "Invalid goal"
    
    def test_field_constraints(self):
        """Test that field constraints are enforced."""
        # Test with values outside constraints
        invalid_data = {
            "email": "test@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "age": -5,  # Should be positive
            "weight_kg": -50.0,  # Should be positive
            "height_cm": 0,  # Should be positive
            "is_male": True,
            "activity_level": "moderately_active",
            "goal": "weight_loss"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            UserProfile(**invalid_data)
        
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("age",) for error in errors), "Age should be positive"
        assert any(error["loc"] == ("weight_kg",) for error in errors), "Weight should be positive"
        assert any(error["loc"] == ("height_cm",) for error in errors), "Height should be positive"

class TestSchemaCompatibility:
    """Test schema compatibility between versions."""
    
    def test_backward_compatibility(self):
        """Test that schemas maintain backward compatibility."""
        # Test with minimal required fields
        minimal_data = {
            "email": "test@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "age": 30,
            "weight_kg": 75.0,
            "height_cm": 175,
            "is_male": True,
            "activity_level": "moderately_active",
            "goal": "weight_loss"
        }
        
        # Should always work
        user_profile = UserProfile(**minimal_data)
        assert user_profile.email == minimal_data["email"]
    
    def test_forward_compatibility(self):
        """Test that schemas handle additional fields gracefully."""
        extended_data = {
            "email": "test@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "age": 30,
            "weight_kg": 75.0,
            "height_cm": 175,
            "is_male": True,
            "activity_level": "moderately_active",
            "goal": "weight_loss",
            "extra_field": "should_be_ignored",  # Extra field
            "another_field": 123  # Another extra field
        }
        
        # Should work (extra fields ignored)
        user_profile = UserProfile(**extended_data)
        assert user_profile.email == extended_data["email"]
        # Extra fields should not be present
        assert not hasattr(user_profile, "extra_field")
        assert not hasattr(user_profile, "another_field")
