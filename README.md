# AI-Powered Fitness Application

> Transform fitness goals into personalized, intelligent plans powered by AI

---

## 🌟 Real-World Impact

This AI-Powered Fitness Application addresses critical challenges in the fitness industry:

- **Democratizing Personal Training**: Makes professional-grade fitness guidance accessible to everyone, regardless of budget. Millions of people cannot afford personal trainers; this application bridges that gap.

- **Personalized Health Solutions**: Moves beyond generic workout templates by generating truly personalized nutrition and workout plans based on individual metrics, goals, and preferences using advanced AI reasoning.

- **Behavioral Change at Scale**: Incorporates streak tracking, progress logging, and AI-driven feedback to help users build sustainable fitness habits. Research shows accountability and tracking increase adherence by 65%.

- **Accessibility & Inclusivity**: Eliminates barriers for underserved populations including people with disabilities, remote communities, and those in resource-limited settings.

- **Data-Driven Optimization**: Continuously learns from user feedback to refine plan recommendations, creating a virtuous cycle of improved outcomes.

- **Mental Health Benefits**: Combines fitness guidance with conversational AI support to address motivation, mental resilience, and holistic wellness—not just physical metrics.

**Potential Impact**: With this platform, we can reach millions of fitness enthusiasts worldwide and help them achieve their health goals while reducing healthcare costs through preventive fitness.

---

## 🛠 Tech Stack & Frameworks

### Backend Framework
- **FastAPI** (v0.104+) - Modern async Python web framework with automatic API documentation
- **Uvicorn** - ASGI server for running FastAPI applications

### Database & ORM
- **PostgreSQL** - Production-grade relational database (with fallback to SQLite)
- **SQLAlchemy** - Python SQL toolkit and ORM for database operations
- **Alembic** - Database migration management tool

### AI & LLM
- **LangGraph** - Multi-agent orchestration framework for building stateful AI workflows
- **LangChain** - Framework for developing LLM applications
- **Google Gemini API** (gemini-2.5-flash) - Advanced language model for intelligent plan generation

### Authentication & Security
- **python-jose** - JWT token generation and validation
- **passlib** + **argon2** - Password hashing and verification
- **pydantic** - Data validation and settings management

### Async & Queue Management
- **Celery** - Distributed task queue for async job processing
- **Redis** - In-memory data store for caching and message brokering

### Data Validation
- **Pydantic** - Data validation using Python type hints
- **pydantic-settings** - Configuration management from environment variables

### Containerization
- **Docker** - Container runtime
- **Docker Compose** - Multi-container orchestration

### Development Tools
- **python-multipart** - Multipart form data support
- **python-dotenv** - Environment variable loading

---

## 🏗 Architecture Overview

### Request Flow Diagram

```mermaid
sequenceDiagram
    actor User
    participant Client
    participant FastAPI
    participant Auth
    participant LangGraph
    participant LLM
    participant Database
    
    User->>Client: Enter fitness data & goal
    Client->>FastAPI: POST /api/fitness/generate-nutrition-plan
    
    FastAPI->>Auth: Verify JWT Token
    Auth-->>FastAPI: ✓ User authenticated
    
    FastAPI->>Database: Get user profile & goals
    Database-->>FastAPI: User data
    
    FastAPI->>LangGraph: Initialize workflow state
    
    LangGraph->>LangGraph: Calculate BMR & Calories
    LangGraph->>LangGraph: Create nutritional framework
    
    LangGraph->>LLM: Generate detailed nutrition plan
    LLM-->>LangGraph: Parsed meal plan + macros
    
    LangGraph->>LangGraph: Validate output structure
    
    FastAPI->>Database: Store nutrition plan
    Database-->>FastAPI: Plan saved (ID: X)
    
    FastAPI-->>Client: Return plan (JSON)
    Client-->>User: Display personalized plan
```

---

## 🔄 Core Architecture Methods

### 1. **LangGraph State Machine Pattern**
The application uses LangGraph's state-based workflow to manage complex AI generation processes:

```
Initial State → BMR Calculation → Calorie Estimation → Plan Generation → Validation → Final State
```

- **State Management**: All user data is stored in a typed `FitnessAppState` dictionary
- **Nodes**: Each workflow step (BMR calc, plan gen, etc.) is a discrete node
- **Edges**: Conditional routing determines next steps based on calculations
- **Memory**: MemorySaver checkpoint system persists conversation context

### 2. **JWT Authentication Layer**
Stateless authentication for distributed systems:

```
Client Credentials → Validate → Generate JWT Token → Return to Client → Client includes in headers → Verify on each request
```

- Token expiry: 30 minutes (configurable)
- Algorithm: HS256
- Secure password hashing with Argon2

