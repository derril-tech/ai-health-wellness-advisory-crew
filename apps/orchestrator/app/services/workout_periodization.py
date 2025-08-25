"""
Workout Periodization Service
Implements progressive overload with upper/lower and push/pull/legs splits.
"""
import structlog
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import math

logger = structlog.get_logger()

@dataclass
class Exercise:
    """Represents a single exercise."""
    id: str
    name: str
    category: str  # compound, isolation, cardio
    muscle_groups: List[str]
    equipment: List[str]
    difficulty: str  # beginner, intermediate, advanced
    contraindications: List[str]
    progressions: List[str]
    regressions: List[str]
    video_url: Optional[str] = None

@dataclass
class Set:
    """Represents a single set."""
    exercise_id: str
    reps: int
    weight_kg: Optional[float] = None
    rpe: Optional[int] = None  # Rate of Perceived Exertion (1-10)
    rest_seconds: int = 90
    notes: Optional[str] = None

@dataclass
class Workout:
    """Represents a single workout."""
    id: str
    name: str
    day_of_week: int
    week: int
    exercises: List[Set]
    estimated_duration_min: int
    difficulty: str
    notes: Optional[str] = None

@dataclass
class TrainingSplit:
    """Represents a training split configuration."""
    name: str
    days_per_week: int
    workouts: List[Workout]
    progression_schedule: Dict[str, Any]

