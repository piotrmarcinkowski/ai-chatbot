"""
CLI client for AI Chatbot that connects to LangGraph server.

This client uses the LangGraph SDK to communicate with the LangGraph server
running in a Docker container or locally.
"""

import logging
import os
import sys
import asyncio
import uuid
from typing import Optional
from langgraph_sdk import get_client

logging.basicConfig(level=logging.WARN)
logger = logging.getLogger(__name__)


class ChatbotCLI:
    """
    Command-line interface for the AI chatbot.
    Connects to LangGraph server via SDK.
    """

    def __init__(self, server_url: Optional[str] = None, graph_name: str = "main"):
        """
        Initialize the chatbot client.

        Args:
            server_url: URL of the LangGraph server (default: http://localhost:8123)
            graph_name: Name of the graph to use (default: main)
        """
        self.server_url = server_url or os.getenv("LANGGRAPH_SERVER_URL", "http://localhost:8123")
        self.graph_name = graph_name
        self.assistant_name = "AI Assistant"
        self.client = None
        self.thread_id = None

    async def initialize(self):
        """Initialize connection to LangGraph server."""
        try:
            self.client = get_client(url=self.server_url)
            # Create a new thread for this conversation
            thread = await self.client.threads.create()
            self.thread_id = thread["thread_id"]
            logger.info(f"Connected to LangGraph server at {self.server_url}")
            logger.info(f"Thread ID: {self.thread_id}")
        except Exception as e:
            logger.error(f"Failed to connect to LangGraph server: {e}")
            raise

    def print_welcome_message(self):
        """Print welcome message to the user."""
        print(f"\n{'='*60}")
        print(f"🤖 Welcome to {self.assistant_name}")
        print(f"{'='*60}")
        print(f"Connected to: {self.server_url}")
        print(f"Graph: {self.graph_name}")
        print("Type your questions or commands. Use 'quit', 'exit', or 'q' to stop.")
        print(f"{'='*60}\n")

    def print_separator(self):
        """Print a separator line."""
        print(f"\n{'-'*60}\n")

    def get_user_input(self) -> str:
        """Get user input from console."""
        try:
            return input("👤 You: ").strip()
        except (EOFError, KeyboardInterrupt):
            return "quit"

    def should_quit(self, user_input: str) -> bool:
        """Check if user wants to quit."""
        return user_input.lower() in ['quit', 'exit', 'q', '']

    async def process_user_query(self, user_input: str) -> str:
        """
        Process user query through the LangGraph server.

        Args:
            user_input: User's message

        Returns:
            Assistant's response
        """
        try:
            logger.info("Processing user query: %s", user_input)

            # Create input for the graph
            input_data = {
                "messages": [
                    {
                        "role": "user",
                        "content": user_input
                    }
                ]
            }

            # Stream the response and look for assistant messages
            assistant_response = None
            async for chunk in self.client.runs.stream(
                thread_id=self.thread_id,
                assistant_id=self.graph_name,
                input=input_data,
                stream_mode="updates"
            ):
                # Process each chunk - look for messages in node updates
                if not (hasattr(chunk, 'data') and isinstance(chunk.data, dict)):
                    continue

                # Check each node update for messages or answer
                for node_data in chunk.data.values():
                    if not isinstance(node_data, dict):
                        continue

                    # Check for direct answer field first
                    if "answer" in node_data:
                        assistant_response = node_data["answer"]
                        continue

                    # Check for messages array
                    messages = node_data.get("messages", [])
                    if not messages:
                        continue

                    # Get the last message
                    last_message = messages[-1]

                    # Extract content from dict or object
                    if isinstance(last_message, dict):
                        msg_type = last_message.get("type") or last_message.get("role")
                        if msg_type in ("ai", "assistant"):
                            assistant_response = last_message.get("content", "")
                    elif hasattr(last_message, 'content'):
                        msg_type = getattr(last_message, 'type', None) or getattr(last_message, 'role', None)
                        if msg_type in ("ai", "assistant"):
                            assistant_response = last_message.content

            if assistant_response:
                return assistant_response

            # If no response found, log for debugging
            logger.warning("No assistant response found in stream chunks")
            return "I'm sorry, I couldn't process your request at the moment."

        except Exception as e:
            logger.error("Error processing query: %s", str(e), exc_info=True)
            return f"I encountered an error while processing your request: {str(e)}"

    async def run_chat_loop(self):
        """Main chat loop."""
        await self.initialize()
        self.print_welcome_message()

        while True:
            try:
                user_input = self.get_user_input()

                if self.should_quit(user_input):
                    print(f"\n👋 Goodbye! Thanks for chatting with {self.assistant_name}.")
                    break

                if not user_input:
                    continue

                print(f"\n🤖 {self.assistant_name}: ", end="", flush=True)

                # Process the query and get response
                response = await self.process_user_query(user_input)
                print(response)

                self.print_separator()

            except KeyboardInterrupt:
                print(f"\n\n👋 Goodbye! Thanks for chatting with {self.assistant_name}.")
                break
            except Exception as e:
                logger.error("Unexpected error in chat loop: %s", str(e))
                print(f"\n❌ An unexpected error occurred: {e}")
                self.print_separator()


async def main():
    """
    Main function to run the CLI application.
    """
    logger.info("Starting the CLI application...")

    try:
        cli = ChatbotCLI()
        await cli.run_chat_loop()
    except Exception as e:
        logger.error("Failed to start CLI: %s", str(e))
        print(f"❌ Failed to start the CLI: {e}")
        print(f"\nMake sure the LangGraph server is running at the expected URL.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
