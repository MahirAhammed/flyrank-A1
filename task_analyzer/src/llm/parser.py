import json
from pydantic import ValidationError
from task_analyzer.src.llm.schema import TaskAnalysisResponse

# ```json\n{\n  \"title\": \"Complete Assignment A9\",\n  \"category\": \"work\",\n  \"priority\": \"high\",\n  \"estimated_minutes\": 180,\n  \"is_actionable\": true,\n  \"confidence\": 0.95\n}\n```

class CustomError(Exception):
    """Base eror class to handle invalid TaskAnalysisResponse from raw output."""

    def __init__(self, message: str, model_output: str):
        super().__init__(message)
        self.model_output = model_output

class ParseError(CustomError):
    """Raw text was not parseable JSON at all."""

class SchemaValidationError(CustomError):
    """Parsed fine, but does not match TaskAnalysisResponse schema."""


def parse_and_validate(text: str) ->  TaskAnalysisResponse:
    data = _parse_json_object(text)
    try:
        return TaskAnalysisResponse.model_validate(data)
    except ValidationError as e:
        raise SchemaValidationError(str(e), text) from e


def _parse_json_object(text: str) -> dict:

    if not text or not text.strip():
        raise ParseError("Empty response from model.", text)

    content = _extract_first_json_object(text)
    if content is None:
        raise ParseError("No JSON object found in model output.", text)

    try:
        return json.loads(content)
    except json.JSONDecodeError as exc:
        raise ParseError(f"Extracted text is not valid JSON: {exc}", text) from exc


def _extract_first_json_object(text: str) -> str | None:

    start = text.find("{")
    # if start == -1:
    #     return None

    depth = 0           # variable to track down the matching closing curly brace
    in_string = False   # to track whether a char is part of a string
    next_escape = False # to handle escape character in strings

    for i in range(start, len(text)):
        char = text[i]
        if next_escape:
            next_escape = False
            continue
        if char == "\\" and in_string:
            next_escape = True
            continue
        if char == '"':
            in_string = not in_string
            continue
        if in_string:
            continue
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[start : i + 1]

    return None