import os
import ast
import operator
import logging
from datetime import datetime, date
from langchain_core.tools import tool
from langchain_community.utilities import ArxivAPIWrapper,WikipediaAPIWrapper
from langchain_community.tools import ArxivQueryRun,WikipediaQueryRun
from pydantic import BaseModel, Field
from utils.time import current_local_time, current_utc_time, local_time_zone
from langchain_google_community import GoogleSearchAPIWrapper
from langchain_tavily import TavilySearch

log = logging.getLogger(__name__)

@tool("current_datetime", return_direct=True)
def get_current_datetime() -> str:
    """
    Returns the current date and time in ISO format.
    Useful when reasoning about upcoming events, schedules, or time-dependent calculations.
    """
    return current_local_time()

@tool
def get_current_utc_time():
    """
    Returns the current UTC time in the ISO 8601 format.
    """
    now = current_utc_time()
    return now

@tool("date_difference", return_direct=True)
def date_difference(target_date: str) -> str:
    """
    Calculates the number of days between today and a given target date.
    Input must be in the format 'YYYY-MM-DD'.
    Returns a human-readable difference (past or future).
    """
    try:
        today = date.today()
        target = datetime.strptime(target_date, "%Y-%m-%d").date()
        delta = (target - today).days

        if delta > 0:
            return f"There are {delta} days until {target}."
        elif delta < 0:
            return f"{abs(delta)} days have passed since {target}."
        else:
            return f"Today is {target}."
    except Exception as e:
        return f"Error: invalid date format. Please provide 'YYYY-MM-DD'. ({str(e)})"

@tool("date_operations", return_direct=True)
def date_operations(operation: str) -> str:
    """
    Performs date arithmetic operations. Supports two types of operations:
    
    1. Calculate difference between two dates (date1 - date2):
       Format: "YYYY-MM-DD - YYYY-MM-DD"
       Example: "2026-02-01 - 2026-01-14" returns "18 days"
    
    2. Add or subtract days from a date (date +/- days):
       Format: "YYYY-MM-DD + X days" or "YYYY-MM-DD - X days"
       Example: "2026-01-14 + 30 days" returns "2026-02-13"
       Example: "2026-01-14 - 10 days" returns "2026-01-04"
    
    All dates must be in YYYY-MM-DD format.
    """
    from datetime import timedelta
    import re
    
    try:
        operation = operation.strip()
        
        # Pattern 1: date1 - date2 (difference between two dates)
        date_diff_pattern = r'(\d{4}-\d{2}-\d{2})\s*-\s*(\d{4}-\d{2}-\d{2})'
        match = re.match(date_diff_pattern, operation)
        if match:
            date1_str, date2_str = match.groups()
            date1 = datetime.strptime(date1_str, "%Y-%m-%d").date()
            date2 = datetime.strptime(date2_str, "%Y-%m-%d").date()
            delta = (date1 - date2).days
            
            if delta == 0:
                return "0 days (same date)"
            elif delta == 1:
                return "1 day"
            elif delta == -1:
                return "-1 day"
            else:
                return f"{delta} days"
        
        # Pattern 2: date + X days or date - X days (date arithmetic)
        date_add_pattern = r'(\d{4}-\d{2}-\d{2})\s*([+\-])\s*(\d+)\s*days?'
        match = re.match(date_add_pattern, operation, re.IGNORECASE)
        if match:
            date_str, operator_sign, days_str = match.groups()
            base_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            days = int(days_str)
            
            if operator_sign == '+':
                result_date = base_date + timedelta(days=days)
            else:  # operator_sign == '-'
                result_date = base_date - timedelta(days=days)
            
            return result_date.strftime("%Y-%m-%d")
        
        # If no pattern matched
        return ("Invalid format. Supported formats:\n"
                "1. Date difference: 'YYYY-MM-DD - YYYY-MM-DD'\n"
                "2. Add days: 'YYYY-MM-DD + X days'\n"
                "3. Subtract days: 'YYYY-MM-DD - X days'")
        
    except ValueError as e:
        return f"Error: Invalid date format. Please use YYYY-MM-DD. ({str(e)})"
    except Exception as e:
        return f"Error processing date operation: {str(e)}"

@tool("local_time_zone", return_direct=True)
def get_local_time_zone():
    """
    Returns the current local timezone.
    """
    local_tz = local_time_zone()
    return str(local_tz)

