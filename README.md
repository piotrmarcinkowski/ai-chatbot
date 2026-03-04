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
docker compose --env-file env/dev.env up -d
```

⚠️ **This is NOT suitable for production** - it runs `langgraph dev` which is a development server.

Other environments:

```bash
# Production (after building the image)
docker compose --env-file env/prod.env up -d
```

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

Dev Container uses the same Docker Compose configuration as dev environment
When you start the dev container, by default no services are started and you can choose which ones to start based on your needs. You can start the LangGraph server, CLI client, or Streamlit UI independently, depending on what you want to work on. Use the provided VS Code launch configurations for an easy start and debugging experience.

## VS Code Launch Configurations

1. `LangGraph Studio`

Starts LangGraph API server with hot reload and opens LangGraph Studio in the browser.
LangGraph Studio provides a web UI for managing and testing your agent graphs, making it a great choice for development and debugging. However, it doesn't support custom checkpointer and store implementations.

+ most handy - starts full dev env (LangGraph Studio, API server with hot reload)
+ vscode debugger support
- LangGraph Studio doesn't support custom checkpointer and store

2. `LangGraph API Server`

Starts the LangGraph API server with hot reload without opening the browser. This is useful when you only need the API server running — for example, to use it together with the `UI - CLI Client` or `UI - Streamlit` launch configs, or when you want to test custom checkpointer and store implementations that are not supported in LangGraph Studio.

3. `CLI Debug (cli_runner.py)`

Starts a standalone CLI client that runs directly against an instance of the agent graph without requiring a separate LangGraph API server. This is useful for fast testing and development of the agent graph logic without the overhead of starting the full LangGraph Studio environment. It also allows you to test custom checkpointer and store implementations that may not be supported in LangGraph Studio.

+ doesn't start nor require LangGraph API server - creates instance of agent graph and runs CLI chat directly against it
+ fast start
+ no extra dependencies
+ vscode debugger support
+ can be used to test custom checkpointer and store

4. `UI - CLI Client`

CLI client that connects to a running LangGraph API server. Start the server first using `LangGraph Dev (langgraph_dev_runner.py)` or `LangGraph API Server (no browser)`. This is useful for testing the CLI client in an environment that closely resembles production, where the client interacts with a running LangGraph API server.

5. `UI - Streamlit`

Starts the Streamlit server that can be used to interact with the LangGraph API server through a web UI. Requires a running LangGraph API server — start it first using `LangGraph Studio` or `LangGraph API Server`. This is useful for testing and developing the Streamlit UI client, allowing you to see changes in real-time as you develop the UI components. It also provides a more user-friendly interface for interacting with the agent graph compared to the CLI client.

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
docker compose exec ai-chatbot <command>

# Restart the container
docker compose restart ai-chatbot

# Rebuild and restart
docker compose up -d --build ai-chatbot
```

## Issues

All issues are stored in Github Issues. See more: [./app/docs/github-issues-extension.md](./app/docs/github-issues-extension.md)

