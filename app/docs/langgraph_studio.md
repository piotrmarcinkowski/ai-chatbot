## LangGraph vscode launch configuration

The `langgraph` command is a simple python script
```
chatbot@a340ca91669f:/ai-chatbot/app/src$ cat /usr/local/bin/langgraph
#!/usr/local/bin/python3.12
# -*- coding: utf-8 -*-
import re
import sys
from langgraph_cli.cli import cli
if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw|\.exe)?$', '', sys.argv[0])
    sys.exit(cli())
```

The script defines the interpreter in the first line. It might cause `module not found` errors when running the application, therefore make sure you define the python interpreter via `python` property in the vscode launch configuration. 

The following launch configuration includes all necessary properties to launch the langgraph server 

```
    {
      "name": "LangGraph Dev",
      "type": "debugpy",
      "request": "launch",
      "program": "/usr/local/bin/langgraph",
      "python": "/usr/local/bin/python3",
      "cwd": "${workspaceFolder}/app/src",
      "args": [
        "dev",
        "--host", "0.0.0.0"
      ],
      "console": "integratedTerminal"
    }
```

The param `--host "0.0.0.0"` makes the server accessible when run in Dev Container.

## LangGraph Studio

You need to use the following address:
```
https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024 
```

## Troubleshooting

When trying to run `langgraph dev`

```
ValueError: Heads up! Your graph 'graph' from './agent/graph.py' includes a custom checkpointer (type <class 'langgraph.checkpoint.mongodb.saver.MongoDBSaver'>). With LangGraph API, persistence is handled automatically by the platform, so providing a custom checkpointer (type <class 'langgraph.checkpoint.mongodb.saver.MongoDBSaver'>) here isn't necessary and will be ignored when deployed.

To simplify your setup and use the built-in persistence, please remove the custom checkpointer (type <class 'langgraph.checkpoint.mongodb.saver.MongoDBSaver'>) from your graph definition. If you are looking to customize which postgres database to connect to, please set the `POSTGRES_URI` environment variable. See https://langchain-ai.github.io/langgraph/cloud/reference/env_var/#postgres_uri_custom for more details.
```

More info: 

- https://github.com/CopilotKit/CopilotKit/issues/1692
- https://github.com/langchain-ai/langgraph/discussions/4352
