import os
from langchain_google_genai import ChatGoogleGenerativeAI

os.environ["GOOGLE_API_KEY"] = "API_KEY"

llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
