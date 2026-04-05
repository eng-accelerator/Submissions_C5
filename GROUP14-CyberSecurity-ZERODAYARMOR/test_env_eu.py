import os
from dotenv import load_dotenv

load_dotenv(override=True)

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_ENDPOINT"] = "https://eu.api.smith.langchain.com"
os.environ["LANGCHAIN_PROJECT"] = "ZeroDayArmor_Local"

print("\nExecuting Trace Call directly to 'ZeroDayArmor_Local' project using EUROPEAN Endpoint...")
from langchain_openai import ChatOpenAI

or_key = os.environ.get("OPENROUTER_API_KEY", "")
llm = ChatOpenAI(base_url="https://openrouter.ai/api/v1", api_key=or_key, model="openai/gpt-4o-mini", max_tokens=10)

try:
    res = llm.invoke("Testing trace export loop")
    print(f"\nModel output success: {res.content}")
except Exception as e:
    print(f"\nTrace Error Encountered: {e}")
