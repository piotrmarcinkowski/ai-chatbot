# AI chatbot
AI chatbot prototype

# Build
```
docker build -t ai-chatbot .
```

# Run
```
docker run --rm -p 8501:8501 --env-file .env --name ai-chatbot ai-chatbot
````