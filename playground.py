from dotenv import load_dotenv
load_dotenv()

from langchain.chat_models import init_chat_model
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt, Command
import os
import random
from datetime import datetime
import requests
from requests.exceptions import RequestException

class State(TypedDict):
    messages: Annotated[list, add_messages]

@tool
def get_payable() -> str:
    '''Return the payable amount from the API'''
    
    url = "https://asbk.mitcloud.com/v6-beta/v6IntegrationAPIlogin/getCashData"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    data = {
        "domain": "demo6",
        "prompt": "payable"
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=15)
        response.raise_for_status()
        response_json = response.json()
        print("API Response:", response_json)

        cash_str = response_json.get("AP amount")
        if not cash_str:
            print("Warning: 'payable' field not found.")
            return 'AP amount 0.0'

        return cash_str
        
    except RequestException as e:
        print(f"RequestException: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Status Code: {e.response.status_code}")
            print(f"Response Text: {e.response.text}")
        return 0.0
    except Exception as e:
        print(f"Unexpected Error: {e}")
        return 0.0
    
@tool
def get_cashbalance() -> str:
    '''Return the cash balance from the API'''
    
    url = "https://asbk.mitcloud.com/v6-beta/v6IntegrationAPIlogin/getCashData"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    data = {
        "domain": "demo6",
        "prompt": "cash"
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=15)
        response.raise_for_status()
        response_json = response.json()
        print("API Response:", response_json)

        cash_str = response_json.get("Cash balance")
        if not cash_str:
            print("Warning: 'cash Balance' field not found.")
            return 'cash balance 0.0'

        return cash_str
        
    except RequestException as e:
        print(f"RequestException: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Status Code: {e.response.status_code}")
            print(f"Response Text: {e.response.text}")
        return 0.0
    except Exception as e:
        print(f"Unexpected Error: {e}")
        return 0.0
    
@tool
def get_stock_price(symbol: str) -> float:
    #your API call to get stock price
    '''Return the current price of a stock given the stock symbol'''
    return {"MSFT": 200.3, "AAPL": 100.4, "AMZN": 150.0, "RIL": 87.6}.get(symbol, 0.0)

@tool
def buy_stocks(symbol: str, quantity: int, total_price: float) -> str:
    #your API call to buy stocks
    '''Buy stocks given the stock symbol and quantity'''
    decision = interrupt(f"Approve buying {quantity} {symbol} stocks for ${total_price:.2f}?")

    if decision == "yes":
        invoice_id = f"INV-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"
        return f"Your Invoice ID: {invoice_id} for a total price of {total_price}"
    else:
        return "Buying declined."


tools = [get_stock_price, buy_stocks, get_cashbalance, get_payable]
key = os.getenv("GOOGLE_API_KEY")

llm = init_chat_model("google_genai:gemini-2.0-flash",api_key=key)
llm_with_tools = llm.bind_tools(tools)

def chatbot_node(state: State):
    msg = llm_with_tools.invoke(state["messages"])
    return {"messages": [msg]}

memory = MemorySaver()
builder = StateGraph(State)
builder.add_node("chatbot", chatbot_node)
builder.add_node("tools", ToolNode(tools))
builder.add_edge(START, "chatbot")
builder.add_conditional_edges("chatbot", tools_condition)
builder.add_edge("tools", "chatbot")
builder.add_edge("chatbot", END)
graph = builder.compile(checkpointer=memory)

config = {"configurable": {"thread_id": "buy_thread"}}


state = None
while True:
    in_message = input("You: ")
    if in_message.lower() in {"quit","exit"}:
        break
    if state is None:
        state: State = {
            "messages": [{"role": "user", "content": in_message}]
        }
    else:
        state["messages"].append({"role": "user", "content": in_message})

    state = graph.invoke(state, config=config)
    print("Bot:", state["messages"][-1].content)
    
    '''who are you?
Bot: I am Gemini, a large language model built by Google.
You: what can you do
Bot: I can provide information, generate text, and translate languages. I can also access and use specific tools to help with tasks, such as retrieving stock prices or making stock trades.
You: check the price for AAPL
Bot: The current price for AAPL is 100.4.
You: how much if i buy 7 stock
Bot: The current price for AAPL is 100.4, so buying 7 stocks would cost 7 * 100.4 = 702.8.
You: my cash balance is enough to buy?
API Response: {}
Warning: 'cash Balance' field not found.
Bot: You have a cash balance of 0.0. Buying 7 stocks of AAPL would cost 702.8. So, you don't have enough cash balance to buy.
You: Who walked on the moon for the first time? Print only the name 
Bot: Neil Armstrong
You: what year
Bot: 1969
'''