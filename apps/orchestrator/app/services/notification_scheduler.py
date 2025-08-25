"""
Notification Scheduler Service
Manages nudges, reminders, and motivational messages based on user behavior and preferences.
"""
import structlog
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import random

logger = structlog.get_logger()

class NotificationType(Enum):
    """Types of notifications."""
    REMINDER = "reminder"
    MOTIVATION = "motivation"
    CELEBRATION = "celebration"
    SUPPORT = "support"
    EDUCATIONAL = "educational"
    CHECK_IN = "check_in"

class NotificationPriority(Enum):
    """Notification priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

@dataclass
class NotificationTemplate:
    """Template for generating notifications."""
    id: str
    type: NotificationType
    title: str
    message: str
    priority: NotificationPriority
    category: str  # "habit", "workout", "nutrition", "mindset", "general"
    triggers: List[str]  # Conditions that trigger this notification
    cooldown_hours: int = 24  # Minimum time between notifications
    max_frequency: int = 3  # Max times per week

@dataclass
class ScheduledNotification:
    """A scheduled notification for a user."""
    id: str
    user_id: str
    template_id: str
    scheduled_for: datetime
    sent_at: Optional[datetime] = None
    delivered: bool = False
    opened: bool = False
    action_taken: bool = False
    created_at: datetime = None

@dataclass
class UserNotificationPreferences:
    """User's notification preferences."""
    user_id: str
    enabled: bool = True
    quiet_hours_start: str = "22:00"
    quiet_hours_end: str = "08:00"
    timezone: str = "UTC"
    frequency_limit: int = 5  # Max notifications per day
    categories_enabled: Dict[str, bool] = None
    created_at: datetime = None

