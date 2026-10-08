from pydantic import BaseModel, Field
from typing import Optional


class QuestionRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        description="Question to ask about the uploaded documents"
    )

    top_k: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Number of document chunks to retrieve"
    )

    prompt_type: str = Field(
        default="zero-shot",
        description="Prompting technique"
    )


class RetrievedChunk(BaseModel):
    content: str
    source: Optional[str] = None
    chunk: Optional[int] = None
    distance: float


class QuestionResponse(BaseModel):
    answer: str
    prompt_type: str
    retrieved_chunks: list[RetrievedChunk]


class IngestionResponse(BaseModel):
    message: str
    chunks_added: int