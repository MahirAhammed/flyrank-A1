import json
import os
from pathlib import Path

from fastapi import APIRouter, HTTPException

from task_analyzer.src.llm.llm_client import call_llm, recall_llm
from task_analyzer.src.llm.parser import parse_and_validate, CustomError
from task_analyzer.src.llm.schema import TextRequest, STUB_OUTPUT, TaskAnalysisResponse
from task_analyzer.src.llm.prompt import load_system_prompt

from task_analyzer.config import LLM_STUB

router = APIRouter(tags=["/llm"])
QUARANTINE_PATH = Path(__file__).parent.parent / "logs" / "quarantine.jsonl"

def _quarantine(input_text: str, version: str, error: str) -> None:
    QUARANTINE_PATH.parent.mkdir(exist_ok=True)
    log = {
        "input": input_text,
        "error": error,
        "prompt_version": version,
    }
    with open(QUARANTINE_PATH, "a") as f:
        f.write(json.dumps(log) + "\n")

@router.post("/task-analyzer")
async def analyze_text(req: TextRequest):
    if LLM_STUB == "1":
        return STUB_OUTPUT
    
    system_prompt, version = load_system_prompt("task_analyzer-v1.md")

    response = call_llm(system_prompt, req.text)
    try:
        return parse_and_validate(response)
    except CustomError as err1:
        new_response = recall_llm(system_prompt, req.text, response, str(err1))
        try:
            return parse_and_validate(new_response)
        except CustomError as err2:
            _quarantine(req.text, version, str(err2))
            
            raise HTTPException(
                status_code=422, detail="Model output failed validation."
            ) from err2