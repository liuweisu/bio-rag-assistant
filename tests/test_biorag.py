from types import SimpleNamespace

import pytest
from anthropic.types.beta import BetaMessage
from fastapi.testclient import TestClient

from biorag import api, corpus, evaluate, generate, pipeline, retrieval


@pytest.fixture(scope="module")
def chunks():
    return corpus.load_corpus()


@pytest.fixture(scope="module")
def bm25(chunks):
    return retrieval.BM25(chunks)


# --- corpus and retrieval ---------------------------------------------------

def test_chunks_have_unique_ids_and_reasonable_size(chunks):
    assert len({c.id for c in chunks}) == len(chunks)
    assert all(5 <= len(c) <= 320 for c in chunks)


def test_split_markdown_keeps_document_title():
    chunks = corpus.split_markdown("doc", "# Title\n\nIntro.\n\n## Part A\n\nText A.\n\n## Part B\n\nText B.")
    assert [c.title for c in chunks] == ["Title > Introduction", "Title > Part A", "Title > Part B"]


def test_tokenizer():
    assert retrieval.tokenize("The LTR retrotransposons of maize") == ["ltr", "retrotransposon", "maize"]


def test_bm25_finds_the_right_note(bm25):
    assert bm25.search("target site duplication of hAT elements")[0].chunk.doc == "dna-transposons"
    assert bm25.search("median of ratios size factors")[0].chunk.doc == "rnaseq-differential-expression"


def test_bm25_prefers_rare_terms(bm25):
    assert bm25.idf["helitron"] > bm25.idf["genome"]


def test_hybrid_fusion_merges_rankings(chunks, bm25):
    class Fixed:
        def search(self, q, k=5):
            return [retrieval.Hit(chunks[0], 1.0, 1)]
    fused = retrieval.HybridRetriever([bm25, Fixed()]).search("N50 contig length", 3)
    assert chunks[0].id in {h.chunk.id for h in fused}


def test_retrieval_eval_meets_bar(bm25):
    rag = pipeline.RAG(bm25, generate.ExtractiveAnswerer(idf=bm25.idf))
    report = evaluate.evaluate_retrieval(rag, evaluate.load_questions())
    assert report.recall_at_k >= 0.95 and report.mrr >= 0.9


# --- extractive baseline -----------------------------------------------------

def test_extractive_answers_and_abstains(bm25):
    rag = pipeline.RAG(bm25, generate.ExtractiveAnswerer(idf=bm25.idf))
    good = rag.ask("Where does trypsin cleave proteins?").answer
    assert not good.abstained and "lysine" in good.text.lower() and good.citations
    bad = rag.ask("What annealing temperature should I use for my 16S rRNA PCR primers?").answer
    assert bad.abstained


# --- Claude answerer with a fake client ----------------------------------------

def fake_message(content, stop_reason="end_turn"):
    return BetaMessage.model_validate({
        "id": "msg_test", "type": "message", "role": "assistant", "model": "claude-opus-5-5",
        "content": content, "stop_reason": stop_reason, "stop_sequence": None,
        "usage": {"input_tokens": 1200, "output_tokens": 80},
    })


class FakeClient:
    def __init__(self, message):
        self.message = message
        self.calls = []
        self.beta = SimpleNamespace(messages=SimpleNamespace(create=self._create))

    def _create(self, **kwargs):
        self.calls.append(kwargs)
        return self.message


def test_claude_answerer_builds_cited_request_and_parses_citations(bm25):
    hits = bm25.search("How is the age of an LTR retrotransposon estimated?", 3)
    msg = fake_message([
        {"type": "thinking", "thinking": "", "signature": "x"},
        {"type": "text", "text": "The age is T = K / (2r).", "citations": [{
            "type": "char_location", "cited_text": "T = K / (2r)", "document_index": 0,
            "document_title": hits[0].chunk.title, "start_char_index": 0, "end_char_index": 12, "file_id": None}]},
    ])
    client = FakeClient(msg)
    ans = generate.ClaudeAnswerer(client=client).answer("How old?", hits)
    req = client.calls[0]
    docs = [b for b in req["messages"][0]["content"] if b["type"] == "document"]
    assert len(docs) == 3 and all(d["citations"] == {"enabled": True} for d in docs)
    assert req["model"] == "claude-opus-5-5" and req["fallbacks"] == "default"
    assert "thinking" not in req and "temperature" not in req
    assert ans.text == "The age is T = K / (2r)." and not ans.abstained
    assert ans.citations[0].chunk_id == hits[0].chunk.id
    assert ans.usage == {"input_tokens": 1200, "output_tokens": 80}


def test_claude_answerer_abstains_on_sentinel_and_refusal(bm25):
    hits = bm25.search("wheat gene count", 2)
    sentinel = generate.ClaudeAnswerer(client=FakeClient(fake_message([{"type": "text", "text": generate.ABSTAIN}])))
    assert sentinel.answer("How many genes does wheat have?", hits).abstained
    refused = generate.ClaudeAnswerer(client=FakeClient(fake_message([], stop_reason="refusal")))
    assert refused.answer("?", hits).abstained


# --- API ---------------------------------------------------------------------

@pytest.fixture
def client(monkeypatch, bm25):
    rag = pipeline.RAG(bm25, generate.ExtractiveAnswerer(idf=bm25.idf))
    monkeypatch.setattr(api, "get_rag", lambda: rag)
    return TestClient(api.app)


def test_api_health_search_ask(client):
    assert client.get("/health").json()["status"] == "ok"
    hits = client.get("/search", params={"q": "excess green index"}).json()
    assert hits[0]["id"].startswith("plant-image-phenotyping")
    r = client.post("/ask", json={"question": "How are touching nuclei separated?"}).json()
    assert "watershed" in r["answer"].lower() and r["citations"]


def test_api_validates_input(client):
    assert client.post("/ask", json={"question": ""}).status_code == 422
