# This file implements the main logic for running the assistant application.

import logging
import sys
import uuid
from langchain_core.messages import HumanMessage
from agent.graph import graph as agent_graph
from agent.state import AgentState
from config.config_loader import assistant_config

logging.basicConfig(level=logging.WARN)
logger = logging.getLogger(__name__)

class AssistantRunner:
    """
    Console application runner for the AI assistant.
    """
    
    def __init__(self):
        self.assistant_name = assistant_config.get("assistant_name", "Assistant")
        self.graph = agent_graph
        self.thread_id = str(uuid.uuid4())
        self.config = {"configurable": {"thread_id": self.thread_id, "model_name": "openai"}}
        
    def print_welcome_message(self):
        """Print welcome message to the user."""
        print(f"\n{'='*60}")
        print(f"🤖 Welcome to {self.assistant_name} - Your AI Assistant")
        print(f"{'='*60}")
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
    
    def process_user_query(self, user_input: str) -> str:
        """Process user query through the agent graph."""
        try:
            logger.info("Processing user query: %s", user_input)
            
            # Create the initial state
            initial_state = AgentState(
                messages=[HumanMessage(content=user_input)],
                # knowledge_search_results=[]
            )
            
            # Run the graph
            result = self.graph.invoke(initial_state, config=self.config)
            
            # Extract the response
            if result.get("answer"):
                return result["answer"]
            elif result.get("messages") and len(result["messages"]) > 1:
                # Get the last AI message
                last_message = result["messages"][-1]
                if hasattr(last_message, 'content'):
                    return last_message.content
                else:
                    return str(last_message)
            else:
                return "I'm sorry, I couldn't process your request at the moment."
                
        except (ValueError, TypeError, RuntimeError) as e:
            logger.error("Error processing query: %s", str(e))
            return f"I encountered an error while processing your request: {str(e)}"
        except Exception as e:
            logger.error("Unexpected error processing query: %s", str(e))
            return "I'm sorry, I encountered an unexpected error while processing your request."
    
    def run_chat_loop(self):
        """Main chat loop."""
        self.print_welcome_message()
        
        while True:
            try:
                user_input = self.get_user_input()
                
                if self.should_quit(user_input):
                    print(f"\n👋 Goodbye! Thanks for chatting with {self.assistant_name}.")
                    break
                
                if not user_input:
                    continue
                
                print(f"\n🤖 {self.assistant_name}: ", end="")
                
                # Process the query and get response
                response = self.process_user_query(user_input)
                print(response)
                
                self.print_separator()
                
            except KeyboardInterrupt:
                print(f"\n\n👋 Goodbye! Thanks for chatting with {self.assistant_name}.")
                break
            except Exception as e:
                logger.error("Unexpected error in chat loop: %s", str(e))
                print(f"\n❌ An unexpected error occurred: {e}")
                self.print_separator()

def run_assistant():
    """
    Main function to run the assistant application.
    """
    logger.info("Starting the assistant application...")
    
    try:
        runner = AssistantRunner()
        runner.run_chat_loop()
    except Exception as e:
        logger.error("Failed to start assistant: %s", str(e))
        print(f"❌ Failed to start the assistant: {e}")
        sys.exit(1)


if __name__ == "__main__":
    run_assistant()
