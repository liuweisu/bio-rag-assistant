"""Evaluate retrieval and answers against eval/questions.jsonl.

Retrieval: recall@k and MRR over the answerable questions (did the right note come back?).
Answers: does the answer contain one of the expected facts, does it cite the right note,
and does the system abstain on questions the notes cannot answer?
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from .corpus import _default_dir
from .pipeline import RAG

DEFAULT_QUESTIONS = _default_dir("eval", "BIORAG_EVAL_DIR") / "questions.jsonl"


def load_questions(path: str | Path = DEFAULT_QUESTIONS) -> list[dict]:
    return [json.loads(line) for line in Path(path).read_text().splitlines() if line.strip()]


@dataclass
class RetrievalReport:
    n: int
    recall_at_1: float
    recall_at_k: float
    mrr: float
    k: int
    misses: list[str]


def evaluate_retrieval(rag: RAG, questions: list[dict], k: int = 4) -> RetrievalReport:
    qs = [q for q in questions if q["answerable"]]
    r1 = rk = rr = 0.0
    misses = []
    for q in qs:
        docs = [h.chunk.doc for h in rag.retriever.search(q["question"], k)]
        ranks = [i + 1 for i, d in enumerate(docs) if d in q["relevant_docs"]]
        if ranks:
            rk += 1
            rr += 1 / ranks[0]
            r1 += ranks[0] == 1
        else:
            misses.append(q["id"])
    n = len(qs)
    return RetrievalReport(n, r1 / n, rk / n, rr / n, k, misses)


@dataclass
class AnswerReport:
    n_answerable: int
    n_unanswerable: int
    fact_accuracy: float  # answerable: answer mentions an expected fact
    citation_accuracy: float  # answerable: a citation points to a relevant note
    false_abstention: float  # answerable questions the system refused
    correct_abstention: float  # unanswerable questions the system refused
    rows: list[dict]


def evaluate_answers(rag: RAG, questions: list[dict]) -> AnswerReport:
    rows = []
    for q in questions:
        res = rag.ask(q["question"])
        a = res.answer
        text = a.text.lower()
        rows.append({
            "id": q["id"],
            "answerable": q["answerable"],
            "abstained": a.abstained,
            "fact": (not a.abstained) and any(f.lower() in text for f in q["facts_any"]),
            "cited_relevant": any(c.chunk_id.split("#")[0] in q["relevant_docs"] for c in a.citations),
            "answer": a.text,
        })
    ans = [r for r in rows if r["answerable"]]
    una = [r for r in rows if not r["answerable"]]
    mean = lambda xs: sum(xs) / len(xs) if xs else 0.0  # noqa: E731
    return AnswerReport(
        n_answerable=len(ans),
        n_unanswerable=len(una),
        fact_accuracy=mean([r["fact"] for r in ans]),
        citation_accuracy=mean([r["cited_relevant"] for r in ans]),
        false_abstention=mean([r["abstained"] for r in ans]),
        correct_abstention=mean([r["abstained"] for r in una]),
        rows=rows,
    )
