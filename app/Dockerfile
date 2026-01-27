FROM python:3.12 AS ai-chatbot-base

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

ARG USER=chatbot
ARG UID=1000
ARG GID=1000

RUN groupadd -g ${GID} ${USER} && \
    useradd -m -u ${UID} -g ${GID} ${USER}

WORKDIR /app

COPY requirements.txt .

RUN pip3 install -r requirements.txt

# Development image - intended to run with 'docker compose up'
FROM ai-chatbot-base AS ai-chatbot-dev

# In development image copy the source directory into the image
COPY . .

RUN pip3 install langgraph-cli python-dotenv

# LangGraph server port (default is 8123)
EXPOSE 8123

HEALTHCHECK CMD curl --fail http://localhost:8123/ok || exit 1

WORKDIR /app/src

USER ${USER}

# Note: 'langgraph up' requires Docker-in-Docker which doesn't work in containers
# 'langgraph dev' is suitable for fast deployments when run with --no-reload
CMD ["langgraph", "dev", "--host", "0.0.0.0", "--port", "8123", "--no-browser", "--no-reload"]

# Development image (used in devcontainer)
FROM ai-chatbot-base AS ai-chatbot-devcontainer

RUN apt-get update && apt-get install -y --no-install-recommends \
    git vim \
    && rm -rf /var/lib/apt/lists/*

ENV EDITOR=vim

RUN pip3 install langgraph-cli[inmem] --upgrade

# In devcontainer image the source directory is not copied to the image - mount it from the host instead
# while configuring the devcontainer

# LangGraph server port (for development with 'langgraph dev')
EXPOSE 2024
# Debug port for VSCode remote debugging
EXPOSE 5678

USER ${USER}

CMD [ "sleep", "infinity" ]
