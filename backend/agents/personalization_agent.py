"""Personalization Agent - Adapts learning paths using analytics."""

from typing import Dict, List, Any
import random

class PersonalizationAgent:
    """Agent for personalizing learning experiences based on student data."""

    def __init__(self):
        self.student_profiles = {}  # In real implementation, this would be from BigQuery/Firebase
        self.learning_patterns = {}

    def analyze_student_profile(self, student_id: str, past_performance: List[Dict] = None) -> Dict[str, Any]:
        """Analyze student's learning profile and preferences."""

        # Mock student data - in real implementation would fetch from BigQuery
        if student_id not in self.student_profiles:
            self.student_profiles[student_id] = self._create_mock_profile(student_id)

        profile = self.student_profiles[student_id]

        # Update profile with recent performance if provided
        if past_performance:
            profile = self._update_profile_with_performance(profile, past_performance)

        return profile

    def _create_mock_profile(self, student_id: str) -> Dict[str, Any]:
        """Create a mock student profile for demo."""
        learning_styles = ["visual", "auditory", "kinesthetic", "reading_writing"]
        pace_preferences = ["fast", "moderate", "slow"]
        challenge_levels = ["beginner", "intermediate", "advanced"]

        return {
            "student_id": student_id,
            "learning_style": random.choice(learning_styles),
            "pace_preference": random.choice(pace_preferences),
            "preferred_challenge": random.choice(challenge_levels),
            "weak_topics": random.sample([
                "calculus", "linear algebra", "probability", "statistics",
                "algorithms", "data structures", "machine learning", "deep learning"
            ], 3),
            "strength_topics": random.sample([
                "programming", "mathematics", "analysis", "problem_solving"
            ], 2),
            "study_habits": {
                "preferred_time": random.choice(["morning", "afternoon", "evening", "night"]),
                "session_duration": random.randint(30, 120),  # minutes
                "break_frequency": random.randint(45, 90)  # minutes
            },
            "emotional_factors": {
                "motivation_level": random.uniform(0.3, 0.9),
                "confidence_level": random.uniform(0.4, 0.8),
                "stress_tolerance": random.uniform(0.2, 0.8)
            },
            "performance_history": {
                "average_score": random.uniform(60, 95),
                "improvement_rate": random.uniform(-5, 15),  # points per assessment
                "consistency_score": random.uniform(0.3, 0.9)
            }
        }

    def _update_profile_with_performance(self, profile: Dict, past_performance: List[Dict]) -> Dict[str, Any]:
        """Update student profile based on recent performance."""
        if not past_performance:
            return profile

        # Calculate recent trends
        recent_scores = [p.get("score", 70) for p in past_performance[-5:]]  # Last 5 assessments

        if recent_scores:
            avg_recent = sum(recent_scores) / len(recent_scores)

            # Update confidence based on recent performance
            if avg_recent > 85:
                profile["emotional_factors"]["confidence_level"] = min(0.9, profile["emotional_factors"]["confidence_level"] + 0.1)
            elif avg_recent < 70:
                profile["emotional_factors"]["confidence_level"] = max(0.3, profile["emotional_factors"]["confidence_level"] - 0.1)

            # Update preferred challenge level
            if avg_recent > 90 and profile["preferred_challenge"] != "advanced":
                profile["preferred_challenge"] = "intermediate" if profile["preferred_challenge"] == "beginner" else "advanced"
            elif avg_recent < 60 and profile["preferred_challenge"] != "beginner":
                profile["preferred_challenge"] = "intermediate" if profile["preferred_challenge"] == "advanced" else "beginner"

        return profile

    def recommend_personalized_path(self, topic: str, learning_resources: Dict[str, Any],
                                  wellness_assessment: Dict[str, Any], student_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Recommend a personalized learning path."""

        # Extract key information
        resources = learning_resources.get("resources", [])
        difficulty = learning_resources.get("difficulty", "intermediate")
        fatigue_level = wellness_assessment.get("fatigue_level", 0.3)
        stress_level = wellness_assessment.get("stress_level", 0.2)

        # Adjust difficulty based on student profile and wellness
        adjusted_difficulty = self._adjust_difficulty(difficulty, student_profile, wellness_assessment)

        # Personalize resource selection
        personalized_resources = self._personalize_resources(resources, student_profile)

        # Create adaptive study plan
        study_plan = self._create_adaptive_plan(topic, adjusted_difficulty, personalized_resources,
                                              student_profile, wellness_assessment)

        return {
            "student_profile": student_profile,
            "adjusted_difficulty": adjusted_difficulty,
            "personalized_resources": personalized_resources,
            "adaptive_study_plan": study_plan,
            "reasoning": self._explain_personalization(student_profile, wellness_assessment)
        }

    def _adjust_difficulty(self, base_difficulty: str, profile: Dict, wellness: Dict) -> str:
        """Adjust difficulty based on student factors."""
        difficulty_levels = ["beginner", "intermediate", "advanced"]
        current_idx = difficulty_levels.index(base_difficulty) if base_difficulty in difficulty_levels else 1

        # Factors that might decrease difficulty
        decrease_factors = []
        if profile["emotional_factors"]["confidence_level"] < 0.5:
            decrease_factors.append("low_confidence")
        if wellness["fatigue_level"] > 0.7:
            decrease_factors.append("high_fatigue")
        if wellness["stress_level"] > 0.6:
            decrease_factors.append("high_stress")
        if profile["performance_history"]["average_score"] < 70:
            decrease_factors.append("low_performance")

        # Factors that might increase difficulty
        increase_factors = []
        if profile["emotional_factors"]["confidence_level"] > 0.8:
            increase_factors.append("high_confidence")
        if profile["preferred_challenge"] == "advanced":
            increase_factors.append("challenge_preference")
        if profile["performance_history"]["average_score"] > 85:
            increase_factors.append("high_performance")

        # Adjust difficulty
        if len(decrease_factors) > len(increase_factors) and current_idx > 0:
            new_difficulty = difficulty_levels[current_idx - 1]
        elif len(increase_factors) > len(decrease_factors) and current_idx < 2:
            new_difficulty = difficulty_levels[current_idx + 1]
        else:
            new_difficulty = base_difficulty

        return new_difficulty

    def _personalize_resources(self, resources: List[Dict], profile: Dict) -> List[Dict]:
        """Personalize resource selection based on learning style."""
        learning_style = profile["learning_style"]
        personalized = []

        for resource in resources:
            resource_copy = resource.copy()

            # Add personalization notes based on learning style
            if learning_style == "visual":
                if "video" in resource.get("type", "").lower():
                    resource_copy["priority"] = "high"
                    resource_copy["reasoning"] = "Matches your visual learning style"
                else:
                    resource_copy["priority"] = "medium"
            elif learning_style == "auditory":
                if "video" in resource.get("type", "").lower():
                    resource_copy["priority"] = "high"
                    resource_copy["reasoning"] = "Audio-visual content suits your learning style"
                else:
                    resource_copy["priority"] = "low"
            else:  # reading_writing or kinesthetic
                if "article" in resource.get("type", "").lower():
                    resource_copy["priority"] = "high"
                    resource_copy["reasoning"] = "Text-based resources match your learning preferences"
                else:
                    resource_copy["priority"] = "medium"

            personalized.append(resource_copy)

        # Sort by priority
        priority_order = {"high": 0, "medium": 1, "low": 2}
        personalized.sort(key=lambda x: priority_order.get(x.get("priority", "medium"), 1))

        return personalized

    def _create_adaptive_plan(self, topic: str, difficulty: str, resources: List[Dict],
                            profile: Dict, wellness: Dict) -> Dict[str, Any]:
        """Create an adaptive study plan."""
        preferred_time = profile["study_habits"]["preferred_time"]
        optimal_duration = profile["study_habits"]["session_duration"]
        break_freq = profile["study_habits"]["break_frequency"]

        # Adjust session duration based on wellness
        if wellness["fatigue_level"] > 0.6:
            optimal_duration = max(30, optimal_duration * 0.7)  # Reduce by 30%
        elif wellness["stress_level"] > 0.5:
            optimal_duration = max(25, optimal_duration * 0.8)  # Reduce by 20%

        plan = {
            "topic": topic,
            "difficulty": difficulty,
            "schedule_preference": preferred_time,
            "session_structure": {
                "duration_minutes": int(optimal_duration),
                "break_frequency_minutes": break_freq,
                "resources_per_session": 2
            },
            "recommended_resources": resources[:3],  # Top 3 personalized resources
            "adaptive_elements": self._get_adaptive_elements(profile, wellness)
        }

        return plan

    def _get_adaptive_elements(self, profile: Dict, wellness: Dict) -> List[Dict]:
        """Get adaptive learning elements."""
        elements = []

        # Add elements based on profile
        if profile["pace_preference"] == "slow":
            elements.append({
                "type": "paced_learning",
                "description": "Extended time for concept absorption",
                "benefit": "Better understanding through deliberate pacing"
            })

        if profile["emotional_factors"]["motivation_level"] < 0.6:
            elements.append({
                "type": "gamification",
                "description": "Achievement badges and progress rewards",
                "benefit": "Increased motivation through gamified elements"
            })

        # Add wellness-based adaptations
        if wellness["fatigue_level"] > 0.5:
            elements.append({
                "type": "micro_learning",
                "description": "Short, focused learning bursts",
                "benefit": "Reduces cognitive load and maintains focus"
            })

        return elements

    def _explain_personalization(self, profile: Dict, wellness: Dict) -> str:
        """Explain why the personalization choices were made."""
        reasons = []

        learning_style = profile["learning_style"]
        reasons.append(f"Prioritized resources matching your {learning_style} learning style")

        if profile["emotional_factors"]["confidence_level"] < 0.6:
            reasons.append("Adjusted difficulty downward due to confidence considerations")

        if wellness["fatigue_level"] > 0.6:
            reasons.append("Reduced session intensity to accommodate fatigue levels")

        if wellness["stress_level"] > 0.5:
            reasons.append("Incorporated stress-management elements in the study plan")

        return " | ".join(reasons)

def get_personalized_path(topic: str, learning_resources: Dict, wellness_assessment: Dict,
                         student_id: str, past_performance: List[Dict] = None) -> Dict[str, Any]:
    """Helper function to get personalized learning path."""
    agent = PersonalizationAgent()
    profile = agent.analyze_student_profile(student_id, past_performance)
    return agent.recommend_personalized_path(topic, learning_resources, wellness_assessment, profile)
