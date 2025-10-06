# AI-Powered Fitness Backend with FastAPI \& LangGraph

This repository contains a backend application for generating personalized nutrition and workout plans powered by FastAPI and LangGraph workflows with integration of Google Gemini AI. It provides user authentication, profile and goal management, AI-driven plan generation, and a conversational chatbot.

***

## Features

- **User Registration and Authentication** with JWT tokens
- **User Profile and Fitness Goal Management**
- **AI-Generated Nutrition and Workout Plans**
- **Separate endpoints for Nutrition and Workout Plan generation**
- **Chatbot Assistant with contextual understanding**
- **Persistent data storage with SQLAlchemy**
- **Clean and parsed JSON output for generated plans**
- **Swagger UI for API exploration and testing**

***

## Getting Started

### Prerequisites

- Python 3.11+
- PostgreSQL or SQLite (default)
- Google Cloud API Key for Google Gemini AI
- Git


### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ai-fitness-backend.git
cd ai-fitness-backend
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Setup environment variables in a `.env` file with:
```
DATABASE_URL=sqlite:///./fitness_app.db
GOOGLE_API_KEY=your_google_api_key_here
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
APP_NAME=Fitness AI Backend
DEBUG=True
```

5. Initialize the database (for SQLite):
```bash
alembic upgrade head
```


***

## Running the Application

Start the FastAPI server with:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API docs are available at [http://localhost:8000/docs](http://localhost:8000/docs)

***

## API Overview

### Authentication

- `POST /api/users/register` — Register new user with email and password
- `POST /api/users/token` — Login to get JWT access token
- `GET /api/users/me` — Get current authenticated user


### User Management

- `POST /api/users/profile` — Create or update user profile (height, weight, age, gender, activity level)
- `POST /api/users/goals` — Create or update user fitness goals (goal type, target weight, target days, notes)


### Plan Generation

- `POST /api/fitness/generate-nutrition-plan` — Generate personalized nutrition plan (clean JSON output)
- `POST /api/fitness/generate-workout-plan` — Generate personalized workout plan (requires nutrition plan completed)


### Chatbot

- `POST /api/chat/chat` — Chat with AI assistant with personalized context
- `GET /api/chat/history` — Retrieve chat history

***

## Project Structure

```
app/
├── main.py              # Application entrypoint
├── models/              # Database & Pydantic models
├── core/                # Config, DB connection, LangGraph workflow
├── api/                 # API route modules & dependencies
├── utils/               # Helper functions e.g., plan text parsing
└── requirements.txt
```


***

## Development \& Testing

- Use `pytest` for unit and integration tests.
- Run tests with:

```bash
pytest tests/
```

- Use Swagger UI or Postman for manual API testing.

***

## Contributing

Contributions and suggestions are welcome! Please open issues or pull requests as needed.

***

## License

MIT License

***

## Acknowledgements

- [FastAPI](https://fastapi.tiangolo.com/)
- [LangGraph](https://github.com/langgraph/langgraph)
- [Google Gemini AI](https://cloud.google.com/vertex-ai)
- [SQLAlchemy](https://www.sqlalchemy.org/)

***

This backend powers scalable AI fitness applications with modern, clean architecture and production-ready features.

