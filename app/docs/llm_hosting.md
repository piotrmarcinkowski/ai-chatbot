# What is Ollama?

`The Ollama project is a platform for hosting and managing AI models`. It simplifies deployment, scaling, and maintenance of AI models, providing infrastructure and tools for seamless integration into applications. Ollama supports multiple models, ensuring efficient management and scalability according to demand.

> [!info] Why Ollama?
> Ollama is considered the easiest platform for building with LLM (in the year 2024).

# Installation

https://ollama.com/

```
curl -fsSL https://ollama.com/install.sh | sh
```
# Run

After the previous `Installation` step the Ollama AI server should already be running. Verify at: 
```
localhost:11434
```

Ollama service
```
systemctl status ollama
```
#### Install and run AI modules

```
ollama pull llama2
ollama run llama2
```

Commands help
```
/help
```

#### Configure ollama server

- https://github.com/ollama/ollama/blob/main/docs/faq.md
- https://github.com/varunvasudeva1/ollama-server-docs

Edit ollama systemd service

```
systemctl edit ollama.service
# If the above command opens incorrect file try the following 
vim /etc/systemd/system/ollama.service
```

Listen on 0.0.0.0:11434 - add the following line (note: there can be multiple `Environment` lines)

```
Environment="OLLAMA_HOST=0.0.0.0:11434"
```

Apply changes

```
systemctl daemon-reload
```

Restart `ollama` server

```
systemctl restart ollama
```

Check server logs

```
systemctl status ollama
```

Verify if listen on 0.0.0.0

```
wrz 17 20:44:19 piotr-ubuntu ollama[19492]: time=2025-09-17T20:44:19.070+02:00 level=INFO source=routes.go:1385 msg="Listening on [::]:11434 (version 0.11.11)"
```

#### GPU usage

```
watch -n 0.5 nvidia-smi
```
