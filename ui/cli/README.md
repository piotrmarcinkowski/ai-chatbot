# CLI Client for AI Chatbot

Command-line interface that connects to the LangGraph server.

## Prerequisites

- Python 3.12+
- LangGraph server running (see main README.md)

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Default (connects to localhost:8123)

```bash
python chatbot_cli.py
```

### Custom server URL

```bash
export LANGGRAPH_SERVER_URL=http://localhost:8123
python chatbot_cli.py
```

## Configuration

Set the following environment variables:

- `LANGGRAPH_SERVER_URL`: URL of the LangGraph server (default: http://localhost:8123)

## Features

- Interactive chat interface
- Connects to remote LangGraph server via SDK
- Maintains conversation thread
- Error handling and recovery
