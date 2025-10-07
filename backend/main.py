"""FastAPI application for the Student AI Assistant."""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import os
import aiofiles
import fitz  # PyMuPDF for PDF processing
import tempfile

try:
    from dotenv import load_dotenv
    load_dotenv('.env')  # Try current directory first
    # Also try backend directory
    import os
    if not os.getenv("GEMINI_API_KEY"):
        backend_env = os.path.join(os.path.dirname(__file__), '.env')
        load_dotenv(backend_env)
except ImportError:
    pass  # dotenv not available, will rely on system env vars

try:
    from .orchestrator import create_study_assistant
except ImportError:
    from orchestrator import create_study_assistant

app = FastAPI(
    title="Student AI Assistant",
    description="Multi-agent AI system for personalized student learning and wellness",
    version="1.0.0"
)

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class StudyRequest(BaseModel):
    user_input: str
    student_id: Optional[str] = "demo_student"

class StudyResponse(BaseModel):
    greeting: str
    study_plan: Dict[str, Any]
    learning_resources: Dict[str, Any]
    wellness_insights: Dict[str, Any]
    assessment: Dict[str, Any]
    motivational_support: Dict[str, Any]
    calendar_events: list
    metadata: Dict[str, Any]

class HealthCheckResponse(BaseModel):
    status: str
    message: str
    agents_available: list

# Global orchestrator instance
orchestrator = None

@app.on_event("startup")
async def startup_event():
    """Initialize the orchestrator on startup."""
    global orchestrator

    # Get Gemini API key from environment (preferred) or OpenAI as fallback
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    openai_api_key = os.getenv("OPENAI_API_KEY")

    print(f"DEBUG: GEMINI_API_KEY found: {gemini_api_key is not None}")
    print(f"DEBUG: OPENAI_API_KEY found: {openai_api_key is not None}")

    api_key = gemini_api_key or openai_api_key

    if not api_key:
        print("Warning: No API key found (GEMINI_API_KEY or OPENAI_API_KEY). Using demo mode with limited functionality.")
        api_key = "demo-key"  # Will use fallback responses

    if gemini_api_key:
        print("Using Google Gemini API for AI operations.")
    elif openai_api_key:
        print("Using OpenAI API for AI operations.")
    else:
        print("Using demo mode with mock responses.")

    try:
        orchestrator = create_study_assistant(api_key)
        print("Student AI Assistant orchestrator initialized successfully!")
    except Exception as e:
        print(f"Failed to initialize orchestrator: {e}")
        # Continue without orchestrator for health check

