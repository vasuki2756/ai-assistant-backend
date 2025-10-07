"""Orchestrator Agent - Coordinates all agents using LangGraph for multi-agent conversations."""

from typing import Dict, List, Any, Annotated, TypedDict
from langgraph.graph import StateGraph, START, END
import google.generativeai as genai
import json

# Import all agents
from .agents.learning_agent import get_learning_resources
from .agents.schedule_agent import get_study_plan
from .agents.wellness_agent import get_wellness_assessment
from .agents.assessment_agent import generate_quiz
from .agents.personalization_agent import get_personalized_path
from .agents.motivation_agent import get_motivational_support

class OrchestratorState(TypedDict):
    """State for the orchestrator graph."""
    user_input: str
    topic: str
    student_id: str
    conversation_history: List[Dict[str, Any]]
    current_step: str
    agent_outputs: Dict[str, Any]
    final_response: Dict[str, Any]
    metadata: Dict[str, Any]

class StudentAOrchestrator:
    """Main orchestrator using LangGraph for multi-agent coordination."""

    def __init__(self, gemini_api_key: str):
        genai.configure(api_key=gemini_api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')

        # Build the LangGraph
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph state machine."""
        graph = StateGraph(OrchestratorState)

        # Add nodes (agent functions)
        graph.add_node("analyze_input", self._analyze_user_input)
        graph.add_node("personalization_agent", self._run_personalization_agent)
        graph.add_node("learning_agent", self._run_learning_agent)
        graph.add_node("wellness_agent", self._run_wellness_agent)
        graph.add_node("assessment_agent", self._run_assessment_agent)
        graph.add_node("schedule_agent", self._run_schedule_agent)
        graph.add_node("motivation_agent", self._run_motivation_agent)
        graph.add_node("coordinate_response", self._coordinate_final_response)

        # Define the flow
        graph.add_edge(START, "analyze_input")

        # Branching logic - analyze input determines which agents to run
        graph.add_conditional_edges(
            "analyze_input",
            self._route_to_agents,
            {
                "personalization_first": "personalization_agent",
                "learning_focused": "learning_agent",
                "comprehensive_study": "personalization_agent"
            }
        )

        # Agent processing flow
        graph.add_edge("personalization_agent", "learning_agent")
        graph.add_edge("personalization_agent", "wellness_agent")
        graph.add_edge("learning_agent", "assessment_agent")
        graph.add_edge("wellness_agent", "schedule_agent")
        graph.add_edge("assessment_agent", "motivation_agent")
        graph.add_edge("schedule_agent", "motivation_agent")
        graph.add_edge("motivation_agent", "coordinate_response")
        graph.add_edge("coordinate_response", END)

        return graph.compile()

    def _extract_topic(self, user_input: str) -> str:
        """Extract topic from user input."""
        # Simple extraction - can be improved with LLM
        cleaned_input = user_input.lower().replace("help me prepare for my", "").replace("help me with", "").strip()
        return cleaned_input

    def process_request(self, user_input: str, student_id: str = "demo_student") -> Dict[str, Any]:
        """Process a student request through the multi-agent system using sequential workflow."""
        # Extract topic from input
        topic = self._extract_topic(user_input)

        # Get actual wellness assessment
        facial_data = {
            "emotion": "focused",
            "fatigue_indicators": []
        }
        activity_data = {
            "steps_today": 8500,
            "active_minutes": 75,
            "calories_burned": 2100
        }
        wellness_assessment = get_wellness_assessment(facial_data, activity_data)

        # Get personalized path (this uses mock data currently)
        past_performance = [
            {"score": 75, "topic": "mathematics", "date": "2025-01-01"},
            {"score": 82, "topic": "programming", "date": "2025-01-03"},
            {"score": 68, "topic": "algorithms", "date": "2025-01-05"}
        ]
        learning_resources_mock = {
            "resources": [{"title": "Placeholder", "platform": "Demo"}],
            "difficulty": "intermediate",
            "estimated_time": "2 hours"
        }
        personalized_path = get_personalized_path(
            topic=topic,
            learning_resources=learning_resources_mock,
            wellness_assessment=wellness_assessment,
            student_id=student_id,
            past_performance=past_performance
        )

        # Now get actual learning resources (this calls Gemini)
        pdf_content = None
        learning_resources = get_learning_resources(topic, None, pdf_content)

        # Generate quiz (this calls Gemini)
        quiz = generate_quiz(topic, learning_resources, num_questions=3, api_key=None)

        # Create study plan
        study_plan = get_study_plan(topic, learning_resources, wellness_assessment)

        # Get motivational support (this uses logic, not LLM directly)
        motivation_context = {
            "performance_level": "good_performance",
            "emotional_state": wellness_assessment["emotional_state"],
            "fatigue_level": wellness_assessment["fatigue_level"],
            "progress_milestone": True,
            "current_topic": topic
        }
        motivation = get_motivational_support(motivation_context, None)

        # Format comprehensive response
        return {
            "greeting": "Here's your personalized study plan! 📚",
            "study_plan": {
                "topic": topic,
                "duration": study_plan.get("total_duration", "2 hours"),
                "difficulty": learning_resources.get("difficulty", "intermediate"),
                "sessions": study_plan.get("sessions", [])
            },
            "learning_resources": {
                "resources": learning_resources.get("resources", []),
                "estimated_time": learning_resources.get("estimated_time", "2 hours")
            },
            "wellness_insights": {
                "fatigue_level": wellness_assessment.get("fatigue_level", 0.3),
                "emotional_state": wellness_assessment.get("emotional_state", "focused"),
                "recommendations": wellness_assessment.get("recommendations", [])[:2]
            },
            "assessment": {
                "available_quiz": bool(quiz.get("questions")),
                "question_count": len(quiz.get("questions", [])),
                "estimated_time": quiz.get("estimated_time", "3 minutes")
            },
            "motivational_support": {
                "primary_message": motivation.get("primary_message", "You've got this!"),
                "next_goal": motivation.get("next_goal", {}).get("goal", "Complete your first study session")
            },
            "calendar_events": study_plan.get("calendar_events", []),
            "metadata": {
                "generated_at": "2025-01-07T14:00:00Z",
                "session_id": f"session_{student_id}_{hash(user_input) % 10000}"
            }
        }

    def _analyze_user_input(self, state: OrchestratorState) -> OrchestratorState:
        """Analyze user input to extract topic and determine processing strategy."""
        user_input = state["user_input"]

        # Check for PDF content
        pdf_content = None
        has_pdf = False
        if "[UPLOADED_BOOK_CONTENT]" in user_input and "[/UPLOADED_BOOK_CONTENT]" in user_input:
            has_pdf = True
            # Extract PDF content
            start_marker = "[UPLOADED_BOOK_CONTENT]"
            end_marker = "[/UPLOADED_BOOK_CONTENT]"
            start_idx = user_input.find(start_marker) + len(start_marker)
            end_idx = user_input.find(end_marker)
            pdf_content = user_input[start_idx:end_idx].strip()

            # Remove PDF content from user input for analysis
            user_input = user_input.replace(user_input[start_idx-len(start_marker):end_idx+len(end_marker)], "").strip()

        prompt = f"""Analyze the student's request to extract key information.

Return a JSON object with these exact keys:
- topic: main subject they want to study
- intent: "study_planning", "resource_finding", "assessment", "general_help"
- complexity: "simple", "moderate", "complex"
- has_time_constraint: boolean
- needs_personalization: boolean
- has_uploaded_content: boolean

Student request: {user_input}

Return ONLY the JSON object, no other text."""

        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,
                    max_output_tokens=300
                )
            )

            content = response.text
            if content:
                # Clean content if needed
                content = content.strip()
                if content.startswith('```json'):
                    content = content[7:]
                if content.endswith('```'):
                    content = content[:-3]
                content = content.strip()

                analysis = json.loads(content)
            else:
                raise ValueError("Empty response from Gemini")
        except:
            # Fallback analysis
            analysis = {
                "topic": user_input.replace("Help me prepare for my", "").replace("Help me with", "").strip(),
                "intent": "study_planning",
                "complexity": "moderate",
                "has_time_constraint": False,
                "needs_personalization": True,
                "has_uploaded_content": has_pdf
            }

        state["topic"] = analysis.get("topic", "general studies")
        state["metadata"]["analysis"] = analysis
        state["metadata"]["has_pdf"] = has_pdf

        if has_pdf and pdf_content:
            state["metadata"]["pdf_content_preview"] = pdf_content[:1000] + "..." if len(pdf_content) > 1000 else pdf_content
            # Store PDF content for agents to use
            state["agent_outputs"]["pdf_content"] = pdf_content

        return state

    def _run_personalization_agent(self, state: OrchestratorState) -> OrchestratorState:
        """Run personalization agent to understand student profile."""
        # Mock past performance for demo
        past_performance = [
            {"score": 75, "topic": "mathematics", "date": "2025-01-01"},
            {"score": 82, "topic": "programming", "date": "2025-01-03"},
            {"score": 68, "topic": "algorithms", "date": "2025-01-05"}
        ]

        # Mock initial learning resources (will be populated by learning agent)
        learning_resources = {
            "resources": [{"title": "Placeholder", "platform": "Demo"}],
            "difficulty": "intermediate",
            "estimated_time": "2 hours"
        }

        # Mock wellness data (will be populated by wellness agent)
        wellness_assessment = {
            "fatigue_level": 0.3,
            "stress_level": 0.2,
            "emotional_state": "focused"
        }

        personalized_path = get_personalized_path(
            topic=state["topic"],
            learning_resources=learning_resources,
            wellness_assessment=wellness_assessment,
            student_id=state["student_id"],
            past_performance=past_performance
        )

        state["agent_outputs"]["personalization"] = personalized_path
        return state

    def _run_learning_agent(self, state: OrchestratorState) -> OrchestratorState:
        """Run learning resource agent."""
        topic = state["topic"]

        # Check for PDF content
        pdf_content = state["agent_outputs"].get("pdf_content")

        # Get personalized preferences if available
        personalization_data = state["agent_outputs"].get("personalization", {})
        preferred_platforms = []

        if personalization_data:
            profile = personalization_data.get("student_profile", {})
            learning_style = profile.get("learning_style", "visual")
            if learning_style == "visual":
                preferred_platforms = ["YouTube", "GeeksforGeeks"]
            elif learning_style == "auditory":
                preferred_platforms = ["YouTube", "podcasts"]

        learning_resources = get_learning_resources(topic, None, pdf_content)
        state["agent_outputs"]["learning"] = learning_resources

        return state

    def _run_wellness_agent(self, state: OrchestratorState) -> OrchestratorState:
        """Run wellness assessment agent."""
        # Mock wellness data - in real implementation would come from sensors
        facial_data = {
            "emotion": "focused",
            "fatigue_indicators": []
        }

        activity_data = {
            "steps_today": 8500,
            "active_minutes": 75,
            "calories_burned": 2100
        }

        wellness_assessment = get_wellness_assessment(facial_data, activity_data)
        state["agent_outputs"]["wellness"] = wellness_assessment

        return state

    def _run_assessment_agent(self, state: OrchestratorState) -> OrchestratorState:
        """Run assessment agent to generate quiz."""
        learning_data = state["agent_outputs"].get("learning", {
            "resources": [],
            "difficulty": "intermediate",
            "estimated_time": "2 hours"
        })

        quiz = generate_quiz(state["topic"], learning_data, num_questions=3, api_key=None)
        state["agent_outputs"]["assessment"] = quiz

        return state

    def _run_schedule_agent(self, state: OrchestratorState) -> OrchestratorState:
        """Run schedule agent to create study plan."""
        learning_data = state["agent_outputs"].get("learning", {})
        wellness_data = state["agent_outputs"].get("wellness", {})

        study_plan = get_study_plan(state["topic"], learning_data, wellness_data)
        state["agent_outputs"]["schedule"] = study_plan

        return state

    def _run_motivation_agent(self, state: OrchestratorState) -> OrchestratorState:
        """Run motivation agent to provide encouragement."""
        # Gather context from other agents
        context = {
            "performance_level": "good_performance",  # Default for new session
            "emotional_state": state["agent_outputs"].get("wellness", {}).get("emotional_state", "neutral"),
            "fatigue_level": state["agent_outputs"].get("wellness", {}).get("fatigue_level", 0.3),
            "progress_milestone": True,  # Starting a new study plan is a milestone
            "current_topic": state["topic"]
        }

        motivational_support = get_motivational_support(context, None)
        state["agent_outputs"]["motivation"] = motivational_support

        return state

    def _route_to_agents(self, state: OrchestratorState) -> str:
        """Route to appropriate agent sequence based on analysis."""
        analysis = state["metadata"].get("analysis", {})
        intent = analysis.get("intent", "study_planning")
        needs_personalization = analysis.get("needs_personalization", True)

        if needs_personalization and intent in ["study_planning", "comprehensive_study"]:
            return "comprehensive_study"
        elif intent == "resource_finding":
            return "learning_focused"
        else:
            return "personalization_first"

    def _coordinate_final_response(self, state: OrchestratorState) -> OrchestratorState:
        """Coordinate and format the final response for the user."""
        agent_outputs = state["agent_outputs"]

        # Build comprehensive response
        study_plan = agent_outputs.get("schedule", {}).get("study_plan", {})
        learning_resources = agent_outputs.get("learning", {})
        wellness_info = agent_outputs.get("wellness", {})
        quiz = agent_outputs.get("assessment", {})
        motivation = agent_outputs.get("motivation", {})

        final_response = {
            "greeting": "Here's your personalized study plan! 📚",
            "study_plan": {
                "topic": study_plan.get("topic", state["topic"]),
                "duration": study_plan.get("total_duration", "2 hours"),
                "difficulty": study_plan.get("difficulty", "intermediate"),
                "sessions": study_plan.get("sessions", [])
            },
            "learning_resources": {
                "resources": learning_resources.get("resources", []),
                "estimated_time": learning_resources.get("estimated_time", "2 hours")
            },
            "wellness_insights": {
                "fatigue_level": wellness_info.get("fatigue_level", 0.3),
                "emotional_state": wellness_info.get("emotional_state", "focused"),
                "recommendations": wellness_info.get("recommendations", [])[:2]  # Top 2
            },
            "assessment": {
                "available_quiz": bool(quiz.get("questions")),
                "question_count": len(quiz.get("questions", [])),
                "estimated_time": quiz.get("estimated_time", "3 minutes")
            },
            "motivational_support": {
                "primary_message": motivation.get("primary_message", "You've got this!"),
                "next_goal": motivation.get("next_goal", {}).get("goal", "Complete your first study session")
            },
            "calendar_events": agent_outputs.get("schedule", {}).get("calendar_events", []),
            "metadata": {
                "generated_at": "2025-01-07T14:00:00Z",
                "session_id": state["metadata"]["session_id"]
            }
        }

        state["final_response"] = final_response
        return state

def create_study_assistant(api_key: str) -> StudentAOrchestrator:
    """Factory function to create the orchestrator."""
    return StudentAOrchestrator(api_key)
