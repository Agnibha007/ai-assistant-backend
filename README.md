# AI Desktop Assistant - Core API

The central orchestration engine for the AI Desktop Assistant. Built with FastAPI and Python.

## 🚀 Features

- **Agent Orchestration**: Managed via LangGraph to break down complex natural language requests into actionable steps.
- **Task Management**: Asynchronous task execution using Celery and Redis.
- **Authentication**: JWT-based secure authentication.
- **Real-time Feedback**: WebSocket integration for streaming execution status back to the UI.
- **Vector Memory**: Context-aware memory storage using ChromaDB.

## 🛠️ Technology Stack

- **Framework**: [FastAPI](https://fastapi.tiangolo.com/)
- **Database**: [PostgreSQL](https://www.postgresql.org/) with [SQLAlchemy](https://www.sqlalchemy.org/)
- **Background Tasks**: [Celery](https://docs.celeryq.dev/) & [Redis](https://redis.io/)
- **AI/LLM**: [LangGraph](https://www.langchain.com/langgraph) & [LangChain](https://www.langchain.com/)
- **Vector DB**: [ChromaDB](https://www.trychroma.com/)

## 🚦 Getting Started

### Prerequisites

- Python 3.11+
- Docker & Docker Compose (for infrastructure)

### Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file based on `.env.example`:

```env
DATABASE_URL=postgresql://user:password@localhost/dbname
REDIS_URL=redis://localhost:6379/0
OPENAI_API_KEY=your_key_here
SECRET_KEY=your_secret_key
```

### Development

```bash
# Run the API
python main.py

# Run Celery worker
celery -A worker.celery_app worker --loglevel=info
```

## 🧪 Testing & Quality

```bash
# Linting
ruff check .

# Type checking
mypy .

# Tests
pytest
```

## 📄 Production Deployment

This application is designed to be hosted on **Render** as a Web Service (API) and Background Worker (Celery). Infrastructure like PostgreSQL and Redis can be provisioned as managed services on Render.
