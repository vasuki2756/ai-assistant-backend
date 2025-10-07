"""MCP Server for tool context switching in the Student AI Assistant."""

import asyncio
import json
from typing import Any, Dict, List, Sequence
from mcp import Tool, types
from mcp.server import Server
from mcp.server.stdio import stdio_server

from .orchestrator import create_study_assistant

# Create MCP server
server = Server("student-ai-assistant")

# Global orchestrator
orchestrator = None

@server.list_tools()
async def handle_list_tools() -> List[types.Tool]:
    """List available tools."""
    return [
        types.Tool(
            name="create_study_plan",
            description="Create a personalized study plan using the multi-agent system",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_input": {
                        "type": "string",
                        "description": "The student's request (e.g., 'Help me prepare for my Machine Learning exam')"
                    },
                    "student_id": {
                        "type": "string",
                        "description": "Student identifier (optional, defaults to 'demo_student')",
                        "default": "demo_student"
                    }
                },
                "required": ["user_input"]
            }
        ),
        types.Tool(
            name="get_learning_resources",
            description="Get personalized learning resources for a specific topic",
            inputSchema={
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description": "The topic to find resources for"
                    },
                    "difficulty": {
                        "type": "string",
                        "enum": ["beginner", "intermediate", "advanced"],
                        "description": "Difficulty level preference",
                        "default": "intermediate"
                    }
                },
                "required": ["topic"]
            }
        ),
        types.Tool(
            name="assess_wellness",
            description="Assess student's current wellness state",
            inputSchema={
                "type": "object",
                "properties": {
                    "facial_data": {
                        "type": "object",
                        "description": "Facial analysis data (optional)",
                        "properties": {
                            "emotion": {"type": "string"},
                            "fatigue_indicators": {"type": "array", "items": {"type": "string"}}
                        }
                    },
                    "activity_data": {
                        "type": "object",
                        "description": "Physical activity data (optional)",
                        "properties": {
                            "steps_today": {"type": "number"},
                            "active_minutes": {"type": "number"},
                            "calories_burned": {"type": "number"}
                        }
                    }
                }
            }
        ),
        types.Tool(
            name="generate_quiz",
            description="Generate a quiz for assessing understanding",
            inputSchema={
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description": "Topic for the quiz"
                    },
                    "difficulty": {
                        "type": "string",
                        "enum": ["beginner", "intermediate", "advanced"],
                        "description": "Quiz difficulty level",
                        "default": "intermediate"
                    },
                    "num_questions": {
                        "type": "number",
                        "description": "Number of questions to generate",
                        "default": 5,
                        "minimum": 1,
                        "maximum": 10
                    }
                },
                "required": ["topic"]
            }
        ),
        types.Tool(
            name="create_schedule",
            description="Create a study schedule and calendar events",
            inputSchema={
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description": "Topic for the study schedule"
                    },
                    "learning_resources": {
                        "type": "object",
                        "description": "Learning resources data"
                    },
                    "wellness_data": {
                        "type": "object",
                        "description": "Wellness assessment data"
                    }
                },
                "required": ["topic"]
            }
        ),
        types.Tool(
            name="get_motivation",
            description="Generate motivational support and encouragement",
            inputSchema={
                "type": "object",
                "properties": {
                    "context": {
                        "type": "object",
                        "description": "Context for motivation (performance level, emotional state, etc.)",
                        "properties": {
                            "performance_level": {"type": "string"},
                            "emotional_state": {"type": "string"},
                            "fatigue_level": {"type": "number"},
                            "current_topic": {"type": "string"}
                        }
                    }
                },
                "required": ["context"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle tool calls."""
    global orchestrator

    if not orchestrator:
        return [types.TextContent(
            type="text",
            text="Error: Orchestrator not initialized. Please check API key configuration."
        )]

    try:
        if name == "create_study_plan":
            # Use the main orchestrator method
            result = orchestrator.process_request(
                arguments["user_input"],
                arguments.get("student_id", "demo_student")
            )
            return [types.TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]

        elif name == "get_learning_resources":
            from .agents.learning_agent import get_learning_resources
            result = get_learning_resources(arguments["topic"], "demo-key")  # API key handling needed
            return [types.TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]

        elif name == "assess_wellness":
            from .agents.wellness_agent import get_wellness_assessment
            result = get_wellness_assessment(
                arguments.get("facial_data"),
                arguments.get("activity_data")
            )
            return [types.TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]

        elif name == "generate_quiz":
            from .agents.assessment_agent import generate_quiz
            learning_data = {
                "resources": [],
                "difficulty": arguments.get("difficulty", "intermediate"),
                "estimated_time": "30 minutes"
            }
            result = generate_quiz(
                arguments["topic"],
                learning_data,
                arguments.get("num_questions", 5)
            )
            return [types.TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]

        elif name == "create_schedule":
            from .agents.schedule_agent import get_study_plan
            result = get_study_plan(
                arguments["topic"],
                arguments.get("learning_resources", {}),
                arguments.get("wellness_data", {})
            )
            return [types.TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]

        elif name == "get_motivation":
            from .agents.motivation_agent import get_motivational_support
            result = get_motivational_support(
                arguments["context"],
                "demo-key"
            )
            return [types.TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]

        else:
            return [types.TextContent(
                type="text",
                text=f"Unknown tool: {name}"
            )]

    except Exception as e:
        return [types.TextContent(
            type="text",
            text=f"Error executing tool {name}: {str(e)}"
        )]

@server.list_resources()
async def handle_list_resources() -> List[types.Resource]:
    """List available resources."""
    return [
        types.Resource(
            uri="student://study-plans",
            name="Study Plans",
            description="Collection of generated study plans",
            mimeType="application/json"
        ),
        types.Resource(
            uri="student://wellness-data",
            description="Student wellness monitoring data",
            mimeType="application/json"
        ),
        types.Resource(
            uri="student://learning-analytics",
            description="Learning progress and analytics",
            mimeType="application/json"
        )
    ]

@server.read_resource()
async def handle_read_resource(uri: str) -> str:
    """Read resource content."""
    # Mock resource content for demo
    if uri == "student://study-plans":
        return json.dumps({
            "plans": [
                {
                    "id": "ml_exam_prep",
                    "topic": "Machine Learning",
                    "created": "2025-01-07",
                    "status": "active"
                }
            ]
        }, indent=2)

    elif uri == "student://wellness-data":
        return json.dumps({
            "current_wellness": {
                "fatigue_level": 0.3,
                "stress_level": 0.2,
                "emotional_state": "focused",
                "last_updated": "2025-01-07T14:00:00Z"
            }
        }, indent=2)

    elif uri == "student://learning-analytics":
        return json.dumps({
            "analytics": {
                "topics_studied": ["Machine Learning", "Data Science", "Algorithms"],
                "average_score": 78.5,
                "study_streak": 5,
                "total_study_time": "24 hours"
            }
        }, indent=2)

    else:
        raise ValueError(f"Unknown resource: {uri}")

async def main():
    """Main entry point for MCP server."""
    import os

    # Initialize orchestrator
    global orchestrator
    api_key = os.getenv("OPENAI_API_KEY", "demo-key")

    try:
        orchestrator = create_study_assistant(api_key)
    except Exception as e:
        print(f"Warning: Could not initialize orchestrator: {e}")
        print("MCP server will run in limited mode")

    # Run the MCP server
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
