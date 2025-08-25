"""
Schedule Optimizer Service
Optimizes workout and meal timing based on user preferences, device data, and scheduling constraints.
"""
import structlog
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta, time
from dataclasses import dataclass
from enum import Enum
import math

logger = structlog.get_logger()

class ActivityType(Enum):
    """Types of activities that can be scheduled."""
    WORKOUT = "workout"
    MEAL = "meal"
    HABIT = "habit"
    MINDSET = "mindset"
    SLEEP = "sleep"

class TimeSlot(Enum):
    """Time slots for scheduling."""
    EARLY_MORNING = "early_morning"  # 5-8 AM
    MORNING = "morning"              # 8-12 PM
    AFTERNOON = "afternoon"          # 12-5 PM
    EVENING = "evening"              # 5-9 PM
    NIGHT = "night"                  # 9 PM-5 AM

@dataclass
class ScheduleConstraint:
    """Represents a scheduling constraint."""
    id: str
    user_id: str
    activity_type: ActivityType
    preferred_time_slots: List[TimeSlot]
    preferred_days: List[int]  # 1=Monday, 7=Sunday
    duration_minutes: int
    frequency_per_week: int
    priority: int  # 1-5, higher = more important
    must_have_spacing_hours: int = 0  # Minimum hours between activities
    flexible_timing: bool = True
    created_at: datetime = None

@dataclass
class ScheduledActivity:
    """Represents a scheduled activity."""
    id: str
    user_id: str
    activity_type: ActivityType
    title: str
    description: str
    scheduled_date: datetime
    start_time: time
    end_time: time
    duration_minutes: int
    constraint_id: str
    priority: int
    metadata: Dict[str, Any] = None

@dataclass
class ScheduleOptimization:
    """Result of schedule optimization."""
    user_id: str
    week_start: datetime
    scheduled_activities: List[ScheduledActivity]
    conflicts: List[Dict[str, Any]]
    recommendations: List[str]
    adherence_score: float  # 0-1, how well the schedule fits constraints
    created_at: datetime = None

@dataclass
class UserPreferences:
    """User scheduling preferences."""
    user_id: str
    wake_up_time: time
    bed_time: time
    work_start_time: time
    work_end_time: time
    preferred_workout_time: TimeSlot
    preferred_meal_times: Dict[str, time]  # breakfast, lunch, dinner
    rest_days: List[int]  # Days of week to avoid workouts
    timezone: str = "UTC"
    created_at: datetime = None

