"""biorag {ask, search, eval, export-index}"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .corpus import load_corpus
from .evaluate import evaluate_answers, evaluate_retrieval, load_questions
from .pipeline import build
from .retrieval import BM25


def main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser(prog="biorag")
    p.add_argument("--version", action="version", version=__version__)
    sub = p.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("ask", help="answer a question with citations")
    a.add_argument("question")
    a.add_argument("--mode", choices=["auto", "claude", "extractive"], default="auto")
    s = sub.add_parser("search", help="show the retrieved passages only")
    s.add_argument("query")
    s.add_argument("-k", type=int, default=5)
    e = sub.add_parser("eval", help="run the evaluation set")
    e.add_argument("--mode", choices=["auto", "claude", "extractive"], default="extractive")
    e.add_argument("--retrieval-only", action="store_true")
    e.add_argument("--save", help="write per-question results to this JSON file")
    x = sub.add_parser("export-index", help="write the BM25 index as JSON for the browser demo")
    x.add_argument("out")
    args = p.parse_args(argv)

    if args.cmd == "ask":
        res = build(args.mode).ask(args.question)
        print(res.answer.text, "\n")
        for i, c in enumerate(res.answer.citations, 1):
            print(f"[{i}] {c.title}\n    \"{c.quote}\"")
        print(f"\n(model: {res.answer.model}; retrieved: {', '.join(h.chunk.id for h in res.hits)})", file=sys.stderr)
    elif args.cmd == "search":
        for h in build("extractive").retriever.search(args.query, args.k):
            print(f"{h.rank}. [{h.score:.2f}] {h.chunk.title}\n   {h.chunk.text[:160].replace(chr(10), ' ')}...")
    elif args.cmd == "eval":
        rag = build(args.mode)
        qs = load_questions()
        r = evaluate_retrieval(rag, qs, rag.k)
        print(f"Retrieval ({r.n} answerable questions): recall@1 {r.recall_at_1:.2f}, recall@{r.k} {r.recall_at_k:.2f}, "
              f"MRR {r.mrr:.2f}; misses: {r.misses or 'none'}")
        if not args.retrieval_only:
            a = evaluate_answers(rag, qs)
            print(f"Answers ({rag.answerer.__class__.__name__}): fact accuracy {a.fact_accuracy:.2f}, "
                  f"cites the right note {a.citation_accuracy:.2f}, false abstentions {a.false_abstention:.2f}, "
                  f"abstains on {a.correct_abstention:.2f} of {a.n_unanswerable} unanswerable questions")
            if args.save:
                Path(args.save).write_text(json.dumps(a.rows, indent=1))
    elif args.cmd == "export-index":
        Path(args.out).write_text(json.dumps(BM25(load_corpus()).to_json()))
        print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
