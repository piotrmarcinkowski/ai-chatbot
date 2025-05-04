# ai-chatbot
General purpose AI chatbot.

# Configuration
Create `.env` file in the project's root folder basing on the attached [env.example](env.example) file.

# Run
The following command spins up all required containers in production mode.
```
docker compose up
```

Note: For development, use Dev Container setup described in the next section.

Once the app is started look for the following URL in the output and open the link in a web browser.

```
You can now view your Streamlit app in your browser.
ai-chatbot-1        |
ai-chatbot-1        |   URL: http://0.0.0.0:8501
```

# Dev container (vscode)

This project supports development in a container using vscode's Dev Container plugin.
Adding new features or fixing the existing ones is easiest when done in Dev Container.

## Prerequisites
Install `vscode` with `Dev Containers` plugin.

## Run Dev Container
- Open the command palette (Crtl+Shift+P)
- Type `Reopen in Dev Container`

After the container spins up, press F5 to run the project.
When working in Dev Container any change in code will be reflected after re-running the project.
The runtime environment used in the Dev Container is the same as the production environment. 
Dev Container offers additional dev tools and packages on top of those installed in the production
container (eg. git).

## Troubleshooting

In case of issues with running Dev Container, inspect the log first.

See the following commands in the command palette (Crtl+Shift+P):

- Dev Containers: Show Previous Log
- Dev Containers: Show Container Log
- Dev Containers Developer: Show All Logs...


## To do list
TODO: Implement chat history: https://github.com/aurelio-labs/langchain-course/blob/main/chapters/04-chat-memory.ipynb
TODO: Tool "if there is a valuable information in user's sentence store it as a fact". Figure out few methods as carrying important info. Np. User: "It's important what I'm going to say ", 
TODO: Tool "what have we talked about before?", "when did we talk about vacation plans?"
