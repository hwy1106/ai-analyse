from dotenv import load_dotenv
import os

load_dotenv()  # loads GOOGLE_API_KEY into environment
#print("CWD =", os.getcwd())
key = os.getenv("GOO_API_KEY")
from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", api_key=key)
print(llm.invoke("Hello Gemini"))
#print("GOOGLE_API_KEY =", os.getenv("GOO_API_KEY"))