class NotificationScheduler:
    """Service for scheduling and managing user notifications."""
    
    def __init__(self):
        # Notification templates
        self.templates = {
            # Habit-related notifications
            "habit_reminder": NotificationTemplate(
                id="habit_reminder",
                type=NotificationType.REMINDER,
                title="Time for your habit!",
                message="Don't break your streak! Take a moment to {habit_name}.",
                priority=NotificationPriority.MEDIUM,
                category="habit",
                triggers=["habit_due", "streak_at_risk"],
                cooldown_hours=4
            ),
            
            "streak_celebration": NotificationTemplate(
                id="streak_celebration",
                type=NotificationType.CELEBRATION,
                title="Amazing streak! 🎉",
                message="You've maintained {habit_name} for {streak_days} days! Keep up the great work!",
                priority=NotificationPriority.LOW,
                category="habit",
                triggers=["streak_milestone"],
                cooldown_hours=168  # 1 week
            ),
            
            "habit_support": NotificationTemplate(
                id="habit_support",
                type=NotificationType.SUPPORT,
                title="Need a little motivation?",
                message="Remember why you started {habit_name}. You've got this! 💪",
                priority=NotificationPriority.MEDIUM,
                category="habit",
                triggers=["habit_missed", "low_motivation"],
                cooldown_hours=12
            ),
            
            # Workout-related notifications
            "workout_reminder": NotificationTemplate(
                id="workout_reminder",
                type=NotificationType.REMINDER,
                title="Workout time! 💪",
                message="Your {workout_name} is scheduled for today. Ready to crush it?",
                priority=NotificationPriority.HIGH,
                category="workout",
                triggers=["workout_scheduled"],
                cooldown_hours=2
            ),
            
            "workout_motivation": NotificationTemplate(
                id="workout_motivation",
                type=NotificationType.MOTIVATION,
                title="You're stronger than you think!",
                message="Every workout makes you stronger. Today's the day to push your limits!",
                priority=NotificationPriority.MEDIUM,
                category="workout",
                triggers=["workout_missed", "low_energy"],
                cooldown_hours=6
            ),
            
            # Nutrition-related notifications
            "meal_reminder": NotificationTemplate(
                id="meal_reminder",
                type=NotificationType.REMINDER,
                title="Time to fuel up! 🍽️",
                message="Don't forget to log your {meal_type} to stay on track with your nutrition goals.",
                priority=NotificationPriority.MEDIUM,
                category="nutrition",
                triggers=["meal_due"],
                cooldown_hours=3
            ),
            
            "hydration_reminder": NotificationTemplate(
                id="hydration_reminder",
                type=NotificationType.REMINDER,
                title="Stay hydrated! 💧",
                message="Time for a water break! Your body will thank you.",
                priority=NotificationPriority.LOW,
                category="nutrition",
                triggers=["hydration_due"],
                cooldown_hours=2
            ),
            
            # Mindset-related notifications
            "mindset_checkin": NotificationTemplate(
                id="mindset_checkin",
                type=NotificationType.CHECK_IN,
                title="How are you feeling?",
                message="Take a moment to check in with yourself. A quick mindset practice can make a big difference.",
                priority=NotificationPriority.MEDIUM,
                category="mindset",
                triggers=["daily_checkin", "stress_detected"],
                cooldown_hours=8
            ),
            
            "gratitude_reminder": NotificationTemplate(
                id="gratitude_reminder",
                type=NotificationType.REMINDER,
                title="Gratitude moment ✨",
                message="What's one thing you're grateful for today? Take a moment to reflect.",
                priority=NotificationPriority.LOW,
                category="mindset",
                triggers=["evening_routine"],
                cooldown_hours=24
            ),
            
            # General motivational notifications
            "morning_motivation": NotificationTemplate(
                id="morning_motivation",
                type=NotificationType.MOTIVATION,
                title="Good morning! 🌅",
                message="Today is a new opportunity to be better than yesterday. Let's make it count!",
                priority=NotificationPriority.MEDIUM,
                category="general",
                triggers=["morning_routine"],
                cooldown_hours=24
            ),
            
            "weekly_progress": NotificationTemplate(
                id="weekly_progress",
                type=NotificationType.CELEBRATION,
                title="Weekly progress update! 📊",
                message="You've completed {completed_workouts} workouts and maintained {habit_streaks} habits this week. Amazing work!",
                priority=NotificationPriority.LOW,
                category="general",
                triggers=["weekly_summary"],
                cooldown_hours=168  # 1 week
            )
        }
        
        # Motivational messages for different contexts
        self.motivational_messages = {
            "workout": [
                "Your future self is watching you right now through memories.",
                "The only bad workout is the one that didn't happen.",
                "Strength doesn't come from what you can do. It comes from overcoming the things you once thought you couldn't.",
                "Every rep counts. Every set matters. Every workout builds the foundation for your success.",
                "You are stronger than any excuse."
            ],
            "habit": [
                "Small actions compound into massive results.",
                "Consistency beats perfection every time.",
                "The difference between try and triumph is just a little umph!",
                "Your habits shape your future. Choose them wisely.",
                "Every day is a new beginning. Take a deep breath and start again."
            ],
            "nutrition": [
                "Food is fuel. Choose wisely.",
                "Your body hears everything your mind says. Stay positive.",
                "Healthy eating is a form of self-respect.",
                "Progress, not perfection.",
                "You don't have to be perfect, just consistent."
            ],
            "mindset": [
                "Your mind is a powerful thing. When you fill it with positive thoughts, your life will start to change.",
                "The only limits that exist are the ones in your mind.",
                "You are capable of amazing things.",
                "Believe you can and you're halfway there.",
                "Your attitude determines your direction."
            ]
        }
    
    def schedule_notification(self, user_id: str, template_id: str, 
                            scheduled_for: datetime, context: Dict[str, Any] = None) -> ScheduledNotification:
        """
        Schedule a notification for a user.
        
        Args:
            user_id: User ID
            template_id: Template ID to use
            scheduled_for: When to send the notification
            context: Additional context for personalization
            
        Returns:
            ScheduledNotification object
        """
        logger.info("Scheduling notification", 
                   user_id=user_id,
                   template_id=template_id,
                   scheduled_for=scheduled_for)
        
        try:
            template = self.templates.get(template_id)
            if not template:
                raise ValueError(f"Template {template_id} not found")
            
            notification = ScheduledNotification(
                id=f"notif_{user_id}_{template_id}_{datetime.now().timestamp()}",
                user_id=user_id,
                template_id=template_id,
                scheduled_for=scheduled_for,
                created_at=datetime.utcnow()
            )
            
            logger.info("Notification scheduled", 
                       user_id=user_id,
                       notification_id=notification.id)
            
            return notification
            
        except Exception as e:
            logger.error("Failed to schedule notification", 
                        user_id=user_id,
                        template_id=template_id,
                        error=str(e))
            raise
    
    def generate_personalized_message(self, template: NotificationTemplate, 
                                    context: Dict[str, Any]) -> Tuple[str, str]:
        """
        Generate a personalized notification message.
        
        Args:
            template: NotificationTemplate object
            context: Context data for personalization
            
        Returns:
            Tuple of (title, message)
        """
        try:
            title = template.title
            message = template.message
            
            # Replace placeholders with context data
            for key, value in context.items():
                placeholder = f"{{{key}}}"
                if placeholder in message:
                    message = message.replace(placeholder, str(value))
                if placeholder in title:
                    title = title.replace(placeholder, str(value))
            
            # Add motivational message if appropriate
            if template.type == NotificationType.MOTIVATION:
                category = template.category
                if category in self.motivational_messages:
                    motivational = random.choice(self.motivational_messages[category])
                    message += f"\n\n{motivational}"
            
            return title, message
            
        except Exception as e:
            logger.error("Failed to generate personalized message", 
                        template_id=template.id,
                        error=str(e))
            return template.title, template.message
    
    def get_due_notifications(self, user_id: str, current_time: datetime = None) -> List[ScheduledNotification]:
        """
        Get notifications that are due to be sent.
        
        Args:
            user_id: User ID
            current_time: Current time (defaults to now)
            
        Returns:
            List of due notifications
        """
        if current_time is None:
            current_time = datetime.utcnow()
        
        # This would typically query a database
        # For now, return empty list as placeholder
        return []
    
    def should_send_notification(self, user_id: str, template_id: str, 
                               preferences: UserNotificationPreferences,
                               recent_notifications: List[ScheduledNotification]) -> bool:
        """
        Determine if a notification should be sent based on user preferences and recent activity.
        
        Args:
            user_id: User ID
            template_id: Template ID
            preferences: User notification preferences
            recent_notifications: Recent notifications for the user
            
        Returns:
            True if notification should be sent
        """
        try:
            # Check if notifications are enabled
            if not preferences.enabled:
                return False
            
            # Check category preferences
            template = self.templates.get(template_id)
            if not template:
                return False
            
            if preferences.categories_enabled and not preferences.categories_enabled.get(template.category, True):
                return False
            
            # Check quiet hours
            current_time = datetime.utcnow()
            if self._is_in_quiet_hours(current_time, preferences):
                return False
            
            # Check frequency limits
            today_notifications = [
                n for n in recent_notifications 
                if n.created_at.date() == current_time.date()
            ]
            
            if len(today_notifications) >= preferences.frequency_limit:
                return False
            
            # Check template cooldown
            recent_template_notifications = [
                n for n in recent_notifications 
                if n.template_id == template_id and n.created_at > current_time - timedelta(hours=template.cooldown_hours)
            ]
            
            if recent_template_notifications:
                return False
            
            # Check weekly frequency limit
            week_ago = current_time - timedelta(days=7)
            weekly_template_notifications = [
                n for n in recent_notifications 
                if n.template_id == template_id and n.created_at > week_ago
            ]
            
            if len(weekly_template_notifications) >= template.max_frequency:
                return False
            
            return True
            
        except Exception as e:
            logger.error("Failed to check notification send criteria", 
                        user_id=user_id,
                        template_id=template_id,
                        error=str(e))
            return False
    
    def get_notification_recommendations(self, user_id: str, 
                                       user_behavior: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Get notification recommendations based on user behavior.
        
        Args:
            user_id: User ID
            user_behavior: User behavior data
            
        Returns:
            List of notification recommendations
        """
        logger.info("Generating notification recommendations", user_id=user_id)
        
        try:
            recommendations = []
            
            # Analyze user behavior and recommend appropriate notifications
            if user_behavior.get("missed_workouts", 0) > 2:
                recommendations.append({
                    "template_id": "workout_motivation",
                    "reason": "You've missed several workouts recently",
                    "priority": "medium",
                    "suggested_time": "morning"
                })
            
            if user_behavior.get("habit_streak", 0) > 7:
                recommendations.append({
                    "template_id": "streak_celebration",
                    "reason": "You're on a great habit streak!",
                    "priority": "low",
                    "suggested_time": "evening"
                })
            
            if user_behavior.get("stress_level", 0) > 7:
                recommendations.append({
                    "template_id": "mindset_checkin",
                    "reason": "You seem stressed, a mindset check-in might help",
                    "priority": "high",
                    "suggested_time": "afternoon"
                })
            
            if user_behavior.get("hydration_logged", 0) < 3:
                recommendations.append({
                    "template_id": "hydration_reminder",
                    "reason": "You haven't logged much water today",
                    "priority": "low",
                    "suggested_time": "hourly"
                })
            
            return recommendations
            
        except Exception as e:
            logger.error("Failed to generate notification recommendations", 
                        user_id=user_id,
                        error=str(e))
            raise
    
    def _is_in_quiet_hours(self, current_time: datetime, 
                          preferences: UserNotificationPreferences) -> bool:
        """Check if current time is in user's quiet hours."""
        try:
            # Parse quiet hours
            start_hour, start_minute = map(int, preferences.quiet_hours_start.split(':'))
            end_hour, end_minute = map(int, preferences.quiet_hours_end.split(':'))
            
            current_hour = current_time.hour
            current_minute = current_time.minute
            current_time_minutes = current_hour * 60 + current_minute
            start_time_minutes = start_hour * 60 + start_minute
            end_time_minutes = end_hour * 60 + end_minute
            
            # Handle overnight quiet hours
            if start_time_minutes > end_time_minutes:
                return current_time_minutes >= start_time_minutes or current_time_minutes <= end_time_minutes
            else:
                return start_time_minutes <= current_time_minutes <= end_time_minutes
                
        except Exception as e:
            logger.error("Failed to check quiet hours", error=str(e))
            return False
