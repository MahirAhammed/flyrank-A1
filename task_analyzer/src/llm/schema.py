from pydantic import BaseModel, field_validator, Field
from enum import Enum

class TextRequest(BaseModel):
    text: str = Field(..., min_length= 3, max_length= 200)

    @field_validator("text")
    @classmethod
    def validate_length(cls, value: str) -> str:
        if len("".join(value.split())) > 200:
            raise ValueError("Maximum 200 non-whitespace characters allowed")
        return value

class Category(Enum):
    WORK = "work"
    PERSONAL = "personal"
    ACADEMIC = "academic"
    SHOPPING = "shopping"
    FITNESS = "fitness"
    OTHER = "other"

class Priority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class EstimatedMinutes(Enum):
    five = 5
    ten = 10
    fifteen = 15
    thirty = 30
    sixty = 60
    one_twenty = 120
    one_eighty = 180

class TaskAnalysisResponse(BaseModel):
    title: str = Field(..., max_length= 100)
    category: Category
    priority: Priority
    estimated_minutes: EstimatedMinutes
    is_actionable: bool
    confidence: float


STUB_OUTPUT = TaskAnalysisResponse(
    title="Implement LLM model for analysis",
    category=Category.WORK,
    priority=Priority.HIGH,
    estimated_minutes=EstimatedMinutes.thirty,
    is_actionable=True,
    confidence=0.9,
)
