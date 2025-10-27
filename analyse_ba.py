from dotenv import load_dotenv
import os
import re
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_google_genai import ChatGoogleGenerativeAI
from pypdf import PdfReader
from collections import Counter
import pandas as pd

load_dotenv()

# Check if API key is available
if not os.getenv("GOOGLE_API_KEY"):
    print("⚠️  Warning: GOOGLE_API_KEY not found in environment variables")
    print("Please set your Google API key in a .env file or environment variable")

# --- Define State ---
class StatementState(TypedDict):
    file_path: str
    text: str
    metrics: dict
    ratios: dict
    analysis: str

# --- Step 1: Read and extract totals from xlsx ---
def read_statement(state: StatementState) -> StatementState:
    # Currently accepting xlsx only, check for pdf compatability
    try:
        df = pd.read_excel(state["file_path"])
        # print('Debugging df headers', list(df.columns.values))

        #Insert warning if no extraction
        # print(f"⚠️  Warning: Could not extract text from page: {e}")
        #         continue
        print(f"✅ Successfully extracted dataframe from Excel")

        # Select rows that contain Sales
        filtered_rows = df[df['Item Name'].str.contains(r'sales', case=False, na=False)]
        # print('Debugging', filtered_rows)

            
        # state["text"] = text
        # text = df.iloc[0].to_string()
        

        # Extract key totals from your PDF
        # metrics = {}
        # patterns = {
        #     "Total Revenue": r"Total Revenue\s+([\d,]+\.\d+)",
        #     "Total Cost of Sales": r"Total Cost of sales\s+\(([\d,]+\.\d+)\)",
        #     "Profit Before Tax": r"Profit Before Tax\s+([\d,]+\.\d+)",
        #     "Total Expenses": r"Total Expenses\s+\(([\d,]+\.\d+)\)",
        #     "Net Profit": r"Net Profit/\(Loss\)\s+([\d,]+\.\d+)",
        #     "Income Tax Expenses": r"Income Tax Expenses\s+([\d,]+\.\d+)",
        #     "Profit For the Year": r"Profit For the Year\s+([\d,]+\.\d+)"
        # }

        # patterns = {
            # "Sales": r"Sales\s+([\d,]+\.\d+)",
            # "Total Cost of Sales": r"Total Cost of sales\s+\(([\d,]+\.\d+)\)",
            # "Profit Before Tax": r"Profit Before Tax\s+([\d,]+\.\d+)",
            # "Total Expenses": r"Total Expenses\s+\(([\d,]+\.\d+)\)",
            # "Net Profit": r"Net Profit/\(Loss\)\s+([\d,]+\.\d+)",
            # "Income Tax Expenses": r"Income Tax Expenses\s+([\d,]+\.\d+)",
            # "Profit For the Year": r"Profit For the Year\s+([\d,]+\.\d+)"
        # }

        # for key, pattern in patterns.items():
        #     match = re.search(pattern, text, re.IGNORECASE)

        #     if match:
        #         try:
        #             value = float(match.group(1).replace(",", ""))
        #             metrics[key] = value
        #             print(f"✅ Found {key}: {value}")
        #         except ValueError:
        #             print(f"⚠️  Could not parse value for {key}: {match.group(1)}")
        #     else:
        #         print(f"⚠️  Could not find {key}")

        state["metrics"] = filtered_rows.to_dict()
        # print('test state after converting from df', state["metrics"])
        return state
        
    except Exception as e:
        print(f"❌ Error reading PDF: {e}")
        state["text"] = ""
        state["metrics"] = {}
        return state

# --- Step 2: Calculate Financial Ratios ---
def calculate_ratios(state: StatementState) -> StatementState:
    m = state["metrics"]
    ratios = {}
    
    print(f"\n📊 Calculating ratios from {len(m)} metrics...")
    # print('Debugging calculate_ratios\n', m)

    # Collect all total sale value (List)
    if "Total Sale Value" in m:
        try:
            ratios["Total Sale"] = sum(m["Total Sale Value"].values())
            # print(ratios["Total Sale"])
            print(f"✅ Extracted Sales Data: {ratios['Total Sale']}")
        except:
            print("⚠️  Cannot extract Total Sale data")

    # Collect all total units sold? Skip for now

    # Sales + units sold per month(? <- To show growth in analyze_statement) Skip for now

    # Collect channel + revenue
    if "Channel" in m and "Total Sale Value" in m:
        try:
            #This portion unusable because type changed to dictionary instead of pandas df
            # channel_df = (
            #     m.groupby("Channel")["Total Sale Value"]   #  Key = Channel
            #     .sum()                                     #  Value = Total Sale Value 
            #     .reset_index()
            # )
            
            ratios["Channel Data"] = dict(zip(m["Channel"].values(), m["Total Sale Value"].values()))
            print(f"✅ Calculated Channel Data: {ratios['Channel Data']}")
        except:
            print("⚠️  Cannot generate Channel data")
    
    # Collect salesperson + revenue  
    if "Salesperson" in m and "Total Sale Value" in m:
        try:
            ratios["Salesperson Data"] = dict(zip(m["Salesperson"].values(), m["Total Sale Value"].values()))
            print(f"✅ Calculated Salesperson Data: {ratios['Salesperson Data']}")
        except:
            print("⚠️  Cannot generate Salesperson data")      
    
    # Collect customers (List)
    if "Customer ID" in m:
        try:
            id_list = list(m["Customer ID"].values())
            ratios["Customer ID Counter"] = Counter(id_list)
            print(f"✅ Extracted Customer Data: {ratios['Customer ID Counter']}")
        except:
            print("⚠️  Cannot extract Customer ID data")

    state["ratios"] = ratios
    print(f"📈 Calculated {len(ratios)} financial ratios")
    return state

