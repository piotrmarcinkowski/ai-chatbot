#!/usr/bin/env python3
import os
import threading
import time
import webbrowser
import sys
from langgraph_cli.cli import cli

def open_browser_later(url, delay=2):
    time.sleep(delay)
    webbrowser.open_new_tab(url)

def main():
    os.chdir("app/src")

    url = "https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024"
    threading.Thread(target=open_browser_later, args=(url, 5), daemon=True).start()

    # Backup sys.argv and set arguments for langgraph
    old_argv = sys.argv.copy()
    sys.argv = ["langgraph", "dev", "--host", "0.0.0.0", "--no-browser"]

    try:
        cli()  # blocks until interrupted
    except SystemExit:
        pass  # prevent langgraph's sys.exit from killing the script
    finally:
        sys.argv = old_argv

if __name__ == "__main__":
    main()
