"""Wire a retriever and an answerer together."""

from __future__ import annotations

import os
from dataclasses import dataclass

from .corpus import DEFAULT_CORPUS, load_corpus
from .generate import Answer, Answerer, ClaudeAnswerer, ExtractiveAnswerer
from .retrieval import BM25, Hit, Retriever


@dataclass
class Result:
    question: str
    answer: Answer
    hits: list[Hit]


class RAG:
    def __init__(self, retriever: Retriever, answerer: Answerer, k: int = 4):
        self.retriever, self.answerer, self.k = retriever, answerer, k

    def ask(self, question: str) -> Result:
        question = question.strip()
        if not question:
            raise ValueError("empty question")
        hits = self.retriever.search(question, self.k)
        return Result(question, self.answerer.answer(question, hits), hits)


def has_claude_credentials() -> bool:
    return bool(os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN") or os.environ.get("ANTHROPIC_PROFILE"))


def build(mode: str = "auto", corpus: str = str(DEFAULT_CORPUS), k: int = 4) -> RAG:
    """mode: 'claude', 'extractive', or 'auto' (Claude if credentials are configured)."""
    retriever = BM25(load_corpus(corpus))
    if mode == "auto":
        mode = "claude" if has_claude_credentials() else "extractive"
    answerer: Answerer = ClaudeAnswerer() if mode == "claude" else ExtractiveAnswerer(idf=retriever.idf)
    return RAG(retriever, answerer, k)
