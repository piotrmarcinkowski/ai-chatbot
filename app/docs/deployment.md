# Deployment Architecture

## Overview

The AI Chatbot uses a **client-server architecture** with LangGraph server as the backend and multiple UI clients as frontends.

## Architecture Diagram

```
┌─────────────────────────────────────────┐
│  Docker Container: ai-chatbot           │
│  ┌───────────────────────────────────┐  │
│  │  LangGraph Server (FastAPI)       │  │
│  │  - Host port: LANGGRAPH_API_PORT  |  |
│  │  - Container port: 8000           │  │
│  │  - Exposes all graphs via REST    │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
           ▲
           │ HTTP/WebSocket (LangGraph SDK)
           │
┌──────────┴──────────────────────────────┐
│  UI Clients                             │
│  ├─ CLI (Python, local)                 │
│  ├─ Streamlit (Web, containerized)      │
│  ├─ Gradio (future)                     │
│  └─ Custom clients via SDK              │
└─────────────────────────────────────────┘
```

There are also database services (MongoDB, Postgres) running in separate containers as defined in `docker-compose.yml`.
These were not included in the diagram for simplicity.

## Components

✅ Dev Environment (default)
File: docker-compose.yml
Env file: .env
Target: ai-chatbot-dev stage
Port: LANGGRAPH_API_PORT (default 8123) → 8000
Command: langgraph dev --host 0.0.0.0 --port 8000 --no-browser --no-reload

✅ Devcontainer Environment
File: .devcontainer/docker-compose.devcontainer.yml
Env file: .devcontainer/.env
Target: ai-chatbot-devcontainer stage
Port: LANGGRAPH_API_PORT (default 2024) → 8000
Command: 'sleep infinity' (correct for devcontainer)

✅ Production Environment
File: docker-compose.yml
Env file: env/prod.env
Image: ai-chatbot-prod:latest (pre-built with langgraph build)
Port: LANGGRAPH_API_PORT (default 8124) → 8000
Includes: PostgreSQL, Redis, MongoDB

## Deployment Options

### Option 1: Docker Compose with langgraph dev (Current Setup - Recommended for Simple Production)

**How it works**: Uses `langgraph dev --no-reload` in a container. This works but is technically a development mode.

Start the LangGraph server:
```bash
docker compose up
```

Rebuild after changes:
```bash
docker compose build --no-cache
```

or simply:
```bash
docker compose up --build --no-cache
```

Then run UI clients separately:
```bash
# CLI
cd ui/cli && python chatbot_cli.py
```

It's also possible to connect to the server with LangGraph Studio:

```bash
ai-chatbot-1            | ╦  ┌─┐┌┐┌┌─┐╔═╗┬─┐┌─┐┌─┐┬ ┬
ai-chatbot-1            | ║  ├─┤││││ ┬║ ╦├┬┘├─┤├─┘├─┤
ai-chatbot-1            | ╩═╝┴ ┴┘└┘└─┘╚═╝┴└─┴ ┴┴  ┴ ┴
ai-chatbot-1            | 
ai-chatbot-1            | - 🚀 API: http://0.0.0.0:8123
ai-chatbot-1            | - 🎨 Studio UI: https://smith.langchain.com/studio/?baseUrl=http://0.0.0.0:8123
ai-chatbot-1            | - 📚 API Docs: http://0.0.0.0:8123/docs
```

> [!TIP]
> If the link in the logs does not work, access Studio at:
> `https://smith.langchain.com/studio/?baseUrl=http://localhost:8123`


**Pros**:
- ✅ Simple single command (`docker compose up`)
- ✅ Works without Docker-in-Docker
- ✅ Includes all dependencies in container
- ✅ Suitable for small-scale production
- ✅ Debuggable

**Cons**:
- ⚠️ Uses development mode (though `--no-reload` makes it stable)
- ⚠️ Not optimized for large-scale production

### Option 2: Use langgraph build (Recommended for Production)

**How it works**: The `langgraph build` command creates an optimized production Docker image based on the official `langchain/langgraph-api` base image.

**Using Makefile (Easiest)**

```bash
# Build production image and start all services
make up-prod

# Stop services
make down
```

**Manual steps**

```bash
# 1. Build production image using langgraph CLI
cd app/src
langgraph build -t ai-chatbot-prod:latest
cd ../..

# 2. Start services
docker compose -f docker-compose.prod.yml up
```

The server will be available at `http://localhost:8123`

**Note**: This uses the official `langchain/langgraph-api` production server via `langgraph build`, NOT a development server.

**Pros**:
- ✅ Official production-ready image
- ✅ Optimized performance
- ✅ Proper production server (uvicorn)
- ✅ No development dependencies

**Cons**:
- ⚠️ Requires two-step process (build, then run)
- ⚠️ Requires installing `langgraph-cli` on host

## Configuration

### Environment Variables

**LangGraph Server** (`app/.env`):
- `OPENAI_API_KEY`: OpenAI API key
- `TAVILY_API_KEY`: Tavily search API key
- `MONGODB_URI`: MongoDB connection string
- `LANGSMITH_API_KEY`: LangSmith API key (optional)

**UI Clients**:
- `LANGGRAPH_API_HOST`: Host URL of the LangGraph server (default: `http://127.0.0.1`)
- `LANGGRAPH_API_PORT`: Port of the LangGraph server (default: `8123`)

### Server URL by Environment

- **Production**: `http://localhost:8123` (or your domain)
- **Development**: `http://localhost:2024`
- **Dev Container**: `http://localhost:2024` (from host) or `http://ai-chatbot-dev:2024` (from another container)

## Health Checks

The LangGraph server provides health check endpoints:

```bash
# Production
curl http://localhost:8123/ok

# Development
curl http://localhost:2024/ok
```

Dockerfile health check:
```dockerfile
HEALTHCHECK CMD curl --fail http://localhost:8123/ok || exit 1
```

## Additional Resources

- [LangGraph Server Docs](https://langchain-ai.github.io/langgraph/cloud/)
- [LangGraph SDK](https://langchain-ai.github.io/langgraph/cloud/reference/sdk/python_sdk_ref/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
