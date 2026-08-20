# Task Analyzer API

Takes a plain-English task description and returns a structured, validated classification: category, priority, time estimate, actionability, and a confidence score. See `JOB-CARD.md` for the full spec.

## Demo Requests
###### Valid request:
```bash
curl -s -X POST http://127.0.0.1:8000/task-analyzer \
  -H "Content-Type: application/json" \
  -d '{"text": "Buy new running shoes before Saturdays 10k"}'
```

###### Invalid request:
```bash
curl -s -X POST http://127.0.0.1:8000/task-analyzer \
  -H "Content-Type: application/json" \
  -d '{"title": "hi"}'
```

- Output (Status 400):
```json
{"error": "validation_failed", "field": "text", "message": "Field required"}
```

## Provider Configuration
The difference between running a model on local PC and in a datacentre is `LLM_BASE_URL`, `LLM_API_KEY`, and `LLM_MODEL`, which is why providers should never be hard-coded.
