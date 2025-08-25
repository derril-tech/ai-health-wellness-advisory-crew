"""
Mindset Practice Service
Manages psychological well-being, journaling prompts, and cognitive behavioral techniques.
"""
import structlog
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import random

logger = structlog.get_logger()

class PracticeType(Enum):
    """Types of mindset practices."""
    GRATITUDE = "gratitude"
    MINDFULNESS = "mindfulness"
    REFLECTION = "reflection"
    GOAL_SETTING = "goal_setting"
    SELF_COMPASSION = "self_compassion"
    STRESS_MANAGEMENT = "stress_management"
    CONFIDENCE_BUILDING = "confidence_building"
    RESILIENCE = "resilience"

class MoodState(Enum):
    """Mood states for practice recommendations."""
    EXCELLENT = "excellent"
    GOOD = "good"
    NEUTRAL = "neutral"
    LOW = "low"
    STRESSED = "stressed"
    ANXIOUS = "anxious"
    OVERWHELMED = "overwhelmed"

@dataclass
class MindsetPractice:
    """Represents a mindset practice session."""
    id: str
    type: PracticeType
    title: str
    description: str
    duration_minutes: int
    difficulty: str
    instructions: List[str]
    prompts: List[str]
    benefits: List[str]
    created_at: datetime = None

@dataclass
class PracticeSession:
    """Represents a completed practice session."""
    id: str
    user_id: str
    practice_id: str
    started_at: datetime
    completed_at: datetime
    duration_minutes: int
    mood_before: MoodState
    mood_after: MoodState
    responses: Dict[str, Any]
    notes: Optional[str] = None
    rating: Optional[int] = None

class MindsetPracticeService:
    """Service for managing mindset practices and psychological well-being."""
    
    def __init__(self):
        # Practice database
        self.practices = {
            "gratitude_journal": MindsetPractice(
                id="gratitude_journal",
                type=PracticeType.GRATITUDE,
                title="Gratitude Journal",
                description="Reflect on and write about things you're grateful for",
                duration_minutes=10,
                difficulty="beginner",
                instructions=[
                    "Find a quiet, comfortable space",
                    "Take 3 deep breaths to center yourself",
                    "Write down 3 things you're grateful for today",
                    "Reflect on why each item matters to you",
                    "End with a moment of appreciation"
                ],
                prompts=[
                    "What made you smile today?",
                    "Who are you grateful to have in your life?",
                    "What's something you're looking forward to?",
                    "What's a challenge you've overcome recently?",
                    "What's something beautiful you noticed today?"
                ],
                benefits=[
                    "Increases positive emotions",
                    "Improves sleep quality",
                    "Reduces stress and anxiety",
                    "Strengthens relationships",
                    "Builds resilience"
                ]
            ),
            
            "mindful_breathing": MindsetPractice(
                id="mindful_breathing",
                type=PracticeType.MINDFULNESS,
                title="Mindful Breathing",
                description="Simple breathing exercise to center and calm your mind",
                duration_minutes=5,
                difficulty="beginner",
                instructions=[
                    "Sit comfortably with your back straight",
                    "Close your eyes or soften your gaze",
                    "Place one hand on your belly",
                    "Breathe in slowly through your nose for 4 counts",
                    "Hold for 2 counts",
                    "Exhale slowly through your mouth for 6 counts",
                    "Repeat for 5-10 minutes"
                ],
                prompts=[
                    "Notice the sensation of your breath",
                    "When your mind wanders, gently return to your breath",
                    "Observe without judgment",
                    "Feel the rhythm of your breathing"
                ],
                benefits=[
                    "Reduces stress and anxiety",
                    "Improves focus and concentration",
                    "Lowers blood pressure",
                    "Increases self-awareness",
                    "Promotes emotional regulation"
                ]
            ),
            
            "goal_reflection": MindsetPractice(
                id="goal_reflection",
                type=PracticeType.REFLECTION,
                title="Goal Reflection",
                description="Reflect on your progress and adjust your goals",
                duration_minutes=15,
                difficulty="intermediate",
                instructions=[
                    "Review your current goals",
                    "Assess your progress honestly",
                    "Identify what's working and what isn't",
                    "Consider what adjustments might help",
                    "Set intentions for the coming week"
                ],
                prompts=[
                    "What progress have you made toward your goals?",
                    "What obstacles are you facing?",
                    "What strategies have been most effective?",
                    "What would you like to focus on this week?",
                    "How can you support yourself better?"
                ],
                benefits=[
                    "Increases motivation",
                    "Improves goal clarity",
                    "Enhances self-efficacy",
                    "Promotes adaptive planning",
                    "Builds confidence"
                ]
            )
        }
        
        # Mood-based practice recommendations
        self.mood_recommendations = {
            MoodState.EXCELLENT: ["gratitude_journal", "goal_reflection"],
            MoodState.GOOD: ["mindful_breathing", "goal_reflection"],
            MoodState.NEUTRAL: ["gratitude_journal", "mindful_breathing"],
            MoodState.LOW: ["gratitude_journal", "mindful_breathing"],
            MoodState.STRESSED: ["mindful_breathing"],
            MoodState.ANXIOUS: ["mindful_breathing"],
            MoodState.OVERWHELMED: ["mindful_breathing"]
        }
    
    def get_practice_by_id(self, practice_id: str) -> Optional[MindsetPractice]:
        """Get a practice by its ID."""
        return self.practices.get(practice_id)
    
    def get_practices_by_type(self, practice_type: PracticeType) -> List[MindsetPractice]:
        """Get all practices of a specific type."""
        return [p for p in self.practices.values() if p.type == practice_type]
    
    def recommend_practices(self, user_id: str, mood: MoodState) -> List[Dict[str, Any]]:
        """Recommend practices based on user's current mood."""
        logger.info("Generating practice recommendations", 
                   user_id=user_id,
                   mood=mood.value)
        
        try:
            recommendations = []
            mood_practices = self.mood_recommendations.get(mood, [])
            
            for practice_id in mood_practices:
                practice = self.practices[practice_id]
                recommendations.append({
                    "practice_id": practice.id,
                    "title": practice.title,
                    "description": practice.description,
                    "duration_minutes": practice.duration_minutes,
                    "reason": f"Recommended for {mood.value} mood"
                })
            
            return recommendations
            
        except Exception as e:
            logger.error("Failed to generate practice recommendations", 
                        user_id=user_id,
                        error=str(e))
            raise
    
    def generate_journaling_prompt(self, practice_type: PracticeType = None) -> str:
        """Generate a journaling prompt."""
        prompts = {
            PracticeType.GRATITUDE: [
                "What's something small that brought you joy today?",
                "Who made a positive impact on your life recently?",
                "What's a challenge you're grateful to have overcome?"
            ],
            PracticeType.REFLECTION: [
                "What's been on your mind lately?",
                "What's something you've learned about yourself recently?",
                "What would you like to improve or change?"
            ]
        }
        
        if practice_type and practice_type in prompts:
            return random.choice(prompts[practice_type])
        
        default_prompts = [
            "How are you feeling right now?",
            "What's something you're looking forward to?",
            "What's something you're grateful for?"
        ]
        
        return random.choice(default_prompts)
