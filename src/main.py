from .workflow import graph

def run_pipeline(code: str) -> dict:
    initial_state = {
        "original_code": code,
        "current_code": code,
        "critic_report": None,
        "iteration_count": 0
    }
    return graph.invoke(initial_state)