class ScheduleOptimizer:
    """Service for optimizing user schedules based on preferences and constraints."""
    
    def __init__(self):
        self.logger = structlog.get_logger()
        self.time_slot_ranges = {
            TimeSlot.EARLY_MORNING: (time(5, 0), time(8, 0)),
            TimeSlot.MORNING: (time(8, 0), time(12, 0)),
            TimeSlot.AFTERNOON: (time(12, 0), time(17, 0)),
            TimeSlot.EVENING: (time(17, 0), time(21, 0)),
            TimeSlot.NIGHT: (time(21, 0), time(5, 0))
        }
    
    def optimize_schedule(self, user_id: str, week_start: datetime, 
                         constraints: List[ScheduleConstraint],
                         preferences: UserPreferences,
                         existing_activities: List[ScheduledActivity] = None) -> ScheduleOptimization:
        """Optimize schedule for a given week."""
        self.logger.info("Starting schedule optimization", user_id=user_id, week_start=week_start)
        
        if existing_activities is None:
            existing_activities = []
        
        # Sort constraints by priority (highest first)
        sorted_constraints = sorted(constraints, key=lambda x: x.priority, reverse=True)
        
        scheduled_activities = []
        conflicts = []
        
        # Generate all possible time slots for the week
        available_slots = self._generate_available_slots(week_start, preferences, existing_activities)
        
        # Schedule activities based on priority
        for constraint in sorted_constraints:
            activities_scheduled = 0
            required_activities = constraint.frequency_per_week
            
            while activities_scheduled < required_activities:
                best_slot = self._find_best_slot(constraint, available_slots, preferences)
                
                if best_slot:
                    # Create scheduled activity
                    activity = self._create_scheduled_activity(constraint, best_slot)
                    scheduled_activities.append(activity)
                    
                    # Update available slots
                    self._update_available_slots(available_slots, best_slot, constraint.duration_minutes)
                    
                    activities_scheduled += 1
                else:
                    # No suitable slot found
                    conflicts.append({
                        'constraint_id': constraint.id,
                        'activity_type': constraint.activity_type.value,
                        'reason': 'No suitable time slot available',
                        'priority': constraint.priority
                    })
                    break
        
        # Calculate adherence score
        adherence_score = self._calculate_adherence_score(scheduled_activities, constraints, preferences)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(scheduled_activities, constraints, conflicts, preferences)
        
        optimization = ScheduleOptimization(
            user_id=user_id,
            week_start=week_start,
            scheduled_activities=scheduled_activities,
            conflicts=conflicts,
            recommendations=recommendations,
            adherence_score=adherence_score,
            created_at=datetime.utcnow()
        )
        
        self.logger.info("Schedule optimization completed", 
                        user_id=user_id, 
                        activities_scheduled=len(scheduled_activities),
                        conflicts=len(conflicts),
                        adherence_score=adherence_score)
        
        return optimization
    
    def _generate_available_slots(self, week_start: datetime, preferences: UserPreferences, 
                                 existing_activities: List[ScheduledActivity]) -> List[Dict[str, Any]]:
        """Generate available time slots for the week."""
        slots = []
        
        for day_offset in range(7):
            current_date = week_start + timedelta(days=day_offset)
            day_of_week = current_date.isoweekday()
            
            # Skip rest days for workouts
            if day_of_week in preferences.rest_days:
                continue
            
            # Generate slots for each time period
            for slot_type, (start_time, end_time) in self.time_slot_ranges.items():
                # Check if this slot conflicts with existing activities
                if not self._has_conflict(current_date, start_time, end_time, existing_activities):
                    slots.append({
                        'date': current_date,
                        'day_of_week': day_of_week,
                        'time_slot': slot_type,
                        'start_time': start_time,
                        'end_time': end_time,
                        'available_duration': self._calculate_available_duration(start_time, end_time, preferences),
                        'score': self._calculate_slot_score(slot_type, day_of_week, preferences)
                    })
        
        return slots
    
    def _find_best_slot(self, constraint: ScheduleConstraint, available_slots: List[Dict[str, Any]], 
                       preferences: UserPreferences) -> Optional[Dict[str, Any]]:
        """Find the best available slot for a constraint."""
        suitable_slots = []
        
        for slot in available_slots:
            # Check if slot meets constraint requirements
            if (slot['time_slot'] in constraint.preferred_time_slots and
                slot['day_of_week'] in constraint.preferred_days and
                slot['available_duration'] >= constraint.duration_minutes):
                
                # Check spacing requirements
                if self._meets_spacing_requirements(slot, constraint, available_slots):
                    suitable_slots.append(slot)
        
        if not suitable_slots:
            return None
        
        # Sort by score and return the best one
        suitable_slots.sort(key=lambda x: x['score'], reverse=True)
        return suitable_slots[0]
    
    def _create_scheduled_activity(self, constraint: ScheduleConstraint, slot: Dict[str, Any]) -> ScheduledActivity:
        """Create a scheduled activity from a constraint and slot."""
        start_time = slot['start_time']
        end_time = self._calculate_end_time(start_time, constraint.duration_minutes)
        
        # Generate title based on activity type
        title = self._generate_activity_title(constraint.activity_type)
        
        return ScheduledActivity(
            id=f"activity_{constraint.id}_{slot['date'].strftime('%Y%m%d')}",
            user_id=constraint.user_id,
            activity_type=constraint.activity_type,
            title=title,
            description=f"Scheduled {constraint.activity_type.value}",
            scheduled_date=slot['date'],
            start_time=start_time,
            end_time=end_time,
            duration_minutes=constraint.duration_minutes,
            constraint_id=constraint.id,
            priority=constraint.priority,
            metadata={
                'time_slot': slot['time_slot'].value,
                'day_of_week': slot['day_of_week']
            }
        )
    
    def _update_available_slots(self, available_slots: List[Dict[str, Any]], 
                              used_slot: Dict[str, Any], duration_minutes: int):
        """Update available slots after scheduling an activity."""
        used_date = used_slot['date']
        used_start = used_slot['start_time']
        used_end = self._calculate_end_time(used_start, duration_minutes)
        
        # Remove or update conflicting slots
        slots_to_remove = []
        for slot in available_slots:
            if (slot['date'] == used_date and
                self._times_overlap(used_start, used_end, slot['start_time'], slot['end_time'])):
                slots_to_remove.append(slot)
        
        for slot in slots_to_remove:
            available_slots.remove(slot)
    
    def _calculate_adherence_score(self, scheduled_activities: List[ScheduledActivity], 
                                 constraints: List[ScheduleConstraint],
                                 preferences: UserPreferences) -> float:
        """Calculate how well the schedule adheres to constraints and preferences."""
        if not constraints:
            return 1.0
        
        total_score = 0
        max_score = len(constraints)
        
        for constraint in constraints:
            constraint_activities = [a for a in scheduled_activities if a.constraint_id == constraint.id]
            
            if len(constraint_activities) >= constraint.frequency_per_week:
                # Full adherence
                score = 1.0
            elif len(constraint_activities) > 0:
                # Partial adherence
                score = len(constraint_activities) / constraint.frequency_per_week
            else:
                # No adherence
                score = 0.0
            
            # Bonus for preferred timing
            timing_bonus = 0
            for activity in constraint_activities:
                if activity.metadata.get('time_slot') in [ts.value for ts in constraint.preferred_time_slots]:
                    timing_bonus += 0.1
            
            score = min(1.0, score + timing_bonus)
            total_score += score
        
        return total_score / max_score if max_score > 0 else 0.0
    
    def _generate_recommendations(self, scheduled_activities: List[ScheduledActivity], 
                                constraints: List[ScheduleConstraint],
                                conflicts: List[Dict[str, Any]],
                                preferences: UserPreferences) -> List[str]:
        """Generate recommendations for improving the schedule."""
        recommendations = []
        
        # Check for conflicts
        if conflicts:
            high_priority_conflicts = [c for c in conflicts if c['priority'] >= 4]
            if high_priority_conflicts:
                recommendations.append(
                    "High-priority activities couldn't be scheduled. Consider adjusting your availability or reducing activity frequency."
                )
        
        # Check for rest day distribution
        workout_days = set()
        for activity in scheduled_activities:
            if activity.activity_type == ActivityType.WORKOUT:
                workout_days.add(activity.scheduled_date.isoweekday())
        
        if len(workout_days) < 3:
            recommendations.append(
                "Consider spreading workouts across more days for better recovery and consistency."
            )
        
        # Check for timing preferences
        morning_workouts = [a for a in scheduled_activities 
                          if a.activity_type == ActivityType.WORKOUT and 
                          a.start_time < time(12, 0)]
        
        if preferences.preferred_workout_time == TimeSlot.MORNING and len(morning_workouts) < 2:
            recommendations.append(
                "Try to schedule more workouts in the morning to match your preferences."
            )
        
        # Check for meal spacing
        meal_activities = [a for a in scheduled_activities if a.activity_type == ActivityType.MEAL]
        if len(meal_activities) < 3:
            recommendations.append(
                "Ensure you have time for regular meals throughout the day."
            )
        
        return recommendations
    
    def _has_conflict(self, date: datetime, start_time: time, end_time: time, 
                     existing_activities: List[ScheduledActivity]) -> bool:
        """Check if a time slot conflicts with existing activities."""
        for activity in existing_activities:
            if (activity.scheduled_date.date() == date.date() and
                self._times_overlap(start_time, end_time, activity.start_time, activity.end_time)):
                return True
        return False
    
    def _times_overlap(self, start1: time, end1: time, start2: time, end2: time) -> bool:
        """Check if two time ranges overlap."""
        return start1 < end2 and start2 < end1
    
    def _calculate_available_duration(self, start_time: time, end_time: time, 
                                    preferences: UserPreferences) -> int:
        """Calculate available duration in a time slot."""
        start_minutes = start_time.hour * 60 + start_time.minute
        end_minutes = end_time.hour * 60 + end_time.minute
        
        # Handle overnight slots
        if end_minutes < start_minutes:
            end_minutes += 24 * 60
        
        return end_minutes - start_minutes
    
    def _calculate_slot_score(self, time_slot: TimeSlot, day_of_week: int, 
                            preferences: UserPreferences) -> float:
        """Calculate a score for a time slot based on preferences."""
        score = 0.5  # Base score
        
        # Prefer morning workouts
        if time_slot == preferences.preferred_workout_time:
            score += 0.3
        
        # Prefer weekdays for workouts
        if day_of_week <= 5:  # Monday-Friday
            score += 0.2
        
        # Avoid very early morning unless specifically preferred
        if time_slot == TimeSlot.EARLY_MORNING and preferences.preferred_workout_time != TimeSlot.EARLY_MORNING:
            score -= 0.1
        
        return max(0.0, min(1.0, score))
    
    def _meets_spacing_requirements(self, slot: Dict[str, Any], constraint: ScheduleConstraint, 
                                  available_slots: List[Dict[str, Any]]) -> bool:
        """Check if a slot meets spacing requirements from other activities."""
        if constraint.must_have_spacing_hours == 0:
            return True
        
        slot_datetime = datetime.combine(slot['date'], slot['start_time'])
        
        # Check spacing from other scheduled activities
        for other_slot in available_slots:
            if other_slot != slot:
                other_datetime = datetime.combine(other_slot['date'], other_slot['start_time'])
                time_diff = abs((slot_datetime - other_datetime).total_seconds() / 3600)
                
                if time_diff < constraint.must_have_spacing_hours:
                    return False
        
        return True
    
    def _calculate_end_time(self, start_time: time, duration_minutes: int) -> time:
        """Calculate end time given start time and duration."""
        start_minutes = start_time.hour * 60 + start_time.minute
        end_minutes = start_minutes + duration_minutes
        
        hours = end_minutes // 60
        minutes = end_minutes % 60
        
        return time(hours, minutes)
    
    def _generate_activity_title(self, activity_type: ActivityType) -> str:
        """Generate a title for an activity based on its type."""
        titles = {
            ActivityType.WORKOUT: "Workout Session",
            ActivityType.MEAL: "Meal Time",
            ActivityType.HABIT: "Habit Check-in",
            ActivityType.MINDSET: "Mindset Practice",
            ActivityType.SLEEP: "Sleep Preparation"
        }
        return titles.get(activity_type, "Scheduled Activity")
    
    def suggest_schedule_adjustments(self, optimization: ScheduleOptimization, 
                                   user_feedback: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Suggest adjustments based on user feedback and optimization results."""
        suggestions = []
        
        # Analyze conflicts and suggest alternatives
        for conflict in optimization.conflicts:
            if conflict['priority'] >= 4:  # High priority conflicts
                suggestions.append({
                    'type': 'reschedule',
                    'constraint_id': conflict['constraint_id'],
                    'suggestion': 'Consider moving this activity to a different day or time',
                    'priority': 'high'
                })
        
        # Suggest based on adherence score
        if optimization.adherence_score < 0.7:
            suggestions.append({
                'type': 'frequency_adjustment',
                'suggestion': 'Consider reducing the frequency of some activities to improve schedule adherence',
                'priority': 'medium'
            })
        
        # Suggest based on user feedback
        if user_feedback.get('too_many_morning_activities'):
            suggestions.append({
                'type': 'timing_adjustment',
                'suggestion': 'Try spreading activities throughout the day instead of clustering them in the morning',
                'priority': 'medium'
            })
        
        if user_feedback.get('need_more_rest_days'):
            suggestions.append({
                'type': 'rest_day_adjustment',
                'suggestion': 'Consider adding more rest days or reducing workout frequency',
                'priority': 'medium'
            })
        
        return suggestions
    
    def get_optimal_workout_timing(self, user_id: str, device_data: List[Dict[str, Any]], 
                                 preferences: UserPreferences) -> Dict[str, Any]:
        """Determine optimal workout timing based on device data and preferences."""
        # Analyze device data for patterns
        energy_patterns = self._analyze_energy_patterns(device_data)
        sleep_patterns = self._analyze_sleep_patterns(device_data)
        
        # Find time slots with highest energy and best sleep recovery
        optimal_slots = []
        
        for time_slot in TimeSlot:
            if time_slot == TimeSlot.NIGHT:  # Skip night time
                continue
            
            energy_score = energy_patterns.get(time_slot.value, 0.5)
            sleep_score = sleep_patterns.get(time_slot.value, 0.5)
            
            # Weight energy more heavily than sleep for workout timing
            combined_score = (energy_score * 0.7) + (sleep_score * 0.3)
            
            optimal_slots.append({
                'time_slot': time_slot.value,
                'score': combined_score,
                'energy_score': energy_score,
                'sleep_score': sleep_score
            })
        
        # Sort by score
        optimal_slots.sort(key=lambda x: x['score'], reverse=True)
        
        return {
            'user_id': user_id,
            'optimal_slots': optimal_slots,
            'recommendation': optimal_slots[0]['time_slot'] if optimal_slots else 'morning',
            'reasoning': f"Based on your energy patterns and sleep data, {optimal_slots[0]['time_slot']} appears to be your optimal workout time."
        }
    
    def _analyze_energy_patterns(self, device_data: List[Dict[str, Any]]) -> Dict[str, float]:
        """Analyze energy patterns from device data."""
        # This would analyze heart rate, activity levels, etc.
        # For now, return default patterns
        return {
            'early_morning': 0.6,
            'morning': 0.8,
            'afternoon': 0.7,
            'evening': 0.5,
            'night': 0.3
        }
    
    def _analyze_sleep_patterns(self, device_data: List[Dict[str, Any]]) -> Dict[str, float]:
        """Analyze sleep patterns from device data."""
        # This would analyze sleep quality, recovery, etc.
        # For now, return default patterns
        return {
            'early_morning': 0.7,
            'morning': 0.9,
            'afternoon': 0.6,
            'evening': 0.4,
            'night': 0.2
        }
