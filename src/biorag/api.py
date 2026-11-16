"""HTTP API: uvicorn biorag.api:app --port 8000"""

from __future__ import annotations

from functools import lru_cache

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from . import __version__
from .pipeline import RAG, build


class AskRequest(BaseModel):
    question: str = Field(min_length=3, max_length=500)


class CitationOut(BaseModel):
    chunk_id: str
    title: str
    quote: str


class AskResponse(BaseModel):
    answer: str
    abstained: bool
    citations: list[CitationOut]
    sources: list[str]
    model: str


app = FastAPI(title="bio-rag-assistant", version=__version__)
# allow the portfolio website to call the API from the browser
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["GET", "POST"], allow_headers=["*"])


@lru_cache(maxsize=1)
def get_rag() -> RAG:
    return build()


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "version": __version__}


@app.get("/search")
def search(q: str = Query(min_length=2, max_length=300), k: int = Query(5, ge=1, le=20)) -> list[dict]:
    return [{"id": h.chunk.id, "title": h.chunk.title, "score": round(h.score, 3), "text": h.chunk.text}
            for h in get_rag().retriever.search(q, k)]


@app.post("/ask", response_model=AskResponse)
def ask(req: AskRequest) -> AskResponse:
    try:
        result = get_rag().ask(req.question)
    except RuntimeError as e:  # upstream API problems
        raise HTTPException(status_code=503, detail=str(e)) from e
    a = result.answer
    return AskResponse(
        answer=a.text,
        abstained=a.abstained,
        citations=[CitationOut(**c.__dict__) for c in a.citations],
        sources=[h.chunk.id for h in result.hits],
        model=a.model,
    )
