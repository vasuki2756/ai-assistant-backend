"""Schedule Agent - Creates and manages study plans and calendar events with Google Calendar integration."""

from typing import Dict, List, Any
from datetime import datetime, timedelta
import json
import os
from dotenv import load_dotenv

# Google Calendar API imports
try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    GOOGLE_CALENDAR_AVAILABLE = True
except ImportError:
    GOOGLE_CALENDAR_AVAILABLE = False

class ScheduleAgent:
    """Agent for creating study schedules and managing calendar with Google Calendar integration."""

    def __init__(self):
        self.calendar_service = None
        self._initialize_google_calendar()

    def _initialize_google_calendar(self):
        """Initialize Google Calendar API service."""
        if not GOOGLE_CALENDAR_AVAILABLE:
            print("Google Calendar API libraries not available - falling back to mock events")
            return

        try:
            # Get credentials from environment
            client_id = os.getenv("GOOGLE_CALENDAR_CLIENT_ID")
            client_secret = os.getenv("GOOGLE_CALENDAR_CLIENT_SECRET")
            refresh_token = os.getenv("GOOGLE_CALENDAR_CREDENTIALS_REFRESH_TOKEN")

            if not all([client_id, client_secret, refresh_token]):
                print("Google Calendar credentials not found in environment - falling back to mock events")
                print("Set GOOGLE_CALENDAR_CLIENT_ID, GOOGLE_CALENDAR_CLIENT_SECRET, and GOOGLE_CALENDAR_CREDENTIALS_REFRESH_TOKEN")
                return

            # Create credentials using refresh token
            creds = Credentials(
                token=None,
                refresh_token=refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=client_id,
                client_secret=client_secret,
                scopes=["https://www.googleapis.com/auth/calendar.events"]
            )

            # Refresh the token if needed
            if creds.expired or not creds.valid:
                creds.refresh(Request())

            # Build the service
            self.calendar_service = build("calendar", "v3", credentials=creds)
            print("✅ Google Calendar API initialized successfully")

        except Exception as e:
            print(f"Failed to initialize Google Calendar API: {e}")
            print("Falling back to mock calendar events")
            self.calendar_service = None

    def create_study_plan(self, topic: str, learning_data: Dict[str, Any], wellness_data: Dict[str, Any] = None, create_google_events: bool = False) -> Dict[str, Any]:
        """Create a personalized study plan based on learning resources and wellness data."""

        resources = learning_data.get("resources", [])
        difficulty = learning_data.get("difficulty", "intermediate")
        estimated_time = learning_data.get("estimated_time", "2 hours")

        # Parse estimated time
        try:
            total_hours = float(estimated_time.split()[0])
        except:
            total_hours = 2.0

        # Create study sessions over multiple days
        sessions = self._create_sessions(topic, resources, total_hours, difficulty)

        # Add wellness breaks if data available
        if wellness_data and wellness_data.get("fatigue_level", 0) > 0.5:
            sessions = self._add_wellness_breaks(sessions, wellness_data)

        # Generate calendar events (Google Calendar or mock)
        calendar_events = self._generate_calendar_events(sessions)

        # Create actual Google Calendar events if requested and available
        google_calendar_result = None
        if create_google_events and self.calendar_service:
            google_calendar_result = self._create_google_calendar_events(calendar_events, topic)
        elif create_google_events and not self.calendar_service:
            print("Google Calendar API not available - cannot create real calendar events")

        return {
            "study_plan": {
                "topic": topic,
                "total_duration": f"{total_hours} hours",
                "difficulty": difficulty,
                "sessions": sessions
            },
            "calendar_events": calendar_events,
            "google_calendar_result": google_calendar_result
        }

    def _create_sessions(self, topic: str, resources: List[Dict], total_hours: float, difficulty: str) -> List[Dict]:
        """Create study sessions spread over days."""
        sessions = []

        # Split into manageable chunks
        if difficulty == "beginner":
            session_duration = 1.0  # 1 hour sessions
        elif difficulty == "intermediate":
            session_duration = 1.5  # 1.5 hour sessions
        else:  # advanced
            session_duration = 2.0  # 2 hour sessions

        num_sessions = max(1, int(total_hours / session_duration))
        hours_per_session = total_hours / num_sessions

        current_date = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)  # Start at 9 AM

        for i in range(num_sessions):
            if i > 0:
                # Add a day gap
                current_date += timedelta(days=1)

            session_resources = resources[i % len(resources)] if resources else {}

            sessions.append({
                "session_id": f"session_{i+1}",
                "date": current_date.strftime("%Y-%m-%d"),
                "time": current_date.strftime("%H:%M"),
                "duration": f"{hours_per_session:.1f} hours",
                "topic": f"{topic} - Part {i+1}",
                "resources": [session_resources],
                "activities": self._get_session_activities(topic, i, num_sessions)
            })

        return sessions

    def _get_session_activities(self, topic: str, session_num: int, total_sessions: int) -> List[str]:
        """Generate activities for a study session."""
        activities = []

        if session_num == 0:  # First session
            activities.extend([
                "Review fundamental concepts",
                "Watch introductory video",
                "Take notes on key terms"
            ])
        elif session_num == total_sessions - 1:  # Last session
            activities.extend([
                "Review all learned concepts",
                "Practice with example problems",
                "Self-assessment quiz"
            ])
        else:  # Middle sessions
            activities.extend([
                "Deep dive into specific topic areas",
                "Practical exercises and examples",
                "Review previous session material"
            ])

        return activities

    def _add_wellness_breaks(self, sessions: List[Dict], wellness_data: Dict) -> List[Dict]:
        """Add wellness breaks to sessions based on fatigue levels."""
        fatigue_level = wellness_data.get("fatigue_level", 0)

        for session in sessions:
            # Add mindfulness break every hour for high fatigue
            if fatigue_level > 0.7:
                session["wellness_break"] = {
                    "duration": "10 minutes",
                    "activity": "Mindfulness meditation",
                    "reason": "High fatigue detected - mental health break needed"
                }
            elif fatigue_level > 0.5:
                session["wellness_break"] = {
                    "duration": "5 minutes",
                    "activity": "Quick stretch break",
                    "reason": "Medium fatigue - physical break recommended"
                }

        return sessions

    def _generate_calendar_events(self, sessions: List[Dict]) -> List[Dict]:
        """Generate calendar events for Google Calendar integration."""
        events = []

        for session in sessions:
            event = {
                "summary": f"Study Session: {session['topic']}",
                "description": f"Study {session['topic']} for {session['duration']}",
                "start": {
                    "dateTime": f"{session['date']}T{session['time']}:00",
                    "timeZone": "UTC"
                },
                "end": {
                    "dateTime": self._calculate_end_time(session['date'], session['time'], session['duration']),
                    "timeZone": "UTC"
                },
                "reminders": {
                    "useDefault": False,
                    "overrides": [
                        {"method": "popup", "minutes": 15}
                    ]
                }
            }
            events.append(event)

            # Add wellness break if present
            if "wellness_break" in session:
                break_duration = session["wellness_break"]["duration"].split()[0]  # "10" from "10 minutes"
                break_start = self._calculate_end_time(session['date'], session['time'], "1 hours")  # After 1 hour

                break_event = {
                    "summary": f"Wellness Break: {session['wellness_break']['activity']}",
                    "description": session['wellness_break']['reason'],
                    "start": {
                        "dateTime": break_start,
                        "timeZone": "UTC"
                    },
                    "end": {
                        "dateTime": self._calculate_end_time_from_datetime(break_start, f"{break_duration} minutes"),
                        "timeZone": "UTC"
                    }
                }
                events.append(break_event)

        return events

    def _calculate_end_time(self, date: str, start_time: str, duration: str) -> str:
        """Calculate end time from start time and duration."""
        try:
            hours = float(duration.split()[0])
            start_dt = datetime.strptime(f"{date} {start_time}", "%Y-%m-%d %H:%M")
            end_dt = start_dt + timedelta(hours=hours)
            return end_dt.strftime("%Y-%m-%dT%H:%M:%S")
        except:
            # Fallback
            return f"{date}T{start_time}:00"

    def _calculate_end_time_from_datetime(self, start_datetime: str, duration: str) -> str:
        """Calculate end time from datetime string and duration."""
        try:
            # Parse ISO format
            if "T" in start_datetime:
                start_dt = datetime.fromisoformat(start_datetime.replace("Z", "+00:00"))
            else:
                start_dt = datetime.strptime(start_datetime, "%Y-%m-%dT%H:%M:%S")

            if "minutes" in duration:
                minutes = int(duration.split()[0])
                end_dt = start_dt + timedelta(minutes=minutes)
            else:
                hours = float(duration.split()[0])
                end_dt = start_dt + timedelta(hours=hours)

            return end_dt.strftime("%Y-%m-%dT%H:%M:%S")
        except:
            return start_datetime

    def _create_google_calendar_events(self, events: List[Dict], topic: str) -> Dict[str, Any]:
        """Create actual Google Calendar events from the event list."""
        if not self.calendar_service:
            return {"success": False, "error": "Google Calendar API not initialized"}

        created_events = []
        failed_events = []

        try:
            # Get primary calendar
            calendar_id = 'primary'

            print(f"📅 Creating {len(events)} Google Calendar events for '{topic}'...")

            for i, event in enumerate(events, 1):
                try:
                    # Add color coding based on event type
                    if "wellness" in event["summary"].lower():
                        event["colorId"] = "11"  # Red for wellness breaks
                    else:
                        event["colorId"] = "10"  # Green for study sessions

                    # Create the event
                    created_event = self.calendar_service.events().insert(
                        calendarId=calendar_id,
                        body=event
                    ).execute()

                    created_events.append({
                        "title": event["summary"],
                        "google_event_id": created_event["id"],
                        "link": created_event.get("htmlLink", ""),
                        "start_time": event["start"]["dateTime"]
                    })

                    print(f"  ✅ Created: {event['summary']}")

                    # Small delay to avoid rate limiting
                    import time
                    time.sleep(0.5)

                except HttpError as e:
                    error_msg = f"Failed to create event '{event['summary']}': {e}"
                    print(f"  ❌ {error_msg}")
                    failed_events.append({
                        "event": event["summary"],
                        "error": str(e)
                    })

            return {
                "success": True,
                "created_count": len(created_events),
                "failed_count": len(failed_events),
                "created_events": created_events,
                "failed_events": failed_events,
                "message": f"Successfully created {len(created_events)} out of {len(events)} calendar events for '{topic}'"
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create calendar events: {str(e)}",
                "created_events": created_events,
                "failed_events": failed_events
            }

    def create_calendar_event(self, summary: str, description: str, start_datetime: str, duration_minutes: int) -> Dict[str, Any]:
        """Create a single calendar event manually."""
        if not self.calendar_service:
            return {"success": False, "error": "Google Calendar API not initialized"}

        try:
            # Calculate end time
            start_dt = datetime.fromisoformat(start_datetime.replace("Z", "+00:00"))
            end_dt = start_dt + timedelta(minutes=duration_minutes)

            event = {
                "summary": summary,
                "description": description,
                "start": {
                    "dateTime": start_dt.isoformat(),
                    "timeZone": "UTC"
                },
                "end": {
                    "dateTime": end_dt.isoformat(),
                    "timeZone": "UTC"
                },
                "reminders": {
                    "useDefault": False,
                    "overrides": [
                        {"method": "popup", "minutes": 10}
                    ]
                }
            }

            # Create the event
            created_event = self.calendar_service.events().insert(
                calendarId='primary',
                body=event
            ).execute()

            return {
                "success": True,
                "event_id": created_event["id"],
                "html_link": created_event.get("htmlLink", ""),
                "message": f"Created calendar event: {summary}"
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create calendar event: {str(e)}"
            }

def get_study_plan(topic: str, learning_data: Dict, wellness_data: Dict = None) -> Dict[str, Any]:
    """Helper function to get study plan."""
    agent = ScheduleAgent()
    return agent.create_study_plan(topic, learning_data, wellness_data)
