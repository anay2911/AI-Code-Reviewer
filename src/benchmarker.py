import time
import sys
import io

def benchmark_code(code_string: str) -> float:
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    execution_context = {"__builtins__": __builtins__}
    
    try:
        start_time = time.perf_counter()
        exec(code_string, execution_context)
        func_name = None
        for line in code_string.split('\n'):
            if line.strip().startswith('def '):
                func_name = line.split('def ')[1].split('(')[0].strip()
                break
        if func_name and func_name in execution_context:
            target_function = execution_context[func_name]
            target_function([1, 2, 3, 4, 5, 2, 1])
            
        end_time = time.perf_counter()
        execution_time_ms = (end_time - start_time) * 1000
        return round(execution_time_ms, 4)
        
    except Exception as e:
        return 9999.0  
    finally:
        sys.stdout = old_stdout