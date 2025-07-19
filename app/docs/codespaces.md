# Run project in Github Workspaces
There were several issues found when trying to run this project in Codespace instance
This page documents these issues and attempts to solve them.

# Workspace folder issue
When setting up a Codespace instance there is an issue with workspace directory. It doesn't exist.
The root cause is probably in the following mount entries in `.devcontainer/devcontainer.json` not being executed

```
"workspaceFolder": "/ai-chatbot",
"mounts": [
   "source=${localWorkspaceFolder},target=/ai-chatbot,type=bind",
   "source=${localWorkspaceFolder}/.devcontainer/.vscode,target=/ai-chatbot/.vscode,type=bind"
],
```

It seems that Codespace uses the following directory. Provide it when prompt with missing workspace folder shows up. 
```
/workspaces/ai-chatbot
```

# Vscode configuration missing
.vscode directory gets mounted on top of the original code structure. 
It's missing becuase of the same reason as described above for workspace directory.

Copy the missing directory using the Codespace instance terminal.
```
cp -r /workspaces/ai-chatbot/.devcontainer/.vscode .
```

# System variables
The following variables are defines in the environment within codespace instance.

```
$ env
GITHUB_TOKEN=ghu_uVHNogf33nzxcvmBwKGWe0MErhsGJm4dJ33d
GITHUB_CODESPACE_TOKEN=ABQUS35D6TXVVWSX6SNOWPLIPRJPLANCNFSM4AO22J2Q
HOSTNAME=00f845f188df
GIT_ASKPASS=/vscode/bin/linux-x64/7adae6a56e34cb64d08899664b814cf620465925/extensions/git/dist/askpass.sh
GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN=app.github.dev
BROWSER=/vscode/bin/linux-x64/7adae6a56e34cb64d08899664b814cf620465925/bin/helpers/browser.sh
HOME=/home/chatbot
TERM_PROGRAM_VERSION=1.102.1
VSCODE_IPC_HOOK_CLI=/tmp/vscode-ipc-9c79c978-607c-4981-90f5-7e0606f8814b.sock
CODESPACES=true
GPG_KEY=7169605F62C751356D054A26A821E680E5FA6305
VSCODE_GIT_ASKPASS_MAIN=/vscode/bin/linux-x64/7adae6a56e34cb64d08899664b814cf620465925/extensions/git/dist/askpass-main.js
VSCODE_GIT_ASKPASS_NODE=/vscode/bin/linux-x64/7adae6a56e34cb64d08899664b814cf620465925/node
PYTHON_SHA256=c30bb24b7f1e9a19b11b55a546434f74e739bb4c271a3e3a80ff4380d49f7adb
GITHUB_GRAPHQL_URL=https://api.github.com/graphql
GITHUB_USER=piotrmarcinkowski
COLORTERM=truecolor
ContainerVersion=13
GITHUB_API_URL=https://api.github.com
RepositoryName=ai-chatbot
CLOUDENV_ENVIRONMENT_ID=08fd5c31-4207-4dfb-ae2b-2c2f836ef94a
TERM=xterm-256color
PATH=/vscode/bin/linux-x64/7adae6a56e34cb64d08899664b814cf620465925/bin/remote-cli:/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
SHELL_LOGGED_IN=true
LANG=C.UTF-8
GITHUB_REPOSITORY=piotrmarcinkowski/ai-chatbot
TERM_PROGRAM=vscode
VSCODE_GIT_IPC_HANDLE=/tmp/vscode-git-d45602d50f.sock
SHELL=/bin/sh
PYTHON_VERSION=3.12.11
STREAMLIT_SERVER_HEADLESS=true
VSCODE_GIT_ASKPASS_EXTRA_ARGS=
INTERNAL_VSCS_TARGET_URL=https://westeurope.online.visualstudio.com
PWD=/workspaces/ai-chatbot
GITHUB_SERVER_URL=https://github.com
CODESPACE_NAME=effective-zebra-59j966vx5pf4r5
CODESPACE_VSCODE_FOLDER=/workspaces/ai-chatbot
```