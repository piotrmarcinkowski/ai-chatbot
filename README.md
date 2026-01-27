# ai-chatbot
LangGraph-powered multi-agent general purpose AI chatbot.

## Architecture

The project consists of two main components:

1. **LangGraph Server** (Backend) - Runs the AI agent graph, exposed via REST API
2. **UI Clients** (Frontend) - Multiple interfaces to interact with the agent:
   - CLI client
   - Streamlit web interface

## Configuration

Create `.env` file in the project's root folder based on [env.example](env.example).

## Quick Start

### Quick Start / Development

For quick testing or development (uses `langgraph dev`, not production-grade):

```bash
docker compose -p ai-chatbot-prod up
```

⚠️ **This is NOT suitable for production** - it runs `langgraph dev` which is a development server.
⚠️ **Use the `-p ai-chatbot-prod` flag** to avoid conflicts with the dev container environment.

See [app/docs/deployment.md](app/docs/deployment.md) for production deployment instructions.

### UI Clients

Once the server is running, you can use any of the UI clients:

#### CLI Client

```bash
cd ui/cli
pip install -r requirements.txt
python chatbot_cli.py
```

#### Streamlit Web UI

```bash
cd ui/streamlit
pip install -r requirements.txt
streamlit run app.py
```

Access the web UI at `http://localhost:8501`

## Development (Dev Container)

This project supports development using VS Code's Dev Container.

### Prerequisites

- VS Code with `Dev Containers` extension

### Start Dev Container

1. Open Command Palette (Ctrl+Shift+P)
2. Select `Dev Containers: Reopen in Container`

### Start LangGraph Server in Dev Container

```bash
cd app/src
langgraph dev --host 0.0.0.0 --no-browser
```

Or use the `Run and Debug` tab → `LangGraph Dev` launch configuration.

Access LangGraph Studio: https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024

### Start UI Clients in Dev Container

After starting the LangGraph server, you can run UI clients:

#### CLI Client
```bash
cd ui/cli
python chatbot_cli.py
```

Or use `Run and Debug` → `CLI Debug (LangGraph SDK Client)`

#### Streamlit UI
```bash
cd ui/streamlit
streamlit run app.py
```

Or use `Run and Debug` → `Streamlit UI`

### Debugging

Available VS Code launch configurations:
- **LangGraph Dev** - Start LangGraph server with debugger
- **CLI Debug** - Start CLI client with debugger
- **Streamlit UI** - Start Streamlit with debugger

For manual debugging, start the server with:

```bash
langgraph dev --debug-port 5678 --wait-for-client --host 0.0.0.0 --no-browser
```

See [LangGraph debugging docs](https://docs.langchain.com/langgraph-platform/quick-start-studio#optional-attach-a-debugger)

## Troubleshooting

In case of issues with running Dev Container, inspect the log first.

See the following commands in the command palette (Crtl+Shift+P):

- Dev Containers: Show Previous Log
- Dev Containers: Show Container Log
- Dev Containers Developer: Show All Logs...

**Useful Docker Commands**
```
# Check container status
docker compose ps -a

# View container logs (last 100 lines)
docker compose logs ai-chatbot --tail=100

# Follow logs in real-time
docker compose logs -f ai-chatbot

# Check health status
docker inspect <container-name> --format='{{json .State.Health}}' | jq

# Execute commands inside container
docker exec ai-chatbot-dev-ai-chatbot-1 <command>

# Restart the container
docker compose restart ai-chatbot

# Rebuild and restart
docker compose up -d --build ai-chatbot
```

## Issues

All issues are stored in Github Issues. See more: [./app/docs/github-issues-extension.md](./app/docs/github-issues-extension.md)

