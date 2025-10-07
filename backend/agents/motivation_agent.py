"""Motivation Agent - Provides emotional support and encouragement."""

from typing import Dict, List, Any
import random
import json
from datetime import datetime
import google.generativeai as genai

class MotivationAgent:
    """Agent for keeping students engaged and emotionally supported."""

    def __init__(self, gemini_api_key: str):
        genai.configure(api_key=gemini_api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        self.affirmations = [
            "You're capable of amazing things when you put your mind to it.",
            "Every expert was once a beginner. You're right where you need to be.",
            "Your brain is getting stronger with every concept you learn.",
            "Mistakes are proof that you're trying - that's something to be proud of!",
            "You're building knowledge that will serve you for the rest of your life.",
            "Learning is a journey, not a race. Celebrate your progress.",
            "You have the power to master this material, one step at a time.",
            "Your dedication to learning sets you apart from the crowd."
        ]

        self.encouraging_messages = {
            "excellent_performance": [
                "Outstanding work! You're mastering this material brilliantly.",
                "Exceptional performance! Keep up this incredible momentum.",
                "You're absolutely crushing it! This level of understanding is impressive."
            ],
            "good_performance": [
                "Great job! You're building a solid foundation.",
                "Well done! Your hard work is paying off.",
                "Nice work! You're making excellent progress."
            ],
            "needs_improvement": [
                "Keep pushing forward! Every expert has faced challenges like this.",
                "You're building resilience with every attempt. That's valuable too!",
                "Learning takes time. You're getting stronger every day."
            ],
            "struggling": [
                "Remember: every journey has difficult stretches. You've got this!",
                "Take a moment to breathe. You're capable of more than you know.",
                "This challenge is shaping you into an even stronger learner."
            ]
        }

    def generate_motivational_response(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate personalized motivational content based on context."""

        performance_level = context.get("performance_level", "good_performance")
        emotional_state = context.get("emotional_state", "neutral")
        fatigue_level = context.get("fatigue_level", 0.3)
        progress_milestone = context.get("progress_milestone", False)

        response = {
            "primary_message": self._get_primary_message(performance_level, emotional_state),
            "affirmation": random.choice(self.affirmations),
            "encouragement": self._generate_encouragement(performance_level, emotional_state),
            "progress_celebration": self._celebrate_progress(context),
            "support_elements": self._provide_support(fatigue_level, emotional_state),
            "next_goal": self._suggest_next_goal(context)
        }

        return response

    def _get_primary_message(self, performance_level: str, emotional_state: str) -> str:
        """Get the main motivational message."""
        messages = self.encouraging_messages.get(performance_level, self.encouraging_messages["good_performance"])

        # Adjust based on emotional state
        if emotional_state == "tired":
            messages = [msg + " Remember to take care of yourself too!" for msg in messages]
        elif emotional_state == "stressed":
            messages = [msg + " Take a deep breath - you've got this!" for msg in messages]
        elif emotional_state == "confused":
            messages = ["You're making progress even when it doesn't feel like it!"]
        elif emotional_state == "focused":
            messages = [msg + " Your concentration is paying off!" for msg in messages]

        return random.choice(messages)

    def _generate_encouragement(self, performance_level: str, emotional_state: str) -> Dict[str, Any]:
        """Generate detailed encouragement."""
        encouragement = {
            "immediate": "",
            "long_term": "",
            "specific_action": ""
        }

        # Immediate encouragement
        if performance_level == "excellent_performance":
            encouragement["immediate"] = "You're excelling in ways that matter!"
        elif performance_level == "needs_improvement":
            encouragement["immediate"] = "This is hard, and that's okay. Hard things make us grow."
        else:
            encouragement["immediate"] = "You're making meaningful progress every day."

        # Long-term perspective
        encouragement["long_term"] = random.choice([
            "Remember why you started. That passion brought you here.",
            "The skills you're building now will open incredible doors.",
            "Every concept you master increases your capabilities exponentially.",
            "You're developing mental resilience that lasts a lifetime.",
            "Knowledge compounds over time - you're investing in your future self."
        ])

        # Specific action
        encouragement["specific_action"] = self._get_specific_action(performance_level, emotional_state)

        return encouragement

    def _get_specific_action(self, performance_level: str, emotional_state: str) -> str:
        """Suggest a specific actionable encouragement."""
        actions = []

        if performance_level in ["needs_improvement", "struggling"]:
            actions.extend([
                "Break this into smaller, manageable steps.",
                "Try teaching this concept to someone else (real or imaginary).",
                "Compare your current understanding to where you were a week ago.",
                "Focus on understanding one key concept deeply rather than rushing through many."
            ])
        else:
            actions.extend([
                "Build on this success by tackling a related challenge.",
                "Share what you've learned with someone - teaching reinforces learning.",
                "Reflect on what strategies helped you succeed here.",
                "Set a small reward for reaching your next milestone."
            ])

        # Add emotional state specific actions
        if emotional_state == "tired":
            actions.append("Take a 5-minute walk or stretch break to recharge.")
        elif emotional_state == "stressed":
            actions.append("Try the 4-7-8 breathing technique: inhale for 4, hold for 7, exhale for 8.")
        elif emotional_state == "confused":
            actions.append("Step away briefly, then come back with fresh eyes.")
        elif emotional_state == "happy":
            actions.append("Ride this positive momentum to tackle the next challenge!")

        return random.choice(actions)

    def _celebrate_progress(self, context: Dict[str, Any]) -> str:
        """Celebrate progress milestones."""
        milestone_messages = []

        if context.get("progress_milestone"):
            milestone_messages.extend([
                "🎉 Milestone achieved! You've grown so much!",
                "🌟 Progress celebration! Pat yourself on the back!",
                "⭐ Achievement unlocked! You're making real progress!",
                "🏆 Goal reached! You deserve to feel proud of this!"
            ])

        if context.get("days_studied", 0) > 0:
            days = context["days_studied"]
            if days % 7 == 0:  # Weekly milestone
                milestone_messages.append(f"📅 Week {days//7} complete! Consistency is your superpower!")
            elif days in [1, 7, 30]:  # Special day counts
                milestone_messages.append(f"🎯 {days} day{'s' if days != 1 else ''} of consistent learning! That's commitment!")

        if context.get("topics_mastered", 0) > 0:
            topics = context["topics_mastered"]
            milestone_messages.append(f"🧠 {topics} topic{'s' if topics != 1 else ''} mastered! Your knowledge is growing!")

        # Default celebration if no specific milestones
        if not milestone_messages:
            improvement_rate = context.get("improvement_rate", 0)
            if improvement_rate > 0:
                milestone_messages.append(f"📈 Improving by {improvement_rate:.1f}% - that's real growth!")
            else:
                milestone_messages.append("💪 Every study session makes you stronger!")

        return random.choice(milestone_messages) if milestone_messages else random.choice([
            "🌱 Small steps, big changes. You're growing!",
            "💡 Learning is progress. Progress is success.",
            "🔥 Keep the learning fire burning!"
        ])

    def _provide_support(self, fatigue_level: float, emotional_state: str) -> List[Dict[str, Any]]:
        """Provide supportive elements based on current state."""
        supports = []

        # Wellness-based support
        if fatigue_level > 0.7:
            supports.append({
                "type": "rest_reminder",
                "message": "Your body and mind need rest to perform at their best.",
                "action": "Consider a short break or earlier bedtime tonight."
            })

        if fatigue_level > 0.5:
            supports.append({
                "type": "energy_boost",
                "message": "Keep hydrated and fuel your brain with healthy snacks.",
                "action": "Drink water and eat something nutritious soon."
            })

        # Emotional state support
        if emotional_state == "confused":
            supports.append({
                "type": "perspective_shift",
                "message": "Confusion is often a sign you're about to have an 'aha!' moment.",
                "action": "Be patient with yourself - clarity often comes after wrestling with ideas."
            })

        if emotional_state == "stressed":
            supports.append({
                "type": "stress_relief",
                "message": "Learning works best when your nervous system is calm.",
                "action": "Try box breathing: inhale for 4 counts, hold for 4, exhale for 4."
            })

        if emotional_state == "tired":
            supports.append({
                "type": "gentle_encouragement",
                "message": "Even tired minds can learn - you're capable of more than you think.",
                "action": "If possible, study during your peak energy time tomorrow."
            })

        # Always include one general support
        supports.append({
            "type": "self_compassion",
            "message": "Be kind to yourself on this learning journey.",
            "action": "Acknowledge that learning is challenging and you're doing your best."
        })

        return supports[:3]  # Limit to 3 supports

    def _suggest_next_goal(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Suggest the next achievable goal."""
        performance_level = context.get("performance_level", "good_performance")
        current_topic = context.get("current_topic", "your studies")

        goals = {
            "excellent_performance": [
                {"goal": f"Master an advanced concept in {current_topic}",
                 "timeline": "this week",
                 "reward": "A special treat or celebration"},
                {"goal": "Help someone else understand a concept you've mastered",
                 "timeline": "within 2 days",
                 "reward": "The satisfaction of teaching"}
            ],
            "good_performance": [
                {"goal": f"Complete one more practice session on {current_topic}",
                 "timeline": "today",
                 "reward": "Time for something enjoyable"},
                {"goal": "Review what you've learned this week",
                 "timeline": "tomorrow",
                 "reward": "A sense of accomplishment"}
            ],
            "needs_improvement": [
                {"goal": f"Spend focused time on difficult parts of {current_topic}",
                 "timeline": "next study session",
                 "reward": "Celebrate the effort, regardless of outcome"},
                {"goal": "Break down one complex concept into smaller parts",
                 "timeline": "today",
                 "reward": "Progress is the real victory"}
            ]
        }

        goal_set = goals.get(performance_level, goals["good_performance"])
        selected_goal = random.choice(goal_set)

        return {
            "goal": selected_goal["goal"],
            "timeline": selected_goal["timeline"],
            "reward": selected_goal["reward"],
            "motivation": "Small goals create big momentum!"
        }

    def create_daily_motivation(self, user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create daily motivational content for sustained engagement."""
        # Get current context or use defaults
        context = user_context or {
            "performance_trend": random.choice(["improving", "steady", "challenging"]),
            "study_streak": random.randint(0, 10),
            "time_of_day": datetime.now().strftime("%H:%M")
        }

        daily_motivation = {
            "greeting": self._get_time_based_greeting(),
            "daily_affirmation": random.choice(self.affirmations),
            "focus_message": self._get_focus_message(context),
            "streak_celebration": self._celebrate_streak(context.get("study_streak", 0)),
            "wellness_reminder": self._get_wellness_reminder()
        }

        return daily_motivation

    def _get_time_based_greeting(self) -> str:
        """Get appropriate greeting based on time of day."""
        hour = datetime.now().hour

        if 5 <= hour < 12:
            return random.choice(["Good morning!", "Rise and shine!", "Morning motivation time!"])
        elif 12 <= hour < 17:
            return random.choice(["Good afternoon!", "Hope your day's going well!", "Afternoon focus!"])
        elif 17 <= hour < 22:
            return random.choice(["Good evening!", "Evening study session!", "Evening motivation!"])
        else:
            return random.choice(["Burning the midnight oil?", "Late night learning!", "Night owl studying!"])

    def _get_focus_message(self, context: Dict) -> str:
        """Get focused motivational message."""
        trend = context.get("performance_trend", "steady")

        if trend == "improving":
            return "You're on an upward trajectory - keep the momentum going!"
        elif trend == "challenging":
            return "Every expert faces challenges. You're building resilience!"
        else:
            return "Consistent effort creates lasting results. You're on the right path!"

    def _celebrate_streak(self, streak: int) -> str:
        """Celebrate study streak."""
        if streak == 0:
            return "Every journey starts with a single step. Ready to begin?"
        elif streak == 1:
            return "First day down! The habit is forming! 🎯"
        elif streak < 7:
            return f"{streak} days in a row! Building momentum! 🔥"
        elif streak < 30:
            return f"{streak} day streak! You're unstoppable! ⚡"
        else:
            return f"{streak} days of consistent learning! Legendary! 🏆"

    def _get_wellness_reminder(self) -> str:
        """Get wellness reminder."""
        reminders = [
            "Remember to stay hydrated while learning.",
            "Take regular breaks to keep your mind sharp.",
            "Movement energizes learning - stand up and stretch!",
            "Healthy eating fuels brain power.",
            "Good sleep is your secret learning weapon.",
            "A positive mindset enhances understanding."
        ]
        return random.choice(reminders)

def get_motivational_support(context: Dict[str, Any], api_key: str) -> Dict[str, Any]:
    """Helper function to get motivational support."""
    agent = MotivationAgent(api_key)
    return agent.generate_motivational_response(context)

def get_daily_motivation(user_context: Dict = None, api_key: str = None) -> Dict[str, Any]:
    """Helper function to get daily motivation."""
    agent = MotivationAgent(api_key or "dummy_key")
    return agent.create_daily_motivation(user_context)
