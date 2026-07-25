import os
from google import genai
from langgraph.graph import StateGraph, START, END
from .state import ReviewState, ReviewReport

# Initialize the official Google GenAI Client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Replace your existing critic_node definition with this verified format:
def critic_node(state: ReviewState) -> dict:
    prompt = f"""
    You are an expert Senior Security & QA Engineer. Analyze this code for bugs, 
    performance bottlenecks, and security hazards.
    
    Code to evaluate:
    ```python
    {state['current_code']}
    ```
    """
    
    # Ensure config parameter uses the types dictionary structure cleanly
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config={
            'response_mime_type': 'application/json',
            'response_schema': ReviewReport,
        }
    )
    
    report: ReviewReport = response.parsed
    return {
        "critic_report": report, 
        "iteration_count": state.get("iteration_count", 0) + 1
    }

def developer_node(state: ReviewState) -> dict:
    report = state["critic_report"]
    bug_details = "\n".join([f"- Line {b.line_number} [{b.category}]: {b.issue} -> Fix: {b.fix}" for b in report.bugs])
    
    prompt = f"""
    You are an Elite Developer. Refactor the following code by implementing the exact fixes 
    suggested by the Code Critic. Maintain the exact original feature behavior while optimizing it.
    Return ONLY valid, refactored Python code inside a standard markdown code block.

    Original Code:
```python
    {state['current_code']}
    ```

    Critic Fixes to apply:
    {bug_details}
    """
    
    response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
    raw_text = response.text
    
    if "```" in raw_text:
        cleaned_code = raw_text.split("```python")[1].split("```")[0].strip()
    elif "```" in raw_text:
        cleaned_code = raw_text.split("```")[1].split("```")[0].strip()
    else:
        cleaned_code = raw_text.strip()
        
    return {"current_code": cleaned_code}

def should_continue(state: ReviewState):
    if state["iteration_count"] >= 3 or state["critic_report"].is_clean:
        return END
    return "developer"

builder = StateGraph(ReviewState)
builder.add_node("critic", critic_node)
builder.add_node("developer", developer_node)

builder.add_edge(START, "critic")
builder.add_conditional_edges("critic", should_continue, {"developer": "developer", END: END})
builder.add_edge("developer", "critic")

graph = builder.compile()