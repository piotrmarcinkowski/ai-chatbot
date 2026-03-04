#!/usr/bin/env python3
import argparse
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
    parser = argparse.ArgumentParser(description="LangGraph dev server runner")
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Start the server without opening the LangGraph Studio browser tab",
    )
    args = parser.parse_args()

    os.chdir("app/src")

    # Check if LANGSMITH_API_KEY is set before starting the server
    if not os.getenv("LANGSMITH_API_KEY"):
        print("Warning: LANGSMITH_API_KEY is not set. LangSmith features will be unavailable.")
        return

    print("Starting LangGraph dev server...")

    if not args.no_browser:
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
