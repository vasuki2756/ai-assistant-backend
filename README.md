# Student AI Assistant

A multi-agent AI ecosystem that provides personalized learning resources, schedules study breaks, and supports overall student wellness.

## Features

✨ **Multi-Agent Architecture**: 6 specialized agents working together via LangGraph orchestration
📚 **Personalized Learning**: Learning paths adapted to your style and needs
🏃‍♂️ **Wellness Monitoring**: Fatigue and stress detection with recommendations
📅 **Smart Scheduling**: AI-powered study plans with wellness breaks
🧠 **Assessment Generation**: Custom quizzes based on learning materials
💪 **Motivational Support**: Emotional encouragement and goal setting
🔧 **MCP Integration**: Tool context switching via Model Context Protocol

## Agents

### 🤖 Orchestrator Agent
- **Role**: Coordinates all agents using LangGraph
- **Tech**: LangGraph state management, conversation routing

### 📖 Learning Resource Agent
- **Role**: Recommends high-quality learning materials
- **Sources**: GeeksforGeeks, YouTube, Google Scholar, academic papers
- **Tech**: Content analysis, platform integration

### 📅 Schedule Agent
- **Role**: Creates personalized study plans
- **Features**: Calendar integration, adaptive scheduling
- **Tech**: Google Calendar API, intelligent time allocation

### 🌿 Wellness Agent
- **Role**: Monitors and supports student wellness
- **Capabilities**: Facial emotion detection, activity monitoring
- **Tech**: Hume AI integration, Google Fit data

### 📝 Assessment Agent
- **Role**: Generates and evaluates quizzes
- **Features**: Adaptive difficulty, performance analysis
- **Tech**: NotebookLM integration, NLP assessment

### 🎯 Personalization Agent
- **Role**: Adapts learning experiences
- **Data**: BigQuery analytics, Firebase preferences, Vertex AI models
- **Tech**: Machine learning personalization

### 💪 Motivation Agent
- **Role**: Provides emotional support and engagement
- **Features**: Daily affirmations, progress celebrations
- **Tech**: Gemini API for conversational motivation

## Tech Stack

- **Backend**: Python, FastAPI, LangGraph, OpenAI GPT
- **Frontend**: React, TypeScript, Material-UI
- **Multi-Agent**: 6 specialized agents with LangGraph orchestration
- **APIs**: OpenAI, Google Workspace, Hume AI, NotebookLM
- **Infrastructure**: Google Cloud Run, BigQuery, Firebase

## Demo Example

**Student Input**: "Help me prepare for my Machine Learning exam"

**Multi-Agent Coordination**:
1. **Personalization Agent** → Analyzes learning profile (visual learner, moderate pace)
2. **Learning Agent** → Finds ML resources (YouTube courses, GeeksforGeeks articles)
3. **Wellness Agent** → Detects fatigue level (0.3 - moderate)
4. **Assessment Agent** → Generates ML quiz questions
5. **Schedule Agent** → Creates 2-day study plan with breaks
6. **Motivation Agent** → Provides encouragement message

**Output**:
```
✅ Your 2-day personalized ML prep plan:
Day 1: Learn SVM (GeeksforGeeks + YouTube video)
Day 2: Practice PCA Quiz (NotebookLM assessment)
Wellness break scheduled after 50 minutes.
Motivation: "You're building incredible knowledge! Keep going! 💪"
```

## Setup

### Prerequisites
- Python 3.8+
- Node.js 16+
- OpenAI API Key
- Google Cloud credentials (for full integration)

### Backend Setup
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
export OPENAI_API_KEY="your-key-here"
python -m uvicorn main:app --reload
```

### Frontend Setup
```bash
cd frontend
npm install
npm start
```

### Environment Variables
```bash
OPENAI_API_KEY=your_openai_key
GOOGLE_CLOUD_PROJECT=your_project_id
HUME_API_KEY=your_hume_key
```

## API Endpoints

- `GET /health` - Health check
- `POST /study-plan` - Create personalized study plan
- `GET /demo` - Demo ML exam preparation
- `GET /agents/status` - Agent status overview

## Architecture

```
┌─────────────────┐    ┌──────────────────┐
│   Student UI    │    │   FastAPI        │
│   (React)       │◄──►│   Backend        │
└─────────────────┘    └──────────────────┘
                              │
                    ┌─────────▼─────────┐
                    │   LangGraph       │
                    │  Orchestrator     │
                    └─────────┬─────────┘
                              │
           ┌──────────────────┼──────────────────┐
           │                  │                  │
    ┌──────▼─────┐     ┌──────▼─────┐     ┌──────▼─────┐
    │ Learning   │     │ Schedule   │     │ Wellness   │
    │ Agent      │     │ Agent      │     │ Agent      │
    └──────┬─────┘     └──────┬─────┘     └──────┬─────┘
           │                  │                  │
    ┌──────▼─────┐     ┌──────▼─────┐     ┌──────▼─────┐
    │ Assessment │     │Personaliza-│     │ Motivation │
    │ Agent      │     │tion Agent  │     │ Agent      │
    └────────────┘     └────────────┘     └────────────┘
```

## Features in Development

- [ ] Real Google Calendar integration
- [ ] Hume AI facial emotion detection
- [ ] NotebookLM quiz generation
- [ ] BigQuery analytics dashboard
- [ ] Firebase real-time sync
- [ ] Voice-based motivation (Gemini)

## Contributing

This is a demonstration of multi-agent AI architecture for educational purposes. The current implementation uses simulated data for external APIs.

## License

Educational demonstration project - not for production use without proper API integrations.
