FROM python:3.12 as ai-chatbot-base

RUN apt-get update && apt-get install -y --no-install-recommends \ 
    curl

ARG USER=chatbot
ARG UID=1000
ARG GID=1000

RUN groupadd -g ${GID} ${USER} && \
    useradd -m -u ${UID} -g ${GID} ${USER}

WORKDIR /app

COPY requirements.txt .

RUN pip3 install -r requirements.txt

# Production image
FROM ai-chatbot-base AS ai-chatbot-prod

# In production image copy the source directory into the image
COPY . .

RUN pip3 install langgraph-cli python-dotenv

EXPOSE 8501

EXPOSE 2024

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

USER ${USER}

#ENTRYPOINT ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]
#TODO: Launch langgraph server here - move UI code (Streamlit) to other container - needs fixing first (FastAPI addition)

# Development image (used in devcontainer)
FROM ai-chatbot-base AS ai-chatbot-dev

RUN apt-get update && apt-get install -y --no-install-recommends \
    git vim

ENV EDITOR=vim

RUN pip3 install langgraph-cli[inmem] --upgrade

# In development image the source directory is not copied to the image - mount it from the host instead
# while configuring the devcontainer

EXPOSE 8501

EXPOSE 2024

EXPOSE 5678

USER ${USER}

CMD [ "sleep", "infinity" ]
