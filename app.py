import streamlit as st
from dotenv import load_dotenv
load_dotenv()
from src.main import run_pipeline
from src.benchmarker import benchmark_code
st.set_page_config(layout="wide", page_title="AI Code Review")
st.title("AI - Code Reviewer & Editor")

with st.sidebar:
    st.header("Documentation")
    st.markdown("""
    ### Architecture Overview
    This platform operates utilizing a **Multi-Agent Workflow** framed via **LangGraph**. 
    
    Instead of a single LLM prompt execution, the backend divides responsibilities across specialized AI nodes for Analysing and Refactoring code.
    """)
    st.info("Workflow: Input Code -> Critic Node -> (If Bugs Found) -> Developer Node -> Loops back to Critic")
    
    st.markdown("""
    ###Specialized Agents
    1. **The Security & QA Critic:** Analyzes code structures utilizing strict Pydantic JSON schemas to flag performance bottlenecks, logical smells, and vulnerabilities.
    2. **The Refactor Developer:** Evaluates the generated Critic schema arrays and programmatically rewrites code blocks to apply target optimizations.
    
    ###Performance Benchmarking
    The evaluation system isolates code strings within memory, executing tracking runtme via `time.perf_counter()` to map before and after optimization latency metrics.
    """)
    st.caption("Built with LangGraph, Google Gemini, Streamlit and lots of Learning :).")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Write Your Python Code")
    
    code_input = st.text_area("Source Code Area", placeholder="Enter your python code...", height=350)
    trigger_btn = st.button("Analyze & Rewrite Code", use_container_width=True)

with col2:
    st.subheader("Optimized Output ")
    if trigger_btn and code_input:
        with st.spinner("AI Agents are working on the code ..."):
            results = run_pipeline(code_input)
            orig_time = benchmark_code(code_input)
            new_time = benchmark_code(results["current_code"])
            
            if orig_time != 9999.0 and new_time != 9999.0:
                speedup = ((orig_time - new_time) / (orig_time + 1e-5)) * 100
                st.metric(label="Execution Time Speedup Percentage", value=f"{new_time:.3f} ms", delta=f"{speedup:.1f}% Faster" if speedup > 0 else f"{abs(speedup):.1f}% Slower")
            
            st.code(results["current_code"], language="python")
            st.subheader("Structural Flaws Found")
            report = results["critic_report"]
            if report and report.bugs:
                for bug in report.bugs:
                    with st.expander(f"Line {bug.line_number} | {bug.category}"):
                        st.write(f"**Issue:** {bug.issue}")
                        st.code(bug.fix, language="python")
            else:
                st.success("No performance defects detected.")