class WorkoutPeriodization:
    """Workout periodization engine with progressive overload."""
    
    def __init__(self):
        # Training splits
        self.splits = {
            'upper_lower': {
                'name': 'Upper/Lower Split',
                'days_per_week': 4,
                'workouts': ['upper_a', 'lower_a', 'upper_b', 'lower_b'],
            },
            'push_pull_legs': {
                'name': 'Push/Pull/Legs Split',
                'days_per_week': 6,
                'workouts': ['push', 'pull', 'legs', 'push', 'pull', 'legs'],
            },
            'full_body': {
                'name': 'Full Body',
                'days_per_week': 3,
                'workouts': ['full_body_a', 'full_body_b', 'full_body_c'],
            },
        }
        
        # Exercise database (simplified - in production, this would come from a database)
        self.exercise_database = {
            # Upper body compound
            'bench_press': Exercise(
                id='bench_press',
                name='Bench Press',
                category='compound',
                muscle_groups=['chest', 'triceps', 'shoulders'],
                equipment=['barbell', 'bench'],
                difficulty='intermediate',
                contraindications=['shoulder_injury', 'chest_injury'],
                progressions=['incline_bench', 'decline_bench'],
                regressions=['push_ups', 'dumbbell_press'],
            ),
            'overhead_press': Exercise(
                id='overhead_press',
                name='Overhead Press',
                category='compound',
                muscle_groups=['shoulders', 'triceps'],
                equipment=['barbell'],
                difficulty='intermediate',
                contraindications=['shoulder_injury', 'back_injury'],
                progressions=['push_press', 'jerk'],
                regressions=['dumbbell_press', 'pike_push_ups'],
            ),
            'pull_ups': Exercise(
                id='pull_ups',
                name='Pull-ups',
                category='compound',
                muscle_groups=['back', 'biceps'],
                equipment=['pull_up_bar'],
                difficulty='intermediate',
                contraindications=['shoulder_injury', 'elbow_injury'],
                progressions=['weighted_pull_ups', 'muscle_ups'],
                regressions=['assisted_pull_ups', 'lat_pulldown'],
            ),
            'rows': Exercise(
                id='rows',
                name='Barbell Rows',
                category='compound',
                muscle_groups=['back', 'biceps'],
                equipment=['barbell'],
                difficulty='intermediate',
                contraindications=['back_injury'],
                progressions=['pendlay_rows', 't_bar_rows'],
                regressions=['dumbbell_rows', 'cable_rows'],
            ),
            
            # Lower body compound
            'squat': Exercise(
                id='squat',
                name='Barbell Squat',
                category='compound',
                muscle_groups=['quads', 'glutes', 'hamstrings'],
                equipment=['barbell'],
                difficulty='intermediate',
                contraindications=['knee_injury', 'back_injury'],
                progressions=['front_squat', 'paused_squat'],
                regressions=['goblet_squat', 'bodyweight_squat'],
            ),
            'deadlift': Exercise(
                id='deadlift',
                name='Deadlift',
                category='compound',
                muscle_groups=['back', 'hamstrings', 'glutes'],
                equipment=['barbell'],
                difficulty='advanced',
                contraindications=['back_injury', 'hamstring_injury'],
                progressions=['sumo_deadlift', 'romanian_deadlift'],
                regressions=['dumbbell_deadlift', 'good_mornings'],
            ),
            'lunge': Exercise(
                id='lunge',
                name='Walking Lunges',
                category='compound',
                muscle_groups=['quads', 'glutes', 'hamstrings'],
                equipment=['dumbbells'],
                difficulty='beginner',
                contraindications=['knee_injury'],
                progressions=['weighted_lunges', 'reverse_lunges'],
                regressions=['bodyweight_lunges', 'step_ups'],
            ),
            
            # Isolation exercises
            'bicep_curl': Exercise(
                id='bicep_curl',
                name='Dumbbell Bicep Curl',
                category='isolation',
                muscle_groups=['biceps'],
                equipment=['dumbbells'],
                difficulty='beginner',
                contraindications=['elbow_injury'],
                progressions=['barbell_curl', 'hammer_curl'],
                regressions=['resistance_band_curl'],
            ),
            'tricep_extension': Exercise(
                id='tricep_extension',
                name='Tricep Extension',
                category='isolation',
                muscle_groups=['triceps'],
                equipment=['dumbbells'],
                difficulty='beginner',
                contraindications=['elbow_injury'],
                progressions=['skull_crushers', 'diamond_push_ups'],
                regressions=['resistance_band_extension'],
            ),
        }
        
        # Progression schemes
        self.progression_schemes = {
            'linear': {
                'weight_increase': 2.5,  # kg per week
                'rep_increase': 1,  # reps per week
                'deload_frequency': 4,  # weeks
            },
            'wave': {
                'cycles': 3,  # weeks per wave
                'weight_increase': 5,  # kg per wave
                'deload_frequency': 12,  # weeks
            },
            'undulating': {
                'rep_ranges': [5, 8, 12],  # different rep ranges per week
                'weight_adjustment': 0.9,  # weight reduction for higher reps
            },
        }
    
    def generate_program(self, profile: Dict[str, Any], program_weeks: int = 12) -> List[TrainingSplit]:
        """
        Generate a complete training program with periodization.
        
        Args:
            profile: User health profile
            program_weeks: Number of weeks in the program
            
        Returns:
            List of TrainingSplit for each week
        """
        logger.info("Generating training program", 
                   user_id=profile.get("user_id"),
                   program_weeks=program_weeks)
        
        try:
            # Determine training split based on profile
            split_type = self._determine_split_type(profile)
            experience_level = profile.get("experience_level", "beginner")
            goal = profile.get("goal", "improve_fitness")
            
            # Generate weekly splits
            weekly_splits = []
            
            for week in range(1, program_weeks + 1):
                # Determine if this is a deload week
                is_deload = self._should_deload(week, experience_level, goal)
                
                # Generate workouts for this week
                workouts = self._generate_weekly_workouts(
                    split_type=split_type,
                    week=week,
                    profile=profile,
                    is_deload=is_deload
                )
                
                # Create training split
                training_split = TrainingSplit(
                    name=f"Week {week} - {self.splits[split_type]['name']}",
                    days_per_week=self.splits[split_type]['days_per_week'],
                    workouts=workouts,
                    progression_schedule=self._get_progression_schedule(week, experience_level, goal)
                )
                
                weekly_splits.append(training_split)
            
            logger.info("Training program generated", 
                       user_id=profile.get("user_id"),
                       weeks_generated=len(weekly_splits))
            
            return weekly_splits
            
        except Exception as e:
            logger.error("Training program generation failed", 
                        user_id=profile.get("user_id"),
                        error=str(e))
            raise
    
    def _determine_split_type(self, profile: Dict[str, Any]) -> str:
        """Determine the best training split based on profile."""
        experience_level = profile.get("experience_level", "beginner")
        days_available = profile.get("training_days_per_week", 3)
        goal = profile.get("goal", "improve_fitness")
        
        if experience_level == "beginner":
            return "full_body"
        elif days_available >= 6:
            return "push_pull_legs"
        else:
            return "upper_lower"
    
    def _should_deload(self, week: int, experience_level: str, goal: str) -> bool:
        """Determine if this should be a deload week."""
        if experience_level == "beginner":
            return week % 6 == 0  # Every 6 weeks for beginners
        elif goal in ["gain_muscle", "strength"]:
            return week % 4 == 0  # Every 4 weeks for muscle/strength goals
        else:
            return week % 5 == 0  # Every 5 weeks for general fitness
    
    def _generate_weekly_workouts(self, split_type: str, week: int, 
                                profile: Dict[str, Any], is_deload: bool) -> List[Workout]:
        """Generate workouts for a specific week."""
        workouts = []
        
        if split_type == "upper_lower":
            workouts = [
                self._generate_upper_workout(week, profile, is_deload, "A"),
                self._generate_lower_workout(week, profile, is_deload, "A"),
                self._generate_upper_workout(week, profile, is_deload, "B"),
                self._generate_lower_workout(week, profile, is_deload, "B"),
            ]
        elif split_type == "push_pull_legs":
            workouts = [
                self._generate_push_workout(week, profile, is_deload),
                self._generate_pull_workout(week, profile, is_deload),
                self._generate_legs_workout(week, profile, is_deload),
                self._generate_push_workout(week, profile, is_deload, "B"),
                self._generate_pull_workout(week, profile, is_deload, "B"),
                self._generate_legs_workout(week, profile, is_deload, "B"),
            ]
        else:  # full_body
            workouts = [
                self._generate_full_body_workout(week, profile, is_deload, "A"),
                self._generate_full_body_workout(week, profile, is_deload, "B"),
                self._generate_full_body_workout(week, profile, is_deload, "C"),
            ]
        
        return workouts
    
    def _generate_upper_workout(self, week: int, profile: Dict[str, Any], 
                              is_deload: bool, variant: str = "A") -> Workout:
        """Generate an upper body workout."""
        exercises = []
        
        # Compound movements
        exercises.extend([
            Set(exercise_id='bench_press', reps=8 if not is_deload else 12, rest_seconds=120),
            Set(exercise_id='overhead_press', reps=8 if not is_deload else 12, rest_seconds=120),
            Set(exercise_id='pull_ups', reps=6 if not is_deload else 10, rest_seconds=120),
            Set(exercise_id='rows', reps=10 if not is_deload else 15, rest_seconds=90),
        ])
        
        # Isolation movements
        exercises.extend([
            Set(exercise_id='bicep_curl', reps=12 if not is_deload else 15, rest_seconds=60),
            Set(exercise_id='tricep_extension', reps=12 if not is_deload else 15, rest_seconds=60),
        ])
        
        return Workout(
            id=f"upper_{variant}_week_{week}",
            name=f"Upper Body {variant} - Week {week}",
            day_of_week=1 if variant == "A" else 3,
            week=week,
            exercises=exercises,
            estimated_duration_min=60 if not is_deload else 45,
            difficulty="intermediate" if not is_deload else "beginner",
            notes="Focus on form and controlled movements" if is_deload else None
        )
    
    def _generate_lower_workout(self, week: int, profile: Dict[str, Any], 
                              is_deload: bool, variant: str = "A") -> Workout:
        """Generate a lower body workout."""
        exercises = []
        
        # Compound movements
        exercises.extend([
            Set(exercise_id='squat', reps=8 if not is_deload else 12, rest_seconds=120),
            Set(exercise_id='deadlift', reps=6 if not is_deload else 10, rest_seconds=180),
            Set(exercise_id='lunge', reps=12 if not is_deload else 15, rest_seconds=90),
        ])
        
        return Workout(
            id=f"lower_{variant}_week_{week}",
            name=f"Lower Body {variant} - Week {week}",
            day_of_week=2 if variant == "A" else 4,
            week=week,
            exercises=exercises,
            estimated_duration_min=75 if not is_deload else 60,
            difficulty="intermediate" if not is_deload else "beginner",
            notes="Focus on form and controlled movements" if is_deload else None
        )
    
    def _generate_push_workout(self, week: int, profile: Dict[str, Any], 
                             is_deload: bool, variant: str = "A") -> Workout:
        """Generate a push workout (chest, shoulders, triceps)."""
        exercises = []
        
        exercises.extend([
            Set(exercise_id='bench_press', reps=8 if not is_deload else 12, rest_seconds=120),
            Set(exercise_id='overhead_press', reps=8 if not is_deload else 12, rest_seconds=120),
            Set(exercise_id='tricep_extension', reps=12 if not is_deload else 15, rest_seconds=60),
        ])
        
        return Workout(
            id=f"push_{variant}_week_{week}",
            name=f"Push {variant} - Week {week}",
            day_of_week=1 if variant == "A" else 4,
            week=week,
            exercises=exercises,
            estimated_duration_min=45 if not is_deload else 35,
            difficulty="intermediate" if not is_deload else "beginner",
        )
    
    def _generate_pull_workout(self, week: int, profile: Dict[str, Any], 
                             is_deload: bool, variant: str = "A") -> Workout:
        """Generate a pull workout (back, biceps)."""
        exercises = []
        
        exercises.extend([
            Set(exercise_id='pull_ups', reps=6 if not is_deload else 10, rest_seconds=120),
            Set(exercise_id='rows', reps=10 if not is_deload else 15, rest_seconds=90),
            Set(exercise_id='bicep_curl', reps=12 if not is_deload else 15, rest_seconds=60),
        ])
        
        return Workout(
            id=f"pull_{variant}_week_{week}",
            name=f"Pull {variant} - Week {week}",
            day_of_week=2 if variant == "A" else 5,
            week=week,
            exercises=exercises,
            estimated_duration_min=45 if not is_deload else 35,
            difficulty="intermediate" if not is_deload else "beginner",
        )
    
    def _generate_legs_workout(self, week: int, profile: Dict[str, Any], 
                             is_deload: bool, variant: str = "A") -> Workout:
        """Generate a legs workout."""
        exercises = []
        
        exercises.extend([
            Set(exercise_id='squat', reps=8 if not is_deload else 12, rest_seconds=120),
            Set(exercise_id='deadlift', reps=6 if not is_deload else 10, rest_seconds=180),
            Set(exercise_id='lunge', reps=12 if not is_deload else 15, rest_seconds=90),
        ])
        
        return Workout(
            id=f"legs_{variant}_week_{week}",
            name=f"Legs {variant} - Week {week}",
            day_of_week=3 if variant == "A" else 6,
            week=week,
            exercises=exercises,
            estimated_duration_min=60 if not is_deload else 45,
            difficulty="intermediate" if not is_deload else "beginner",
        )
    
    def _generate_full_body_workout(self, week: int, profile: Dict[str, Any], 
                                  is_deload: bool, variant: str = "A") -> Workout:
        """Generate a full body workout."""
        exercises = []
        
        exercises.extend([
            Set(exercise_id='squat', reps=8 if not is_deload else 12, rest_seconds=120),
            Set(exercise_id='bench_press', reps=8 if not is_deload else 12, rest_seconds=120),
            Set(exercise_id='rows', reps=10 if not is_deload else 15, rest_seconds=90),
            Set(exercise_id='overhead_press', reps=8 if not is_deload else 12, rest_seconds=90),
        ])
        
        return Workout(
            id=f"full_body_{variant}_week_{week}",
            name=f"Full Body {variant} - Week {week}",
            day_of_week=1 if variant == "A" else (2 if variant == "B" else 3),
            week=week,
            exercises=exercises,
            estimated_duration_min=60 if not is_deload else 45,
            difficulty="beginner" if not is_deload else "beginner",
        )
    
    def _get_progression_schedule(self, week: int, experience_level: str, goal: str) -> Dict[str, Any]:
        """Get progression schedule for the week."""
        if experience_level == "beginner":
            scheme = "linear"
        elif goal in ["gain_muscle", "strength"]:
            scheme = "wave"
        else:
            scheme = "undulating"
        
        return {
            "scheme": scheme,
            "week": week,
            "weight_increase": self.progression_schemes[scheme].get("weight_increase", 0),
            "rep_increase": self.progression_schemes[scheme].get("rep_increase", 0),
            "is_deload": self._should_deload(week, experience_level, goal),
        }
    
    def suggest_substitutions(self, exercise_id: str, profile: Dict[str, Any], 
                            reason: str = "injury") -> List[Exercise]:
        """Suggest exercise substitutions based on contraindications."""
        original_exercise = self.exercise_database.get(exercise_id)
        if not original_exercise:
            return []
        
        suggestions = []
        
        # Check contraindications
        contraindications = profile.get("injuries", [])
        available_equipment = profile.get("equipment_access", [])
        experience_level = profile.get("experience_level", "beginner")
        
        for exercise in self.exercise_database.values():
            # Skip the original exercise
            if exercise.id == exercise_id:
                continue
            
            # Check if exercise targets similar muscle groups
            if not any(mg in exercise.muscle_groups for mg in original_exercise.muscle_groups):
                continue
            
            # Check contraindications
            if any(contraindication in exercise.contraindications for contraindication in contraindications):
                continue
            
            # Check equipment availability
            if not all(eq in available_equipment for eq in exercise.equipment):
                continue
            
            # Check difficulty level
            if experience_level == "beginner" and exercise.difficulty == "advanced":
                continue
            
            suggestions.append(exercise)
        
        # Sort by relevance (same category, similar difficulty)
        suggestions.sort(key=lambda x: (
            x.category == original_exercise.category,
            x.difficulty == original_exercise.difficulty,
            len(set(x.muscle_groups) & set(original_exercise.muscle_groups))
        ), reverse=True)
        
        return suggestions[:5]  # Return top 5 suggestions
