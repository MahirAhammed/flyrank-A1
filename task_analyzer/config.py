import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(dotenv_path= find_dotenv(".env.llm"))

LLM_BASE_URL = os.environ["LLM_BASE_URL"]
LLM_API_KEY = os.environ["LLM_API_KEY"]
LLM_MODEL = os.environ["LLM_MODEL"]
LLM_STUB = os.getenv("LLM_STUB", "1")
LLM_ENABLED = os.getenv("LLM_ENABLED", "true").lower() != "false"