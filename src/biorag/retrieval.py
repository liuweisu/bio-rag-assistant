"""BM25 retrieval written from scratch, plus optional dense and hybrid retrieval."""

from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass
from typing import Protocol

from .corpus import Chunk

STOPWORDS = set("""a an and are as at be by for from has have how in is it its of on or that the this to was
were which with what when where who why do does did can could would should their there these those than then
into about between over under not no yes also so such very more most other some any each per via using use used""".split())


def tokenize(text: str) -> list[str]:
    """Lowercase word tokens; keeps tokens like 'l1hs', 'n50', 'dna' and splits hyphenated terms."""
    tokens = re.findall(r"[a-z0-9]+", text.lower())
    return [_stem(t) for t in tokens if t not in STOPWORDS and len(t) > 1]


def _stem(t: str) -> str:
    # tiny suffix stripper: 'transposons' -> 'transposon', 'counts' -> 'count'
    for suf in ("ies", "es", "s"):
        if len(t) > 4 and t.endswith(suf) and not t.endswith("ss"):
            return t[: -len(suf)] + ("y" if suf == "ies" else "")
    return t


@dataclass(frozen=True)
class Hit:
    chunk: Chunk
    score: float
    rank: int


class Retriever(Protocol):
    def search(self, query: str, k: int = 5) -> list[Hit]: ...


class BM25:
    """Okapi BM25 (Robertson et al.): score = sum over query terms of
    idf(t) * tf * (k1 + 1) / (tf + k1 * (1 - b + b * len / avg_len))."""

    def __init__(self, chunks: list[Chunk], k1: float = 1.5, b: float = 0.75):
        self.chunks = chunks
        self.k1, self.b = k1, b
        self.doc_tokens = [tokenize(c.title + " " + c.text) for c in chunks]
        self.tf = [Counter(toks) for toks in self.doc_tokens]
        self.lengths = [len(t) for t in self.doc_tokens]
        self.avg_len = sum(self.lengths) / len(self.lengths)
        df: Counter[str] = Counter()
        for toks in self.doc_tokens:
            df.update(set(toks))
        n = len(chunks)
        self.idf = {t: math.log(1 + (n - d + 0.5) / (d + 0.5)) for t, d in df.items()}

    def scores(self, query: str) -> list[float]:
        q = tokenize(query)
        out = []
        for tf, length in zip(self.tf, self.lengths):
            s = 0.0
            for t in q:
                f = tf.get(t, 0)
                if f:
                    s += self.idf[t] * f * (self.k1 + 1) / (f + self.k1 * (1 - self.b + self.b * length / self.avg_len))
            out.append(s)
        return out

    def search(self, query: str, k: int = 5) -> list[Hit]:
        scored = sorted(enumerate(self.scores(query)), key=lambda x: x[1], reverse=True)[:k]
        return [Hit(self.chunks[i], s, r + 1) for r, (i, s) in enumerate(scored) if s > 0]

    def to_json(self) -> dict:
        """Everything a browser needs to run the same search (see docs/index.html)."""
        return {
            "k1": self.k1, "b": self.b, "avg_len": self.avg_len, "idf": self.idf,
            "chunks": [{"id": c.id, "title": c.title, "text": c.text, "tf": dict(tf), "len": n}
                       for c, tf, n in zip(self.chunks, self.tf, self.lengths)],
        }


class DenseRetriever:
    """Embedding search with sentence-transformers (optional dependency: pip install '.[dense]')."""

    def __init__(self, chunks: list[Chunk], model: str = "sentence-transformers/all-MiniLM-L6-v2"):
        from sentence_transformers import SentenceTransformer

        self.chunks = chunks
        self.model = SentenceTransformer(model)
        self.emb = self.model.encode([c.title + "\n" + c.text for c in chunks], normalize_embeddings=True)

    def search(self, query: str, k: int = 5) -> list[Hit]:
        q = self.model.encode([query], normalize_embeddings=True)[0]
        sims = self.emb @ q
        order = sims.argsort()[::-1][:k]
        return [Hit(self.chunks[i], float(sims[i]), r + 1) for r, i in enumerate(order)]


class HybridRetriever:
    """Reciprocal rank fusion: score = sum over retrievers of 1 / (c + rank)."""

    def __init__(self, retrievers: list[Retriever], c: int = 60, depth: int = 20):
        self.retrievers, self.c, self.depth = retrievers, c, depth

    def search(self, query: str, k: int = 5) -> list[Hit]:
        fused: dict[str, float] = {}
        by_id: dict[str, Chunk] = {}
        for r in self.retrievers:
            for h in r.search(query, self.depth):
                fused[h.chunk.id] = fused.get(h.chunk.id, 0.0) + 1 / (self.c + h.rank)
                by_id[h.chunk.id] = h.chunk
        best = sorted(fused.items(), key=lambda x: x[1], reverse=True)[:k]
        return [Hit(by_id[cid], s, i + 1) for i, (cid, s) in enumerate(best)]
