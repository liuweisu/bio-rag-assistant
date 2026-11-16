"""Turn retrieved chunks into an answer: with Claude (cited) or offline (extractive)."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from typing import Any, Protocol

from .retrieval import Hit, tokenize

ABSTAIN = "NOT_IN_SOURCES"
DEFAULT_MODEL = "claude-opus-5-5"

SYSTEM_PROMPT = f"""You answer questions for bioinformaticians using only the documents provided in the user turn.

- Base every statement on the documents and cite them. Do not add facts from memory, even if you know them.
- If the documents do not contain the answer, reply with exactly {ABSTAIN} and nothing else. A partial answer is fine
  if you say what is missing.
- Answer in two to five sentences of plain prose. Keep numbers, gene names and tool names exactly as written in the documents."""


@dataclass
class Citation:
    chunk_id: str
    title: str
    quote: str


@dataclass
class Answer:
    text: str
    citations: list[Citation] = field(default_factory=list)
    abstained: bool = False
    model: str = ""
    usage: dict[str, int] = field(default_factory=dict)


class Answerer(Protocol):
    def answer(self, question: str, hits: list[Hit]) -> Answer: ...


class ExtractiveAnswerer:
    """No LLM: return the sentences that best match the question, or abstain.

    Useful offline, in tests and CI, and as a baseline: if an LLM does not beat
    this, the retrieval is doing all the work.

    It abstains when the best passage covers too little of the question's
    information (idf-weighted share of question terms found in the passage).
    Terms that never occur in the notes count with the highest idf, so a
    question about "annealing temperature" is not answered from a passage
    that only shares the word "primer".
    """

    def __init__(self, idf: dict[str, float] | None = None, min_coverage: float = 0.6, min_score: float = 4.0,
                 n_sentences: int = 2):
        self.idf = idf or {}
        self.unknown_idf = max(self.idf.values(), default=1.0)
        self.min_coverage, self.min_score, self.n_sentences = min_coverage, min_score, n_sentences

    def _w(self, term: str) -> float:
        return self.idf.get(term, self.unknown_idf)

    def coverage(self, question: str, text: str) -> float:
        q = set(tokenize(question))
        if not q:
            return 0.0
        found = q & set(tokenize(text))
        return sum(self._w(t) for t in found) / sum(self._w(t) for t in q)

    def answer(self, question: str, hits: list[Hit]) -> Answer:
        refuse = Answer("I could not find this in the notes.", abstained=True, model="extractive")
        if not hits or hits[0].score < self.min_score:
            return refuse
        if self.coverage(question, hits[0].chunk.title + " " + hits[0].chunk.text) < self.min_coverage:
            return refuse
        q = set(tokenize(question))
        candidates = []
        for h in hits[:3]:
            for sent in re.split(r"(?<!\bal\.)(?<=[.!?])\s+(?=[A-Z])", h.chunk.text.replace("\n", " ")):
                weight = sum(self._w(t) for t in q & set(tokenize(sent)))
                if weight:
                    candidates.append((weight / h.rank, sent.strip(), h))
        if not candidates:
            return refuse
        best = sorted(candidates, key=lambda c: c[0], reverse=True)[: self.n_sentences]
        return Answer(
            text=" ".join(s for _, s, _ in best),
            citations=[Citation(h.chunk.id, h.chunk.title, s) for _, s, h in best],
            model="extractive",
        )


class ClaudeAnswerer:
    """Grounded answers with the Claude API's built-in citations.

    Each retrieved chunk is sent as a separate ``document`` block with
    citations enabled, so every cited sentence points back to the exact
    passage it came from. Credentials come from the environment
    (ANTHROPIC_API_KEY or an ``ant auth login`` profile).
    """

    def __init__(self, client: Any | None = None, model: str | None = None, effort: str = "low"):
        if client is None:
            import anthropic

            client = anthropic.Anthropic()
        self.client = client
        self.model = model or os.environ.get("BIORAG_MODEL", DEFAULT_MODEL)
        self.effort = effort  # short grounded answers do not need deep reasoning

    def _request(self, question: str, hits: list[Hit]) -> Any:
        documents = [
            {
                "type": "document",
                "source": {"type": "text", "media_type": "text/plain", "data": h.chunk.text},
                "title": h.chunk.title,
                "citations": {"enabled": True},
            }
            for h in hits
        ]
        return self.client.beta.messages.create(
            model=self.model,
            max_tokens=16000,
            system=SYSTEM_PROMPT,
            output_config={"effort": self.effort},
            # if a safety classifier declines, the API retries on a fallback model in the same call
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
            messages=[{"role": "user", "content": [*documents, {"type": "text", "text": question}]}],
        )

    def answer(self, question: str, hits: list[Hit]) -> Answer:
        if not hits:
            return Answer("No relevant notes were found.", abstained=True, model=self.model)
        import anthropic

        try:
            response = self._request(question, hits)
        except anthropic.RateLimitError as e:
            raise RuntimeError("Rate limited by the Claude API; try again shortly") from e
        except anthropic.APIStatusError as e:
            raise RuntimeError(f"Claude API error {e.status_code}: {e.message}") from e
        except anthropic.APIConnectionError as e:
            raise RuntimeError("Could not reach the Claude API") from e

        usage = {"input_tokens": response.usage.input_tokens, "output_tokens": response.usage.output_tokens}
        if response.stop_reason == "refusal":
            return Answer("The model declined to answer this question.", abstained=True, model=response.model, usage=usage)

        text_parts: list[str] = []
        citations: list[Citation] = []
        for block in response.content:
            if block.type != "text":  # thinking and fallback blocks are not part of the answer
                continue
            text_parts.append(block.text)
            for c in getattr(block, "citations", None) or []:
                hit = hits[c.document_index]
                citations.append(Citation(hit.chunk.id, hit.chunk.title, c.cited_text.strip()))
        text = "".join(text_parts).strip()
        abstained = text.startswith(ABSTAIN)
        if abstained:
            text = "I could not find this in the notes."
        return Answer(text, citations, abstained, response.model, usage)