### 3. **Async Task Processing with Celery**
Long-running operations (plan generation) run asynchronously:

```
HTTP Request → Task Queue (Redis) → Celery Worker → Process AI Generation → Update Database → Client polls status
```

### 4. **Rate Limiting**
Prevent abuse with token bucket algorithm:
- **20 requests per minute** for chat endpoint
- Stored in Redis for distributed rate limiting

### 5. **Database Transaction Management**
- SQLAlchemy session management for ACID compliance
- Automatic cascade deletion for related records
- Timestamp tracking (created_at, updated_at)

---

## 🖼 Screenshots Section

![Login and Profile Setup](screenshots/t1.png)

![AI Plan Generation](screenshots/t2.png)

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- PostgreSQL 15+ (or SQLite for development)
- Redis 7+ (optional, for production features)
- Google Gemini API Key
- Git

### Installation

1. **Clone the repository**:
```bash
git clone https://github.com/yourusername/ai-workout-application.git
cd ai-workout-application
```

2. **Create and activate virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate     # Windows
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Configure environment variables** (`.env`):
```env
# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/fitness_db
REDIS_URL=redis://localhost:6379/0

# Google AI
GOOGLE_API_KEY=your_google_gemini_api_key_here

# JWT Security
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# App Config
APP_NAME=AI Fitness Assistant
DEBUG=True
```

5. **Initialize database**:
```bash
alembic upgrade head
```

### Quick Start

#### Option 1: Docker Compose (Recommended)
```bash
docker-compose up --build
```

The API will be available at `http://localhost:8000`

#### Option 2: Local Development
```bash
# Terminal 1: Start FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Start Celery worker (optional)
celery -A app.worker worker --loglevel=info
```

---

## 📚 API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/users/register` | Register new user |
| POST | `/api/users/token` | Login and get JWT token |
| GET | `/api/users/me` | Get current user info |

### User Profile & Goals
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/users/profile` | Create/update user profile |
| GET | `/api/users/profile` | Get user profile |
| POST | `/api/users/goals` | Create/update fitness goals |
| GET | `/api/users/goals` | Get fitness goals |

### AI Plan Generation
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/fitness/generate-nutrition-plan` | Generate personalized nutrition plan |
| POST | `/api/fitness/generate-workout-plan` | Generate personalized workout plan |
| GET | `/api/fitness/plans` | Get user's generated plans |

### Chat & Interaction
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/chat/chat` | Send message to AI assistant |
| GET | `/api/chat/history` | Get chat history |

### Progress Tracking
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/tracking/daily-log` | Log daily workout |
| POST | `/api/tracking/body-metrics` | Log body measurements |
| GET | `/api/tracking/progress` | Get progress statistics |
| GET | `/api/tracking/streak` | Get current streak info |

### Feedback
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/feedback/rate-plan` | Rate a generated plan |
| GET | `/api/feedback/history` | Get feedback history |

---

## 🧪 Testing

Run tests with pytest:
```bash
pytest tests/ -v --cov=app
```

---

## 📖 Key Features Explained

### 🤖 AI-Powered Plan Generation
- **LangGraph Orchestration**: Multi-step workflows for plan generation
- **Gemini Integration**: Uses Google's latest LLM for intelligent recommendations
- **Contextual Understanding**: Considers user history, preferences, and feedback
- **Structured Output**: Guarantees valid JSON plan format

### 💬 Conversational AI Assistant
- **Context Awareness**: Maintains conversation history and user profile context
- **Rate Limited**: 20 requests/minute to prevent abuse
- **Real-time**: Streams responses for better UX
- **Feedback Loop**: Learn from user interactions

### 📊 Progress Tracking
- **Daily Activity Logs**: Track completed exercises and workouts
- **Body Metrics**: Log weight, body fat percentage, and other metrics
- **Streak System**: Gamification with current and longest streaks
- **Statistics**: View progress over time with calculated insights

### 🔐 Security
- **JWT Authentication**: Stateless and distributed-system friendly
- **Password Hashing**: Argon2 for secure password storage
- **CORS Enabled**: Controlled cross-origin requests
- **Rate Limiting**: Prevent API abuse and ensure fair usage

---


## 🔄 Development Workflow

1. **Create Feature Branch**:
```bash
git checkout -b feature/your-feature-name
```

2. **Make Changes**:
   - Follow PEP 8 style guide
   - Add type hints to functions
   - Write docstrings for complex logic

3. **Test Locally**:
```bash
docker-compose up
# Test API endpoints at http://localhost:8000/docs
```

4. **Commit & Push**:
```bash
git add .
git commit -m "feat: descriptive commit message"
git push origin feature/your-feature-name
```

5. **Create Pull Request** on GitHub

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new features
5. Submit a pull request


---



