"""
Habits Engine Service
Manages habit tracking, streak calculations, and behavioral psychology principles.
"""
import structlog
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

logger = structlog.get_logger()

class HabitCategory(Enum):
    """Categories of habits for organization and analysis."""
    NUTRITION = "nutrition"
    EXERCISE = "exercise"
    SLEEP = "sleep"
    MINDSET = "mindset"
    HYDRATION = "hydration"
    RECOVERY = "recovery"
    SOCIAL = "social"
    PRODUCTIVITY = "productivity"

class HabitDifficulty(Enum):
    """Difficulty levels for habit formation."""
    EASY = "easy"      # 1-2 weeks to form
    MEDIUM = "medium"  # 3-4 weeks to form
    HARD = "hard"      # 6-8 weeks to form

@dataclass
class Habit:
    """Represents a single habit."""
    id: str
    name: str
    description: str
    category: HabitCategory
    difficulty: HabitDifficulty
    target_frequency: str  # "daily", "weekly", "monthly"
    target_count: int      # How many times per period
    reminder_time: Optional[str] = None  # "HH:MM" format
    reminder_days: List[int] = None  # [1,2,3,4,5,6,7] for days of week
    streak_goal: int = 21  # Default 21 days for habit formation
    current_streak: int = 0
    longest_streak: int = 0
    total_completions: int = 0
    created_at: datetime = None
    is_active: bool = True

@dataclass
class HabitLog:
    """Represents a single habit completion log."""
    id: str
    habit_id: str
    user_id: str
    completed_at: datetime
    notes: Optional[str] = None
    mood_rating: Optional[int] = None  # 1-10 scale
    difficulty_rating: Optional[int] = None  # 1-10 scale
    context: Optional[Dict[str, Any]] = None  # Additional context data

@dataclass
class HabitInsight:
    """Insights about habit performance."""
    habit_id: str
    current_streak: int
    longest_streak: int
    completion_rate: float
    best_time_of_day: Optional[str] = None
    best_day_of_week: Optional[int] = None
    common_obstacles: List[str] = []
    success_patterns: List[str] = []
    next_milestone: Optional[str] = None

