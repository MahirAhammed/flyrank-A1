import os
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv

load_dotenv(dotenv_path= Path(__file__).resolve().parent.parent.parent / ".env.llm")

client = OpenAI(base_url= os.environ["LLM_BASE_URL"], api_key= os.environ["LLM_API_KEY"])

res = client.chat.completions.create(
        model= os.environ["LLM_MODEL"],
        messages= [{"role": "user", "content": "Reply with exactly the word: ready"}],
    )

print(res.choices[0].message.content)