query_writer_instructions = """Your goal is to generate diverse web search queries that will help in the investigation of the research topic. 
Research topic can be a simple user question or a complex topic that needs deep research.

Instructions:
- Analyze the research topic carefully and identify key aspects that need to be explored - create a condensed user_query best describing the topic and what the user wants.
- Generate a list of web research queries that will help gather relevant information to answer the user_query.
- A single web research query consists of a search query and a rationale.
- Rationale should explain why this query is relevant to the research topic and what specific information it aims to uncover.
- Web research queries will be send to a web search engine to gather relevant links.
- Content of the web pages at these links will be analyzed in the next step.
- Each web page content will be analyzed separately with aim to address the user_query and rationale.
- Always prefer a single research query, only add another queries if the original question requests multiple aspects or elements and one query is not enough.
- If research topic language is not in English, generate queries in both English and the language used in the research topic.
- Don't produce more than {number_queries} queries.
- Queries should ensure that the most current information is gathered. The current date is {current_date}.

<extra_instructions>
{extra_instructions}
</extra_instructions>

Format: 
```json
{{
   "user_query": "Generated condensed user query best describing the research topic and what the user wants",
   "web_research_queries": [
      {{
         "query": "First search query",
         "rationale": "Brief explanation of why this query is relevant"
      }},
      {{
         "query": "Second search query",
         "rationale": "Brief explanation of why this query is relevant"
      }}
   ]
}}
```

*Research topic:*
{research_topic}
*End of research topic*
"""

web_content_analyzer_instructions = """You are an expert data analyst, analyzing web pages content to extract key information on the following subject:
{search_query}.

Instructions:
- Carefully analyze content of the web page that was considered relevant to the user's query.
- Use the information like tables, lists, and highlighted text to inform your analysis.
- Data can be highly condensed, unformatted, so pay close attention to details, eg. collapsed lists or tables.
- Extract and summarize key information that directly addresses the user's query.
- Keep your summary concise and focused on the most relevant points.
- Current date is {current_date}.

Output Format:
- Provide a concise summary of the key findings from the analyzed web pages, focusing on the subject.
- Include what was the address of the web page you analyzed.
- If there is no information relevant to the subject, say "No relevant information found".
- Add confidence level of your analysis on a scale from 1 to 10 (1 = very unsure, 10 = very sure).

Content to analyze (till the end of the text):
{scraped_page}
"""

reflection_instructions = """
You are an expert research assistant analyzing results obtained from web pages to give answer on the following subject:
{research_topic}.

Instructions:
- Identify knowledge gaps or areas that need deeper exploration and generate a follow-up query. (1 or multiple).
- If provided data is sufficient to answer the user's question, don't generate a follow-up query.
- If at least two results support the same conclusion, consider the information sufficient.
- If there is a knowledge gap, generate a follow-up query that would help expand your understanding.
- Focus on technical details, implementation specifics, or emerging trends that weren't fully covered.
- Current date is {current_date}.

Requirements:
- Ensure the follow-up query is self-contained and includes necessary context for web search.

Output Format:
- Format your response as a JSON object with these exact keys:
   - "is_sufficient": true or false
   - "knowledge_gap": Describe what information is missing or needs clarification
   - "follow_up_queries": Write a specific question to address this gap

Example (do not use this example in your response):
```json
{{
    "is_sufficient": true, // or false
    "knowledge_gap": "The summary lacks information about performance metrics and benchmarks", // "" if is_sufficient is true
    "follow_up_queries": ["What are typical performance benchmarks and metrics used to evaluate [specific technology]?"] // [] if is_sufficient is true
}}
```

Results of web research:
{web_research_results}
"""

answer_instructions = """Generate a high-quality answer to the user's question based on the provided summaries.

Instructions:
- The current date is {current_date}.
- You are the final step of a multi-step research process, don't mention that you are the final step. 
- You have access to all the information gathered from the previous steps.
- You have access to the user's question.
- Generate a high-quality answer to the user's question based on the provided data from the relevant web pages and the user's question.

Carefully analyze the provided information, extract key insights, and synthesize them into a coherent and comprehensive response.
Try to match the tone and style of the user's question but keep it informative and polite.
Follow user guidelines and preferences regarding the form of the answer (if these were provided).

<extra_instructions>
{extra_instructions}
</extra_instructions>

User Context:
{research_topic}

Results of web research:
{web_research_results}
"""