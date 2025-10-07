"""Wellness Agent - Monitors stress, fatigue, and mental health with Hume AI emotion detection."""

from typing import Dict, Any, List
import random
import time
import os
import asyncio
import base64
import io
import json
from PIL import Image
import numpy as np
from dotenv import load_dotenv

try:
    from hume import HumeBatchClient
    from hume.models import BurstConfig, FacemeshConfig
    HUME_AVAILABLE = True
except ImportError:
    HUME_AVAILABLE = False

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

class WellnessAgent:
    """Agent for monitoring and supporting student wellness with Hume AI."""

    def __init__(self):
        self.hume_api_key = os.getenv("HUME_API_KEY")
        self.hume_client = None

        if HUME_AVAILABLE and self.hume_api_key:
            try:
                self.hume_client = HumeBatchClient(self.hume_api_key)
                print("🎥 Hume AI emotion detection initialized")
            except Exception as e:
                print(f"Failed to initialize Hume AI: {e}")
                self.hume_client = None

        self.emotions = [
            "happy", "sad", "angry", "fearful", "surprised", "disgusted",
            "neutral", "confused", "focused", "tired", "stressed", "relaxed"
        ]

    def assess_wellness(self, facial_data: Dict = None, activity_data: Dict = None, capture_image: bool = True) -> Dict[str, Any]:
        """Assess student's current wellness state with real AI analysis."""

        # Try real Hume AI emotion detection first
        hume_emotion_data = None
        if capture_image and self.hume_client and CV2_AVAILABLE:
            try:
                hume_emotion_data = self._capture_and_analyze_emotion()
            except Exception as e:
                print(f"Hume AI analysis failed: {e}")

        wellness_report = {
            "fatigue_level": self._calculate_fatigue(facial_data, activity_data, hume_emotion_data),
            "stress_level": self._calculate_stress(facial_data, activity_data, hume_emotion_data),
            "emotional_state": self._detect_emotion(hume_emotion_data, facial_data),
            "activity_level": self._assess_activity(activity_data),
            "hume_emotion_data": hume_emotion_data,
            "recommendations": [],
            "wellness_breaks": []
        }

        # Generate personalized recommendations
        wellness_report["recommendations"] = self._generate_recommendations(wellness_report)
        wellness_report["wellness_breaks"] = self._suggest_breaks(wellness_report)

        return wellness_report

    async def analyze_emotion_async(self, image_data: bytes) -> Dict[str, Any]:
        """Async emotion analysis using Hume AI."""
        if not self.hume_client:
            return {"emotion": "neutral", "confidence": 0.5, "mood": "stable"}

        try:
            # Configure Hume AI for facial emotion analysis
            configs = [BurstConfig(), FacemeshConfig()]

            # Convert image bytes to base64
            image_b64 = base64.b64encode(image_data).decode("utf-8")
            urls = [f"data:image/jpeg;base64,{image_b64}"]

            # Run Hume AI analysis
            job = self.hume_client.submit_job(urls, configs)

            # Wait for results
            result = job.get_job_result()
            predictions = result.get("predictions", [])

            if predictions and len(predictions) > 0:
                # Extract top emotions from first face detected
                faces = predictions[0].get("results", {}).get("predictions", [])
                if faces and len(faces) > 0:
                    face = faces[0]

                    # Get burst emotions (immediate emotional state)
                    burst_emotions = face.get("models", {}).get("burst", {}).get("grouped_predictions", [])

                    if burst_emotions and len(burst_emotions) > 0:
                        top_emotion_data = burst_emotions[0].get("predictions", [{}])[0]
                        emotion_name = top_emotion_data.get("name", "neutral").lower()

                        # Convert Hume AI emotions to our emotion categories
                        translated_emotion = self._translate_hume_emotion(emotion_name)

                        # Get confidence score
                        confidence = top_emotion_data.get("confidence", 0.5)

                        return {
                            "emotion": translated_emotion,
                            "confidence": confidence,
                            "all_emotions": [{
                                "name": pred.get("name", "").lower(),
                                "score": pred.get("confidence", 0)
                            } for pred in burst_emotions[0].get("predictions", [])][:5],
                            "detected_at": time.time()
                        }

        except Exception as e:
            print(f"Hume AI emotion analysis error: {e}")

        # Fallback response
        return {
            "emotion": "neutral",
            "confidence": 0.5,
            "all_emotions": [{"name": "neutral", "score": 0.5}],
            "error": str(e) if 'e' in locals() else None
        }

    def _capture_and_analyze_emotion(self) -> Dict[str, Any]:
        """Capture webcam image and analyze emotion."""
        if not CV2_AVAILABLE:
            return {"emotion": "neutral", "confidence": 0.5}

        cap = None
        try:
            # Initialize webcam
            cap = cv2.VideoCapture(0)

            if not cap.isOpened():
                print("Could not access webcam for Hume AI analysis")
                return {"emotion": "neutral", "confidence": 0.5, "error": "webcam_unavailable"}

            # Capture a frame
            ret, frame = cap.read()
            if not ret:
                return {"emotion": "neutral", "confidence": 0.5, "error": "capture_failed"}

            # Convert to PIL Image and then to bytes
            pil_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            buffer = io.BytesIO()
            pil_image.save(buffer, format="JPEG")
            image_data = buffer.getvalue()

            # Run async analysis (will run synchronously here)
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.analyze_emotion_async(image_data))
            loop.close()

            return result

        except Exception as e:
            print(f"Webcam emotion analysis failed: {e}")
            return {"emotion": "neutral", "confidence": 0.5, "error": str(e)}
        finally:
            if cap:
                cap.release()

    def _translate_hume_emotion(self, hume_emotion: str) -> str:
        """Translate Hume AI emotion names to our categories."""
        emotion_mapping = {
            "joy": "happy",
            "sadness": "sad",
            "anger": "angry",
            "Fear": "fearful",
            "surprise": "surprised",
            "disgust": "disgusted",
            "neutral": "neutral",
            "amusement": "happy",
            "excitement": "happy",
            "contentment": "relaxed",
            "anxiety": "stressed",
            "confusion": "confused",
            "frustration": "stressed",
            "tiredness": "tired",
            "determination": "focused",
            "concentration": "focused",
            "interest": "focused",
            "boredom": "neutral"
        }

        # Partial matching for emotion variations
        for hume_key, our_emotion in emotion_mapping.items():
            if hume_emotion.lower().startswith(hume_key.lower()) or hume_emotion.lower().endswith(hume_key.lower()):
                return our_emotion

        return "neutral"  # Default fallback

    def _calculate_fatigue(self, facial_data: Dict = None, activity_data: Dict = None, hume_data: Dict = None) -> float:
        """Calculate fatigue level using Hume AI data."""
        base_fatigue = 0.3  # Baseline

        # Time-based fatigue
        import datetime
        current_hour = datetime.datetime.now().hour
        if 22 <= current_hour or current_hour <= 6:
            base_fatigue += 0.4
        elif 18 <= current_hour <= 21:
            base_fatigue += 0.2

        # Hume AI-based fatigue indicators
        if hume_data and hume_data.get("confidence", 0) > 0.6:
            emotion = hume_data.get("emotion", "").lower()

            # Direct fatigue indicators from Hume AI
            if emotion in ["tired", "sleepy", "boredom", "disengaged"]:
                base_fatigue += 0.4
            elif emotion in ["focused", "determined", "curious"]:
                base_fatigue -= 0.2  # Alert emotions reduce fatigue
            elif emotion in ["frustrated", "irritated"]:
                base_fatigue += 0.3  # Emotional exhaustion

        # Legacy facial analysis fallback
        if facial_data:
            fatigue_indicators = facial_data.get("fatigue_indicators", [])
            if "tired_eyes" in fatigue_indicators:
                base_fatigue += 0.3
            if "yawning" in fatigue_indicators:
                base_fatigue += 0.2

        # Activity data
        if activity_data:
            steps_today = activity_data.get("steps_today", 5000)
            if steps_today < 3000:
                base_fatigue += 0.2

        return min(1.0, max(0.0, base_fatigue))

    def _calculate_stress(self, facial_data: Dict = None, activity_data: Dict = None, hume_data: Dict = None) -> float:
        """Calculate stress level using Hume AI data."""
        base_stress = 0.2  # Baseline

        # Hume AI stress indicators
        if hume_data and hume_data.get("confidence", 0) > 0.6:
            emotion = hume_data.get("emotion", "").lower()

            stress_emotions = ["anxiety", "fear", "anger", "frustration", "irritation", "stress"]
            if any(e in emotion for e in stress_emotions):
                base_stress += 0.4

            calm_emotions = ["contentment", "relaxation", "satisfaction", "peace"]
            if any(e in emotion for e in calm_emotions):
                base_stress -= 0.2

        # Legacy stress indicators
        if facial_data:
            stress_indicators = facial_data.get("stress_indicators", [])
            if "frown" in stress_indicators:
                base_stress += 0.3
            if "tense_jaw" in stress_indicators:
                base_stress += 0.2

        if activity_data:
            hrv = activity_data.get("heart_rate_variability", 50)
            if hrv < 30:
                base_stress += 0.3
            elif hrv > 70:
                base_stress -= 0.2

        return min(1.0, max(0.0, base_stress))

    def _detect_emotion(self, hume_data: Dict = None, legacy_facial_data: Dict = None) -> str:
        """Detect dominant emotion using Hume AI or fallback."""

        # Use Hume AI data if available and confident
        if hume_data and hume_data.get("confidence", 0) > 0.7:
            return hume_data.get("emotion", "neutral")

        # Legacy fallback
        if legacy_facial_data and "emotion" in legacy_facial_data:
            return legacy_facial_data["emotion"]

        # Time-adjusted simulation
        import datetime
        hour = datetime.datetime.now().hour
        base_emotions = ["focused", "confused", "tired", "stressed", "neutral", "happy"]

        if hour >= 22 or hour <= 6:
            base_emotions = ["tired", "focused", "neutral", "confused", "stressed", "happy"]

        return random.choices(base_emotions, weights=[0.3, 0.2, 0.15, 0.1, 0.15, 0.1], k=1)[0]

    def _assess_activity(self, activity_data: Dict = None) -> Dict[str, Any]:
        """Assess physical activity levels."""
        if activity_data:
            return {
                "steps_today": activity_data.get("steps_today", 5000),
                "active_minutes": activity_data.get("active_minutes", 45),
                "calories_burned": activity_data.get("calories_burned", 1800),
                "last_activity": activity_data.get("last_activity", "walking")
            }

        # Simulate activity data
        return {
            "steps_today": random.randint(3000, 8000),
            "active_minutes": random.randint(20, 90),
            "calories_burned": random.randint(1500, 2200),
            "last_activity": random.choice(["walking", "running", "cycling", "sitting"])
        }

    def _generate_recommendations(self, wellness_report: Dict) -> List[Dict]:
        """Generate personalized wellness recommendations based on Hume AI data."""
        recommendations = []

        fatigue = wellness_report["fatigue_level"]
        stress = wellness_report["stress_level"]
        emotion = wellness_report["emotional_state"]
        hume_data = wellness_report.get("hume_emotion_data", {})

        # High fatigue -> immediate rest
        if fatigue > 0.7:
            recommendations.append({
                "type": "rest",
                "priority": "high",
                "title": "Immediate Rest Break",
                "description": "Emotion analysis shows signs of high fatigue. Take a 15-minute break with deep breathing.",
                "duration": "15 minutes",
                "benefits": "Reduces mental fatigue and improves focus"
            })

        # High stress from emotion data
        if stress > 0.6 or emotion in ["anxious", "stressed", "frustrated"]:
            recommendations.append({
                "type": "mindfulness",
                "priority": "medium",
                "title": "Emotion-Focused Stress Management",
                "description": f"Analysis shows you're feeling {emotion}. Try progressive muscle relaxation or short meditation.",
                "duration": "10 minutes",
                "benefits": "Lowers cortisol levels and improves concentration"
            })

        # Emotion-specific recommendations
        if emotion == "confused":
            recommendations.append({
                "type": "study_technique",
                "priority": "low",
                "title": "Change Study Approach",
                "description": "Your facial expressions suggest confusion. Try a different explanation or take short breaks.",
                "duration": "N/A",
                "benefits": "Improves understanding and reduces frustration"
            })

        if emotion in ["tired", "sleepy"]:
            recommendations.append({
                "type": "hydration_nutrition",
                "priority": "medium",
                "title": "Energy Boost Check",
                "description": "Drink water, have a healthy snack, and consider a 5-minute walk.",
                "duration": "5 minutes",
                "benefits": "Increases alertness and cognitive function"
            })

        if emotion in ["happy", "excited", "focused"]:
            recommendations.append({
                "type": "motivation",
                "priority": "low",
                "title": "Ride the Momentum",
                "description": f"Great to see you're feeling {emotion}! Use this positive state to tackle challenging materials.",
                "duration": "N/A",
                "benefits": "Optimizes learning during peak emotional states"
            })

        # Hume AI confidence indicator
        confidence = hume_data.get("confidence", 0)
        if confidence > 0.8:
            recommendations.append({
                "type": "ai_insight",
                "priority": "low",
                "title": "AI Emotion Analysis",
                "description": f"High confidence emotion detection enabled. Current state: {emotion} ({confidence:.1f} confidence).",
                "duration": "N/A",
                "benefits": "Personalized learning based on real emotional state"
            })

        return recommendations[:3]  # Maximum 3 recommendations

    def _suggest_breaks(self, wellness_report: Dict) -> List[Dict]:
        """Suggest strategic breaks based on Hume AI emotional analysis."""
        breaks = []

        fatigue = wellness_report["fatigue_level"]
        stress = wellness_report["stress_level"]
        emotion = wellness_report["emotional_state"]

        # Enhanced break suggestions based on emotion
        if fatigue > 0.5 or emotion in ["tired", "boredom"]:
            breaks.append({
                "timing": "every_45_minutes",
                "duration": "10 minutes",
                "activity": "mindfulness_meditation",
                "purpose": "combat_fatigue"
            })

        if stress > 0.5 or emotion in ["anxious", "frustrated", "stressed"]:
            breaks.append({
                "timing": "every_75_minutes",
                "duration": "5 minutes",
                "activity": "deep_breathing",
                "purpose": "reduce_stress"
            })

        # Emotion-specific breaks
        if emotion == "confused":
            breaks.append({
                "timing": "every_90_minutes",
                "duration": "10 minutes",
                "activity": "concept_review",
                "purpose": "clarify_confusion"
            })

        # General wellness break
        breaks.append({
            "timing": "every_60_minutes",
            "duration": "5 minutes",
            "activity": "eye_rest_walk",
            "purpose": "general_wellness"
        })

        return breaks[:3]  # Maximum 3 breaks

def get_wellness_assessment(facial_data: Dict = None, activity_data: Dict = None) -> Dict[str, Any]:
    """Helper function to get wellness assessment."""
    agent = WellnessAgent()
    return agent.assess_wellness(facial_data, activity_data)
