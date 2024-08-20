from langchain_openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")

chat_model = OpenAI(openai_api_key = API_KEY)

result = chat_model.predict("Hello there chat")

print(result)