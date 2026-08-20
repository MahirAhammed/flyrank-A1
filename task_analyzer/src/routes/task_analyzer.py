from fastapi import APIRouter
from task_analyzer.src.llm.schema import TextRequest, STUB_OUTPUT
from task_analyzer.config import LLM_STUB

router = APIRouter(tags=["/llm"])

@router.post("/task-analyzer")
async def analyze_text(req: TextRequest):
    if LLM_STUB == "1":
        return STUB_OUTPUT
    
    return {"status": "Coming soon..."}