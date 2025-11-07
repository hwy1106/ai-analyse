from dotenv import load_dotenv
import os
import re
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_google_genai import ChatGoogleGenerativeAI
from pypdf import PdfReader
from collections import Counter
from pathlib import Path
import pandas as pd
import numpy as np

from analyse import (
    graph as finance_graph,
)

from analyse_ba import (
    graph as sales_graph,
)

load_dotenv()

# Check if API key is available
if not os.getenv("GOOGLE_API_KEY"):
    print("⚠️  Warning: GOOGLE_API_KEY not found in environment variables")
    print("Please set your Google API key in a .env file or environment variable")

# --- Combined State Definition ---
class CombinedState(TypedDict):
    file_path_finance: str
    file_path_sales: str
    analysis_finance: str
    analysis_sales: str
    combined_analysis: str

# --- Step 1: Create subgraph for financial analysis ---
def run_financial_analysis(state: CombinedState) -> CombinedState:
    print('Debug financial analysis called:', state["file_path_finance"])
    
    try:
        result = finance_graph.invoke({"file_path": state["file_path_finance"]})
        state["analysis_finance"] = result.get("analysis", "")
        print(f"✅ Financial analysis completed")

    except Exception as e:
        print(f"❌ Error during financial analysis: {e}")
        state["analysis_finance"] = f"Analysis failed: {e}"
        return state
    
    return state

# --- Step 2: Create subgraph for sales analysis ---
def run_sales_analysis(state: CombinedState) -> CombinedState:
    try:
        result = sales_graph.invoke({"file_path": state["file_path_sales"]})
        state["analysis_sales"] = result.get("analysis", "")
        print(f"✅ Sales analysis completed")

    except Exception as e:
        print(f"❌ Error during sales analysis: {e}")
        state["analysis_sales"] = f"Analysis failed: {e}"
        return state
    
    return state

# --- Step 3: Combine analyses ---
def combine_analyses(state: CombinedState) -> CombinedState:
    api_key = os.getenv("GOOGLE_API_KEY")
    
    if not api_key:
        print("❌ Cannot analyze: GOOGLE_API_KEY not found")
        state["combined_analysis"] = "Analysis failed: API key not available"
        return state
    
    try:
        llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", api_key=api_key)
        if not (bool(state["analysis_finance"])) or not (bool(state["analysis_sales"])):
            print("⚠️  No analysis available for merging")
            state["combined_analysis"] = "Analysis failed: No financial or sales data available"
            return state

        prompt = f"""
        You are a Senior Business Advisory analyst who needs to generate a report containing information about your company's financial status and operation, and overall business suggestion.

        You have two analysis reports generated from financial statement and sales statement. Merge the two analysis reports into one comprehensive report.
        
        Financial Analysis:
        {state['analysis_finance']}

        Sales Analysis:
        {state['analysis_sales']}

        Please provide a clear, professional analysis with one paragraph each containing information about your company's financial status, their operation details, and overall business suggestion.
        """

        # print('DEBUG prompt:', prompt, '\n\n')
        print("🤖 Requesting AI combination from Gemini...")
        result = llm.invoke(prompt)
        state["combined_analysis"] = result.content
        print(f"✅ Combined analysis generated")
        return state

    except Exception as e:
        print(f"❌ Error when combining analysis data: {e}")
        state["combined_analysis"] = f"Analysis failed: {str(e)}"
        return state

# --- Build LangGraph (Using analyse and analyse_ba as submodules) ---
memory = MemorySaver()
builder = StateGraph(CombinedState)

builder.add_node("finance", run_financial_analysis)
builder.add_node("sales", run_sales_analysis)
builder.add_node("combined", combine_analyses)

builder.add_edge(START, "finance")
builder.add_edge("finance", "sales")
builder.add_edge("sales", "combined")
builder.add_edge("combined", END)

graph = builder.compile(checkpointer=memory)

# --- Main Execution ---
if __name__ == "__main__":
    print("🚀 Starting Business Statement Analysis...")
    print("=" * 50)
    
    # You can change this file path to analyze different PDFs
    pdf_file = "demo6_fs.pdf" # Finance
    xlsx_file = "data.xlsx" # Sales
    
    if not os.path.exists(xlsx_file) or not os.path.exists(pdf_file):
        print(f"❌ Missing either financial or sales data: {xlsx_file}")
        print("Please ensure the relevant files exist in the current directory")
        exit(1)
    
    try:
        config = {"configurable": {"thread_id": "combined_thread"}}
        
        state = graph.invoke(
            {
                "file_path_finance": pdf_file,
                "file_path_sales": xlsx_file
             }, config=config)
        
        print("\n" + "=" * 50)
        print("📊 ANALYSIS RESULTS")
        print("=" * 50)

        if state["analysis_finance"]:
            print("\n🤖 Extracted Financial Analysis:")
            print(state["analysis_finance"])
        else:
            print("\n⚠️  No financial analysis was extracted")

        if state["analysis_sales"]:
            print("\n🤖 Extracted Sales Analysis:")
            print(state["analysis_sales"])
        else:
            print("\n⚠️  No sales analysis was extracted")

        if state["combined_analysis"] and not state["combined_analysis"].startswith("Analysis failed"):
            print("\n🧠 Combined AI-Generated Analysis:")
            print(state["combined_analysis"])
        else:
            print(f"\n⚠️  Combined analysis failed")

    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        print("Please check your Excel file and ensure it's a valid financial statement")
