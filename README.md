# ai-chatbot
General purpose AI chatbot.

# Configuration
Create `.env` file in the project's root folder basing on the attached [env.example](env.example) file.

# Run

| :zap:  Out of order - docker compose environment needs fixing [issue](https://github.com/piotrmarcinkowski/ai-chatbot/issues/20)
|------------------------------------------|

The following command spins up all required containers in production mode. 
```
docker compose up
```

Note: For development, use Dev Container setup described in the next section.

~~
Once the app is started look for the following URL in the output and open the link in a web browser.

```
You can now view your Streamlit app in your browser.
ai-chatbot-1        |
ai-chatbot-1        |   URL: http://0.0.0.0:8501
```
~~

# Dev container (vscode)

This project supports development in a container using vscode's Dev Container plugin.
Devcontainer environment is the same as the environment used in the final deployment
with minor changes required for vscode addons (eg. `git` package is installed in devcontainer).
See `ai-chatbot-dev` image in [./app/Dockerfile]

## Prerequisites
Install `vscode` with `Dev Containers` plugin.

## Run Dev Container
- Open the command palette (Crtl+Shift+P)
- Type `Reopen in Dev Container`

## Start LangGraph server within Dev Container

After the container spins up, run the following command in the terminal:

```
cd app/src
langgraph dev --host 0.0.0.0 --no-browser
```

It can also be run through the `Run and Debug` tab, using `LangGraph Dev` launch configuration.

Open LangGraph Studio with the following link:
https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024 

Alternatively you can use a handy script that does all of the above. 
Launch it with

```
chmod +x agent_launcher.py
./agent_launcher.py
```

## Debugger

If running in Dev Container you can use the provided launch configration `LangGraph Dev (agent_launcher.py)`
It will start the langgraph server with the debugger.

Otherwise, start the server with the following command:

```
langgraph dev --debug-port 5678 --wait-for-client --host 0.0.0.0 --no-browser
```

https://docs.langchain.com/langgraph-platform/quick-start-studio#optional-attach-a-debugger

```
INFO:langgraph_api.cli:🐛 Debugger listening on port 5678. Waiting for client to attach...
INFO:langgraph_api.cli:To attach the debugger:
INFO:langgraph_api.cli:1. Open your python debugger client (e.g., Visual Studio Code).
INFO:langgraph_api.cli:2. Use the 'Remote Attach' configuration with the following settings:
INFO:langgraph_api.cli:   - Host: 0.0.0.0
INFO:langgraph_api.cli:   - Port: 5678
```

## Troubleshooting

In case of issues with running Dev Container, inspect the log first.

See the following commands in the command palette (Crtl+Shift+P):

- Dev Containers: Show Previous Log
- Dev Containers: Show Container Log
- Dev Containers Developer: Show All Logs...

## Issues

All issues are stored in Github Issues. See more: [./docs/github-issues-extension.md](./docs/github-issues-extension.md)
