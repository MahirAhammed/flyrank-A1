from fastapi import APIRouter
from task_analyzer.src.llm.schema import TextRequest, STUB_OUTPUT
from task_analyzer.config import LLM_STUB
from task_analyzer.src.llm.llm_client import call_llm
from task_analyzer.src.llm.prompt import load_system_prompt

router = APIRouter(tags=["/llm"])

@router.post("/task-analyzer")
async def analyze_text(req: TextRequest):
    if LLM_STUB == "1":
        return STUB_OUTPUT
    
    response = call_llm(load_system_prompt(), req.text)
    return {"response": response}