@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint."""
    agents_available = [
        "learning_agent",
        "schedule_agent",
        "wellness_agent",
        "assessment_agent",
        "personalization_agent",
        "motivation_agent",
        "orchestrator"
    ] if orchestrator else []

    return HealthCheckResponse(
        status="healthy" if orchestrator else "degraded",
        message="All systems operational" if orchestrator else "Orchestrator not initialized - check API key",
        agents_available=agents_available
    )

@app.post("/study-plan", response_model=StudyResponse)
async def create_study_plan(request: StudyRequest):
    """Create a personalized study plan using the multi-agent system."""
    if not orchestrator:
        raise HTTPException(
            status_code=503,
            detail="Study assistant is not available. Please check the API key configuration."
        )

    try:
        # Process the request through the orchestrator
        response = orchestrator.process_request(request.user_input, request.student_id)

        # Validate response structure
        required_keys = ["greeting", "study_plan", "learning_resources", "wellness_insights",
                        "assessment", "motivational_support", "calendar_events", "metadata"]

        for key in required_keys:
            if key not in response:
                response[key] = {} if key != "calendar_events" else []

        return StudyResponse(**response)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing study plan: {str(e)}")

@app.get("/demo")
async def demo_study_plan():
    """Demo endpoint with pre-configured ML exam preparation."""
    demo_request = StudyRequest(
        user_input="Help me prepare for my Machine Learning exam",
        student_id="demo_student"
    )
    return await create_study_plan(demo_request)

@app.get("/agents/status")
async def get_agents_status():
    """Get status of all agents."""
    if not orchestrator:
        return {"error": "Orchestrator not initialized"}

    # In a real implementation, you might check each agent individually
    return {
        "orchestrator": "active",
        "learning_agent": "active",
        "schedule_agent": "active",
        "wellness_agent": "active",
        "assessment_agent": "active",
        "personalization_agent": "active",
        "motivation_agent": "active"
    }

# Additional endpoints for future expansion
@app.post("/quiz/evaluate")
async def evaluate_quiz(quiz_data: Dict[str, Any]):
    """Evaluate quiz answers (future implementation)."""
    return {"message": "Quiz evaluation endpoint - coming soon!"}

@app.get("/wellness/today")
async def get_daily_wellness():
    """Get daily wellness recommendations (future implementation)."""
    return {"message": "Daily wellness endpoint - coming soon!"}

@app.get("/analytics/student/{student_id}")
async def get_student_analytics(student_id: str):
    """Get student analytics (future implementation)."""
    return {"message": f"Analytics for student {student_id} - coming soon!"}

@app.post("/study-plan-with-calendar")
async def create_study_plan_with_calendar(
    user_input: str,
    student_id: str = "demo_student",
    create_calendar_events: bool = False
):
    """Create a study plan and optionally add events to Google Calendar."""
    if not orchestrator:
        raise HTTPException(
            status_code=503,
            detail="Study assistant is not available. Please check the API key configuration."
        )

    try:
        # Process the request through the orchestrator
        response = orchestrator.process_request(user_input, student_id)

        # If calendar events are requested, create them via schedule agent
        if create_calendar_events:
            try:
                # Get the existing schedule agent and create Google Calendar events
                from agents.schedule_agent import ScheduleAgent
                schedule_agent = ScheduleAgent()

                if schedule_agent.calendar_service:
                    # Recreate the study plan with Google Calendar events
                    study_plan = schedule_agent.create_study_plan(
                        response["study_plan"]["topic"],
                        {"resources": response["learning_resources"]["resources"] or [], "difficulty": response["study_plan"].get("difficulty", "intermediate"), "estimated_time": response["learning_resources"]["estimated_time"]},
                        {"fatigue_level": response["wellness_insights"].get("fatigue_level", 0.3)},
                        create_google_events=True
                    )

                    response["google_calendar_result"] = study_plan.get("google_calendar_result")
                else:
                    response["google_calendar_result"] = {"success": False, "error": "Google Calendar API not configured"}

            except Exception as calendar_error:
                print(f"Calendar integration error: {calendar_error}")
                response["google_calendar_result"] = {"success": False, "error": str(calendar_error)}

        # Validate response structure
        required_keys = ["greeting", "study_plan", "learning_resources", "wellness_insights",
                        "assessment", "motivational_support", "calendar_events", "metadata"]

        for key in required_keys:
            if key not in response:
                response[key] = {} if key != "calendar_events" else []

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing study plan: {str(e)}")

@app.post("/study-plan-with-pdf")
async def create_study_plan_with_pdf(
    file: UploadFile = File(...),
    user_input: str = Form(...),
    student_id: str = Form("demo_student")
):
    """Create a personalized study plan using uploaded PDF/book content."""
    if not orchestrator:
        raise HTTPException(
            status_code=503,
            detail="Study assistant is not available. Please check the API key configuration."
        )

    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name

        # Extract text from PDF
        pdf_content = extract_pdf_text(temp_file_path)

        # Clean up temp file
        os.unlink(temp_file_path)

        # Create enhanced user input that includes PDF content
        enhanced_input = f"{user_input}\n\n[UPLOADED_BOOK_CONTENT]\n{pdf_content}\n[/UPLOADED_BOOK_CONTENT]"

        # Process through orchestrator with PDF context
        response = orchestrator.process_request(enhanced_input, student_id)

        # Add PDF metadata to response
        response["metadata"]["pdf_processed"] = True
        response["metadata"]["pdf_pages"] = len(pdf_content.split('\n\n'))
        response["metadata"]["pdf_filename"] = file.filename

        # Validate response structure
        required_keys = ["greeting", "study_plan", "learning_resources", "wellness_insights",
                        "assessment", "motivational_support", "calendar_events", "metadata"]

        for key in required_keys:
            if key not in response:
                response[key] = {} if key != "calendar_events" else []

        return StudyResponse(**response)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF study plan: {str(e)}")

def extract_pdf_text(file_path: str) -> str:
    """Extract text content from PDF file."""
    try:
        doc = fitz.open(file_path)
        text_content = []

        for page_num in range(doc.page_count):
            page = doc.load_page(page_num)
            text = page.get_text()

            # Add page separator
            if page_num > 0:
                text_content.append(f"\n--- Page {page_num} ---\n")
            text_content.append(text)

        doc.close()
        return "".join(text_content)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error extracting PDF text: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
