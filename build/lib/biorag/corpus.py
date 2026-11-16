"""Load markdown notes and split them into section-sized chunks."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path


def _default_dir(name: str, env: str) -> Path:
    """$ENV, else the folder next to the source tree (editable install), else ./<name>."""
    if os.environ.get(env):
        return Path(os.environ[env])
    repo = Path(__file__).resolve().parents[2] / name
    return repo if repo.exists() else Path.cwd() / name


DEFAULT_CORPUS = _default_dir("corpus", "BIORAG_CORPUS")


@dataclass(frozen=True)
class Chunk:
    id: str  # "<doc>#<section-slug>"
    doc: str  # file stem
    title: str  # "Document title > Section"
    text: str

    def __len__(self) -> int:
        return len(self.text.split())


def _slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def split_markdown(doc: str, text: str, max_words: int = 220) -> list[Chunk]:
    """One chunk per ``##`` section; long sections are split on paragraph boundaries.

    The document title is kept in every chunk's title, so a chunk still makes
    sense on its own when it is retrieved without its neighbours.
    """
    lines = text.strip().splitlines()
    doc_title = lines[0].lstrip("# ").strip() if lines and lines[0].startswith("# ") else doc
    sections: list[tuple[str, list[str]]] = [("Introduction", [])]
    for line in lines[1:]:
        if line.startswith("## "):
            sections.append((line[3:].strip(), []))
        else:
            sections[-1][1].append(line)
    chunks: list[Chunk] = []
    for heading, body in sections:
        paragraphs = [p.strip() for p in "\n".join(body).split("\n\n") if p.strip()]
        if not paragraphs:
            continue
        part: list[str] = []
        n = 0
        for para in paragraphs:
            words = len(para.split())
            if part and n + words > max_words:
                chunks.append(_make(doc, doc_title, heading, part, len(chunks)))
                part, n = [], 0
            part.append(para)
            n += words
        chunks.append(_make(doc, doc_title, heading, part, len(chunks)))
    return chunks


def _make(doc: str, doc_title: str, heading: str, paragraphs: list[str], i: int) -> Chunk:
    return Chunk(id=f"{doc}#{_slug(heading)}-{i}", doc=doc, title=f"{doc_title} > {heading}", text="\n\n".join(paragraphs))


def load_corpus(path: str | Path = DEFAULT_CORPUS, max_words: int = 220) -> list[Chunk]:
    chunks: list[Chunk] = []
    for f in sorted(Path(path).glob("*.md")):
        chunks.extend(split_markdown(f.stem, f.read_text(), max_words))
    if not chunks:
        raise FileNotFoundError(f"no markdown files in {path}")
    return chunks