class HabitsEngine:
    """Engine for managing habits and behavioral psychology principles."""
    
    def __init__(self):
        # Behavioral psychology principles
        self.habit_formation_weeks = {
            HabitDifficulty.EASY: 2,
            HabitDifficulty.MEDIUM: 4,
            HabitDifficulty.HARD: 8,
        }
        
        # Streak milestones for motivation
        self.streak_milestones = [3, 7, 14, 21, 30, 60, 90, 180, 365]
        
        # Common habit templates
        self.habit_templates = {
            "water_intake": {
                "name": "Drink Water",
                "description": "Stay hydrated throughout the day",
                "category": HabitCategory.HYDRATION,
                "difficulty": HabitDifficulty.EASY,
                "target_frequency": "daily",
                "target_count": 8,
                "reminder_time": "09:00",
                "reminder_days": [1, 2, 3, 4, 5, 6, 7],
            },
            "morning_exercise": {
                "name": "Morning Exercise",
                "description": "Start the day with physical activity",
                "category": HabitCategory.EXERCISE,
                "difficulty": HabitDifficulty.MEDIUM,
                "target_frequency": "daily",
                "target_count": 1,
                "reminder_time": "06:00",
                "reminder_days": [1, 2, 3, 4, 5, 6, 7],
            },
            "sleep_schedule": {
                "name": "Consistent Sleep Schedule",
                "description": "Go to bed and wake up at the same time",
                "category": HabitCategory.SLEEP,
                "difficulty": HabitDifficulty.HARD,
                "target_frequency": "daily",
                "target_count": 1,
                "reminder_time": "22:00",
                "reminder_days": [1, 2, 3, 4, 5, 6, 7],
            },
            "gratitude_journal": {
                "name": "Gratitude Journal",
                "description": "Write down 3 things you're grateful for",
                "category": HabitCategory.MINDSET,
                "difficulty": HabitDifficulty.EASY,
                "target_frequency": "daily",
                "target_count": 1,
                "reminder_time": "20:00",
                "reminder_days": [1, 2, 3, 4, 5, 6, 7],
            },
            "meal_prep": {
                "name": "Meal Preparation",
                "description": "Prepare healthy meals in advance",
                "category": HabitCategory.NUTRITION,
                "difficulty": HabitDifficulty.MEDIUM,
                "target_frequency": "weekly",
                "target_count": 1,
                "reminder_time": "16:00",
                "reminder_days": [6],  # Saturday
            },
        }
    
    def create_habit(self, user_id: str, habit_data: Dict[str, Any]) -> Habit:
        """
        Create a new habit for a user.
        
        Args:
            user_id: User ID
            habit_data: Habit configuration data
            
        Returns:
            Created Habit object
        """
        logger.info("Creating habit", user_id=user_id, habit_name=habit_data.get("name"))
        
        try:
            habit = Habit(
                id=f"habit_{user_id}_{datetime.now().timestamp()}",
                name=habit_data["name"],
                description=habit_data.get("description", ""),
                category=HabitCategory(habit_data["category"]),
                difficulty=HabitDifficulty(habit_data["difficulty"]),
                target_frequency=habit_data["target_frequency"],
                target_count=habit_data["target_count"],
                reminder_time=habit_data.get("reminder_time"),
                reminder_days=habit_data.get("reminder_days", []),
                streak_goal=self.habit_formation_weeks[HabitDifficulty(habit_data["difficulty"])] * 7,
                created_at=datetime.utcnow(),
            )
            
            logger.info("Habit created successfully", 
                       user_id=user_id,
                       habit_id=habit.id,
                       category=habit.category.value)
            
            return habit
            
        except Exception as e:
            logger.error("Failed to create habit", 
                        user_id=user_id,
                        error=str(e))
            raise
    
    def log_habit_completion(self, user_id: str, habit_id: str, 
                           completion_data: Dict[str, Any]) -> HabitLog:
        """
        Log a habit completion.
        
        Args:
            user_id: User ID
            habit_id: Habit ID
            completion_data: Completion details
            
        Returns:
            Created HabitLog object
        """
        logger.info("Logging habit completion", 
                   user_id=user_id,
                   habit_id=habit_id)
        
        try:
            habit_log = HabitLog(
                id=f"log_{user_id}_{habit_id}_{datetime.now().timestamp()}",
                habit_id=habit_id,
                user_id=user_id,
                completed_at=datetime.utcnow(),
                notes=completion_data.get("notes"),
                mood_rating=completion_data.get("mood_rating"),
                difficulty_rating=completion_data.get("difficulty_rating"),
                context=completion_data.get("context", {}),
            )
            
            logger.info("Habit completion logged", 
                       user_id=user_id,
                       habit_id=habit_id,
                       log_id=habit_log.id)
            
            return habit_log
            
        except Exception as e:
            logger.error("Failed to log habit completion", 
                        user_id=user_id,
                        habit_id=habit_id,
                        error=str(e))
            raise
    
    def calculate_streak(self, habit_logs: List[HabitLog], 
                        habit: Habit) -> Tuple[int, int]:
        """
        Calculate current and longest streaks for a habit.
        
        Args:
            habit_logs: List of habit completion logs
            habit: Habit object
            
        Returns:
            Tuple of (current_streak, longest_streak)
        """
        if not habit_logs:
            return 0, 0
        
        # Sort logs by completion time (newest first)
        sorted_logs = sorted(habit_logs, key=lambda x: x.completed_at, reverse=True)
        
        current_streak = 0
        longest_streak = 0
        temp_streak = 0
        
        # Calculate streaks based on frequency
        if habit.target_frequency == "daily":
            current_date = datetime.now().date()
            
            for log in sorted_logs:
                log_date = log.completed_at.date()
                days_diff = (current_date - log_date).days
                
                if days_diff == temp_streak:
                    temp_streak += 1
                else:
                    if temp_streak > longest_streak:
                        longest_streak = temp_streak
                    if current_streak == 0:
                        current_streak = temp_streak
                    temp_streak = 1
                
                current_date = log_date - timedelta(days=1)
            
            # Check final streak
            if temp_streak > longest_streak:
                longest_streak = temp_streak
            if current_streak == 0:
                current_streak = temp_streak
                
        elif habit.target_frequency == "weekly":
            # Weekly streak calculation
            current_week = datetime.now().isocalendar()[1]
            current_year = datetime.now().year
            
            for log in sorted_logs:
                log_week = log.completed_at.isocalendar()[1]
                log_year = log.completed_at.year
                
                if log_year == current_year and log_week == current_week - temp_streak:
                    temp_streak += 1
                else:
                    if temp_streak > longest_streak:
                        longest_streak = temp_streak
                    if current_streak == 0:
                        current_streak = temp_streak
                    temp_streak = 1
            
            # Check final streak
            if temp_streak > longest_streak:
                longest_streak = temp_streak
            if current_streak == 0:
                current_streak = temp_streak
        
        return current_streak, longest_streak
    
    def calculate_completion_rate(self, habit_logs: List[HabitLog], 
                                habit: Habit, days: int = 30) -> float:
        """
        Calculate completion rate for a habit over a specified period.
        
        Args:
            habit_logs: List of habit completion logs
            habit: Habit object
            days: Number of days to analyze
            
        Returns:
            Completion rate as a percentage
        """
        if not habit_logs:
            return 0.0
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Filter logs within the date range
        relevant_logs = [
            log for log in habit_logs 
            if start_date <= log.completed_at <= end_date
        ]
        
        if habit.target_frequency == "daily":
            expected_completions = days * habit.target_count
        elif habit.target_frequency == "weekly":
            expected_completions = (days // 7) * habit.target_count
        else:
            expected_completions = days * habit.target_count
        
        actual_completions = len(relevant_logs)
        
        if expected_completions == 0:
            return 0.0
        
        return min(100.0, (actual_completions / expected_completions) * 100)
    
    def generate_insights(self, habit: Habit, habit_logs: List[HabitLog]) -> HabitInsight:
        """
        Generate insights about habit performance.
        
        Args:
            habit: Habit object
            habit_logs: List of habit completion logs
            
        Returns:
            HabitInsight object with performance analysis
        """
        logger.info("Generating habit insights", habit_id=habit.id)
        
        try:
            current_streak, longest_streak = self.calculate_streak(habit_logs, habit)
            completion_rate = self.calculate_completion_rate(habit_logs, habit)
            
            # Analyze best time of day
            best_time_of_day = self._analyze_best_time(habit_logs)
            
            # Analyze best day of week
            best_day_of_week = self._analyze_best_day(habit_logs)
            
            # Analyze common obstacles
            common_obstacles = self._analyze_obstacles(habit_logs)
            
            # Analyze success patterns
            success_patterns = self._analyze_success_patterns(habit_logs)
            
            # Determine next milestone
            next_milestone = self._get_next_milestone(current_streak)
            
            insight = HabitInsight(
                habit_id=habit.id,
                current_streak=current_streak,
                longest_streak=longest_streak,
                completion_rate=completion_rate,
                best_time_of_day=best_time_of_day,
                best_day_of_week=best_day_of_week,
                common_obstacles=common_obstacles,
                success_patterns=success_patterns,
                next_milestone=next_milestone,
            )
            
            logger.info("Habit insights generated", 
                       habit_id=habit.id,
                       current_streak=current_streak,
                       completion_rate=completion_rate)
            
            return insight
            
        except Exception as e:
            logger.error("Failed to generate habit insights", 
                        habit_id=habit.id,
                        error=str(e))
            raise
    
    def suggest_habit_improvements(self, habit: Habit, 
                                 insight: HabitInsight) -> List[str]:
        """
        Suggest improvements based on habit performance.
        
        Args:
            habit: Habit object
            insight: HabitInsight object
            
        Returns:
            List of improvement suggestions
        """
        suggestions = []
        
        # Low completion rate suggestions
        if insight.completion_rate < 50:
            suggestions.append("Consider reducing the target frequency to build momentum")
            suggestions.append("Set a specific time reminder to make it part of your routine")
            suggestions.append("Break down the habit into smaller, more manageable steps")
        
        # Streak-based suggestions
        if insight.current_streak < 7:
            suggestions.append("Focus on building a 7-day streak to establish the habit")
        elif insight.current_streak < 21:
            suggestions.append("You're building a strong foundation! Keep going for 21 days")
        elif insight.current_streak < 66:
            suggestions.append("Great progress! You're approaching automatic habit formation")
        
        # Time-based suggestions
        if insight.best_time_of_day:
            suggestions.append(f"Try to complete this habit around {insight.best_time_of_day} when you're most successful")
        
        # Obstacle-based suggestions
        if insight.common_obstacles:
            suggestions.append(f"Plan ahead for: {', '.join(insight.common_obstacles[:2])}")
        
        return suggestions
    
    def get_habit_templates(self, category: Optional[HabitCategory] = None) -> Dict[str, Dict[str, Any]]:
        """
        Get habit templates, optionally filtered by category.
        
        Args:
            category: Optional category filter
            
        Returns:
            Dictionary of habit templates
        """
        if category:
            return {
                k: v for k, v in self.habit_templates.items()
                if v["category"] == category
            }
        return self.habit_templates
    
    def _analyze_best_time(self, habit_logs: List[HabitLog]) -> Optional[str]:
        """Analyze the best time of day for habit completion."""
        if not habit_logs:
            return None
        
        time_counts = {}
        for log in habit_logs:
            hour = log.completed_at.hour
            time_counts[hour] = time_counts.get(hour, 0) + 1
        
        if time_counts:
            best_hour = max(time_counts, key=time_counts.get)
            return f"{best_hour:02d}:00"
        
        return None
    
    def _analyze_best_day(self, habit_logs: List[HabitLog]) -> Optional[int]:
        """Analyze the best day of week for habit completion."""
        if not habit_logs:
            return None
        
        day_counts = {}
        for log in habit_logs:
            day = log.completed_at.isoweekday()
            day_counts[day] = day_counts.get(day, 0) + 1
        
        if day_counts:
            return max(day_counts, key=day_counts.get)
        
        return None
    
    def _analyze_obstacles(self, habit_logs: List[HabitLog]) -> List[str]:
        """Analyze common obstacles based on log context."""
        obstacles = []
        
        # Analyze gaps in completion
        if len(habit_logs) > 1:
            sorted_logs = sorted(habit_logs, key=lambda x: x.completed_at)
            gaps = []
            
            for i in range(1, len(sorted_logs)):
                gap = (sorted_logs[i].completed_at - sorted_logs[i-1].completed_at).days
                if gap > 1:
                    gaps.append(gap)
            
            if gaps:
                avg_gap = sum(gaps) / len(gaps)
                if avg_gap > 3:
                    obstacles.append("Inconsistent scheduling")
                if avg_gap > 7:
                    obstacles.append("Weekly interruptions")
        
        # Analyze difficulty ratings
        difficulty_logs = [log for log in habit_logs if log.difficulty_rating]
        if difficulty_logs:
            avg_difficulty = sum(log.difficulty_rating for log in difficulty_logs) / len(difficulty_logs)
            if avg_difficulty > 7:
                obstacles.append("High perceived difficulty")
        
        return obstacles
    
    def _analyze_success_patterns(self, habit_logs: List[HabitLog]) -> List[str]:
        """Analyze patterns that lead to successful habit completion."""
        patterns = []
        
        # Analyze mood patterns
        mood_logs = [log for log in habit_logs if log.mood_rating]
        if mood_logs:
            high_mood_logs = [log for log in mood_logs if log.mood_rating >= 7]
            if len(high_mood_logs) > len(mood_logs) * 0.6:
                patterns.append("Better completion when mood is positive")
        
        # Analyze time patterns
        morning_logs = [log for log in habit_logs if 6 <= log.completed_at.hour <= 10]
        if len(morning_logs) > len(habit_logs) * 0.5:
            patterns.append("More successful in the morning")
        
        # Analyze consistency patterns
        if len(habit_logs) >= 7:
            recent_logs = sorted(habit_logs, key=lambda x: x.completed_at)[-7:]
            if len(recent_logs) >= 5:
                patterns.append("Strong recent consistency")
        
        return patterns
    
    def _get_next_milestone(self, current_streak: int) -> Optional[str]:
        """Get the next streak milestone."""
        for milestone in self.streak_milestones:
            if current_streak < milestone:
                return f"{milestone} days"
        return None