@tool("math_calculator", return_direct=True)
def calculate_math_expression(expression: str) -> str:
    """
    Safely evaluates a mathematical expression and returns the result.
    Supports basic arithmetic operations: +, -, *, /, //, %, ** (power).
    Also supports mathematical functions: sqrt, sin, cos, tan, log, exp, abs, round.
    
    Examples:
    - "2 + 2" returns "4"
    - "10 * (5 + 3)" returns "80"
    - "2 ** 8" returns "256"
    - "sqrt(16)" returns "4.0"
    
    Input must be a valid mathematical expression as a string.
    """
    # Allowed operators
    operators = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.FloorDiv: operator.floordiv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
        ast.USub: operator.neg,
        ast.UAdd: operator.pos,
    }
    
    # Allowed functions
    import math
    functions = {
        'sqrt': math.sqrt,
        'sin': math.sin,
        'cos': math.cos,
        'tan': math.tan,
        'log': math.log,
        'log10': math.log10,
        'exp': math.exp,
        'abs': abs,
        'round': round,
        'floor': math.floor,
        'ceil': math.ceil,
        'pi': math.pi,
        'e': math.e,
    }
    
    def eval_node(node):
        if isinstance(node, ast.Num):
            return node.n
        elif isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.BinOp):
            left = eval_node(node.left)
            right = eval_node(node.right)
            return operators[type(node.op)](left, right)
        elif isinstance(node, ast.UnaryOp):
            operand = eval_node(node.operand)
            return operators[type(node.op)](operand)
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in functions:
                func = functions[node.func.id]
                args = [eval_node(arg) for arg in node.args]
                return func(*args)
            else:
                raise ValueError(f"Function not allowed: {node.func.id if isinstance(node.func, ast.Name) else 'unknown'}")
        elif isinstance(node, ast.Name):
            if node.id in functions and not callable(functions[node.id]):
                return functions[node.id]
            else:
                raise ValueError(f"Variable not allowed: {node.id}")
        else:
            raise ValueError(f"Unsupported operation: {type(node).__name__}")
    
    try:
        # Parse the expression
        tree = ast.parse(expression, mode='eval')
        # Evaluate safely
        result = eval_node(tree.body)
        log.debug(f"Math calculator: '{expression}' = {result}")
        return str(result)
    except SyntaxError as e:
        return f"Syntax error: Invalid mathematical expression. {str(e)}"
    except ValueError as e:
        return f"Error: {str(e)}"
    except ZeroDivisionError:
        return "Error: Division by zero."
    except Exception as e:
        return f"Error calculating expression: {str(e)}"

class ArxivTopic(BaseModel):
    topic: str = Field(description="The topic of the article to search on arxiv.")

@tool (args_schema=ArxivTopic)
def arxiv_search(topic: str) -> str:
    """Returns the information about research papers from arxiv"""
    arxiv_api=ArxivAPIWrapper(top_k_results=1,doc_content_chars_max=300)
    arxiv_tool=ArxivQueryRun(api_wrapper=arxiv_api)
    log.debug("Tool: arxiv_search - query: %s", topic)
    result = arxiv_tool.invoke(topic)
    log.debug("Tool: arxiv_search - result: %s", result)
    return result


class WikipediaTopic(BaseModel):
    topic: str = Field(description="The wikipedia article topic to search")

@tool(args_schema = WikipediaTopic)
def wikipedia_search(topic: str) -> str:
    """Returns the summary of wikipedia page of the passed topic"""
    api_wrapper=WikipediaAPIWrapper(top_k_results=1,doc_content_chars_max=300)
    wiki_tool=WikipediaQueryRun(api_wrapper=api_wrapper)
    log.debug("Tool: get_wiki_data - query: %s", topic)
    result = wiki_tool.invoke(topic)
    log.debug("Tool: get_wiki_data - result: %s", result)
    return result

@tool
def google_web_search(query: str) -> str:
    """
    Searches the web using Google Custom Search Engine (CSE) and returns the top results.
    """

    google_search = GoogleSearchAPIWrapper(
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        google_cse_id=os.getenv("GOOGLE_CSE_ID")
    )
    results = google_search.results(query=query, num_results=5)
    log.debug("Google search results for query '%s': %s", query, results)
    return results

def init_all_tools():
    """
    Initializes and returns a list of tools.
    """
    log.info("Initializing tools...")
    _tools = [get_current_datetime, date_difference, date_operations, get_current_utc_time, get_local_time_zone,
             calculate_math_expression, arxiv_search, wikipedia_search
    ]

    init_tavily_search_tool(_tools)
    init_google_search_tool(_tools)
    
    log.info("Tools initialized: %s", _tools)
    return _tools

def init_tavily_search_tool(tools_list):
    """
    Initialize Tavily search tool with API key
    """
    _tavily_api_key = os.getenv("TAVILY_API_KEY")
    if _tavily_api_key:
        log.info("Tavily API key found - activating Tavily search tool.")
        tools_list.append(TavilySearch(max_results=2, include_answer=True, include_raw_content=False, auto_parameters=True))
    else:
        log.warning("Tavily API key must be set in environment variables. Tavily search tool will not be available.")

def init_google_search_tool(tools_list):
    """
    Initialize Google search tool with API key and CSE ID
    """
    _google_api_key = os.getenv("GOOGLE_API_KEY")
    _google_cse_id = os.getenv("GOOGLE_CSE_ID")
    if _google_api_key and _google_cse_id:
        log.info("Google API key and CSE ID found - activating Google search tool.")
        tools_list.append(google_web_search)
    else:
        log.warning("Google API key and CSE ID must be set in environment variables. Google search tool will not be available.")

all_tools = init_all_tools()
