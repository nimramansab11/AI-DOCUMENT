from pathlib import Path
import traceback
from fastapi.staticfiles import StaticFiles

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from .rag_service import RAGService
from .llm_service import LLMService
from .prompts import get_prompt

from .models import (
    QuestionRequest,
    QuestionResponse,
    IngestionResponse,
)


app = FastAPI(
    title="AI Document Question Answering System",
    description=(
        "AI-powered document Q&A system using "
        "RAG, embeddings, semantic search, ChromaDB, "
        "and prompt engineering."
    ),
    version="2.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


rag_service = RAGService()
llm_service = LLMService()

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"

app.mount(
    "/static",
    StaticFiles(directory=STATIC_DIR),
    name="static"
)


@app.get("/")
def home():
    return FileResponse(
        STATIC_DIR / "index.html"
    )


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "documents_chunks": rag_service.count(),
        "database": "ChromaDB",
        "embedding_model": "all-MiniLM-L6-v2",
        "llm": "Gemini",
    }


@app.post(
    "/ingest",
    response_model=IngestionResponse
)
def ingest_documents():

    try:
        chunks_added = rag_service.ingest_documents()

        return {
            "message": "Documents successfully processed.",
            "chunks_added": chunks_added,
        }

    except Exception as e:

        print("\n========== INGEST ERROR ==========")
        traceback.print_exc()
        print("==================================\n")

        raise HTTPException(
            status_code=500,
            detail=f"{type(e).__name__}: {str(e)}"
        )


@app.post("/search")
def search_documents(request: QuestionRequest):

    try:
        results = rag_service.search(
            question=request.question,
            top_k=request.top_k,
        )

        return {
            "question": request.question,
            "results": results,
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@app.post(
    "/ask",
    response_model=QuestionResponse
)
def ask_question(request: QuestionRequest):

    try:

        # 1. Retrieve relevant chunks
        results = rag_service.search(
            question=request.question,
            top_k=request.top_k,
        )

        if not results:
            raise HTTPException(
                status_code=404,
                detail="No relevant documents found."
            )

        # 2. Build context
        context_parts = []

        for item in results:

            context_parts.append(
                f"Source: {item['source']}\n"
                f"Chunk: {item['chunk']}\n"
                f"Content:\n{item['content']}"
            )

        context = "\n\n---\n\n".join(
            context_parts
        )

        # 3. Select prompting technique
        prompt = get_prompt(
            prompt_type=request.prompt_type,
            context=context,
            question=request.question
        )

        # 4. Generate AI answer
        answer = llm_service.generate(prompt)

        # 5. Return answer + retrieved chunks
        return {
            "answer": answer,
            "prompt_type": request.prompt_type,
            "retrieved_chunks": results,
        }

    except HTTPException:
        raise

    except Exception as e:

        print("\n========== ASK ERROR ==========")
        traceback.print_exc()
        print("================================\n")

        raise HTTPException(
            status_code=500,
            detail=f"{type(e).__name__}: {str(e)}"
        )