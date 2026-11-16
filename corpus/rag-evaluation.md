# Retrieval-augmented generation and how to evaluate it

## The idea

Retrieval-augmented generation (RAG) answers a question in two steps: retrieve the passages from a document collection that are most relevant to the question, then let a language model answer using only those passages. The model can cite where each statement comes from, and the collection can be updated without retraining.

## Retrieval

Documents are split into chunks of a few hundred words, ideally along section boundaries. Lexical retrieval with BM25 scores chunks by term frequency, inverse document frequency and length normalisation; it is strong for exact technical terms, gene names and abbreviations. Dense retrieval embeds questions and chunks as vectors and finds semantic matches even without shared words. Hybrid systems combine both, for example with reciprocal rank fusion, which adds 1 / (k + rank) from each ranking.

## Evaluating retrieval

With a set of questions labelled with their relevant documents, recall at k (is a relevant document among the top k?) and mean reciprocal rank (1 / rank of the first relevant result, averaged) measure retrieval separately from generation. Poor answers are often retrieval failures.

## Evaluating answers

Answers are checked for correctness against reference facts, for grounding (is every claim supported by a cited passage?) and for abstention: questions whose answer is not in the collection should get "I don't know" instead of a fluent guess. Keep the evaluation set fixed and run it on every change to the prompt, chunking or model.