# --- Step 3: Analyze with Gemini ---
def analyze_statement(state: StatementState) -> StatementState:
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ Cannot analyze: GOOGLE_API_KEY not found")
        state["analysis"] = "Analysis failed: API key not available"
        return state
    
    try:
        llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", api_key=api_key)
        
        if not (bool(state["metrics"])) or not (bool(state["ratios"])):
            print("⚠️  No metrics or ratios available for analysis")
            state["analysis"] = "Analysis failed: No financial data available"
            return state
        
        prompt = f"""
        You are a Senior Business Advisory analyst. 
        Using the following business advisory data, generate an analysis report and some summary text. Make sure you provide:
        - Executive summary (Total sales, growth, standout performers)
        - Sales performance analysis (Salesperson that generated most revenue and who are the customers)
        - Cost efficiency analysis (Channel that performed best)
        - Product/Service insight
        - Actionable recommendations

        Extracted Metrics:
        {state['metrics']}

        Calculated Ratios:
        {state['ratios']}
        
        Please provide a clear, professional analysis in 3-4 paragraphs.
        """
        # print('DEBUGGING PROMPT\n', prompt, '\nEND OF PROMPT\n')
        
        print("🤖 Requesting AI analysis from Gemini...")
        result = llm.invoke(prompt)
        state["analysis"] = result.content
        print("✅ AI analysis completed successfully")
        return state
        
    except Exception as e:
        print(f"❌ Error during AI analysis: {e}")
        state["analysis"] = f"Analysis failed: {str(e)}"
        return state

# --- Build LangGraph ---
memory = MemorySaver()
builder = StateGraph(StatementState)
builder.add_node("read", read_statement)
builder.add_node("ratios", calculate_ratios)
builder.add_node("analyze", analyze_statement)

builder.add_edge(START, "read")
builder.add_edge("read", "ratios")
builder.add_edge("ratios", "analyze")
builder.add_edge("analyze", END)
graph = builder.compile(checkpointer=memory)

# --- Main Execution ---
if __name__ == "__main__":
    print("🚀 Starting Financial Statement Analysis...")
    print("=" * 50)
    
    # You can change this file path to analyze different PDFs
    # pdf_file = "demo6_fs.pdf"
    # pdf_file = "SME_Business_Advisory_Template.pdf"
    xlsx_file = "data.xlsx"
    
    if not os.path.exists(xlsx_file):
        print(f"❌ PDF file not found: {xlsx_file}")
        print("Please ensure the PDF file exists in the current directory")
        exit(1)
    
    print(f"📄 Analyzing xlsx: {xlsx_file}")
    
    try:
        config = {"configurable": {"thread_id": "analysis_thread"}}
        state = graph.invoke({"file_path": xlsx_file}, config=config)
        
        print("\n" + "=" * 50)
        print("📊 ANALYSIS RESULTS")
        print("=" * 50)

        print('Test metrics', state["metrics"])
        if state["metrics"]:
            print("\n💰 Extracted Financial Metrics:")
            print(state["metrics"])
        else:
            print("\n⚠️  No financial metrics were extracted")
        
        print('Test ratios')
        if state["ratios"]:
            print("\n📈 Calculated Financial Ratios:")
            for key, value in state["ratios"].items():
                print(f"   {key}: {value}")
        else:
            print("\n⚠️  No financial ratios were calculated")
        
        print('a')
        if state["analysis"] and not state["analysis"].startswith("Analysis failed"):
            print("\n🤖 AI-Generated Analysis:")
            print("-" * 30)
            print(state["analysis"])
        else:
            print(f"\n❌ Analysis failed: {state['analysis']}")
            
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        print("Please check your PDF file and ensure it's a valid financial statement")
