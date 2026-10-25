---
title: "Retrieval-Augmented Generation (RAG): a practical guide with examples and best practices"
date: 2026-10-25 10:00:00 +0700
categories: [ai]
lang: en
---

Large language models know a lot, but they do not know your documents, your product catalog, or yesterday's policy change. They also make things up when they are unsure. Retrieval-Augmented Generation (RAG) fixes both problems by fetching relevant text at question time and giving it to the model as context. This guide explains how RAG works, walks through a small example, and lists the practices that separate a demo from a system people trust.

## What RAG is

RAG has two phases.

1. **Indexing (offline):** split your documents into chunks, turn each chunk into a vector (an embedding), and store the vectors with their text and metadata.
2. **Answering (online):** turn the user's question into a vector, find the most similar chunks, and place them in the prompt next to the question. The model answers using that context.

The model does not learn your data. It reads the retrieved text each time. That is why RAG is usually cheaper and easier to update than fine-tuning: when a document changes, you re-index it.

```
Question ──► embed ──► vector search ──► top-k chunks ──┐
                                                         ▼
Documents ──► chunk ──► embed ──► vector store      prompt = context + question ──► LLM ──► answer + citations
```

## A minimal example

This example uses an in-memory index so you can run it without infrastructure. It shows the moving parts; a production system swaps each piece for a real component.

```python
import numpy as np

def chunk(text: str, size: int = 500, overlap: int = 50) -> list[str]:
    words = text.split()
    chunks, start = [], 0
    while start < len(words):
        chunks.append(" ".join(words[start:start + size]))
        start += size - overlap
    return chunks

def embed(texts: list[str]) -> np.ndarray:
    # Replace with your embedding model (an API or a local model).
    ...

class Index:
    def __init__(self):
        self.texts, self.meta, self.vectors = [], [], []

    def add(self, doc_id: str, text: str):
        for c in chunk(text):
            self.texts.append(c)
            self.meta.append({"doc_id": doc_id})
        self.vectors = embed(self.texts)  # simplified: re-embed on add

    def search(self, query: str, k: int = 4):
        q = embed([query])[0]
        scores = self.vectors @ q / (np.linalg.norm(self.vectors, axis=1) * np.linalg.norm(q))
        top = np.argsort(-scores)[:k]
        return [(self.texts[i], self.meta[i], float(scores[i])) for i in top]

def answer(index: Index, question: str, llm) -> str:
    hits = index.search(question)
    context = "\n\n".join(f"[{i+1}] {text}" for i, (text, _, _) in enumerate(hits))
    prompt = (
        "Answer using only the sources below. Cite sources as [n]. "
        "If the sources do not contain the answer, say you do not know.\n\n"
        f"Sources:\n{context}\n\nQuestion: {question}"
    )
    return llm(prompt)
```

Three things in this sketch matter more than they look. The prompt tells the model to answer only from the sources. Each source has a number, so the answer can cite it. And the prompt gives the model an explicit way to say "I don't know," which prevents most made-up answers.

## A worked example: a returns policy assistant

Suppose an online store wants a chatbot that answers questions about its returns policy, which changes twice a year.

- **Documents:** the policy pages, plus the FAQ, exported as Markdown. Each file has metadata: `region`, `effective_date`, `product_category`.
- **Chunking:** split by heading first, then by size. A section called "Electronics returns" becomes one chunk, not a fragment cut in the middle of a sentence.
- **Question:** "Can I return a laptop I bought in Germany 40 days ago?"
- **Retrieval:** filter by `region = DE` and `effective_date` = the current version, then search for "returns laptop" within that subset.
- **Prompt:** the top chunks, with the question, and the instruction to cite sources.
- **Answer:** "No. Electronics can be returned within 30 days of delivery [2]." The citation lets a support agent check the source in one click.

The metadata filter is the key step. Without it, the model may cite last year's 60-day policy for German customers, and sound confident about it.

## Chunking

Chunking has the largest effect on answer quality, and it is the step most often skipped.

**Practices:**

- **Split on structure first.** Headings, sections, list items, and code blocks are natural boundaries. Split by size only when a section is too large.
- **Start around 300 to 800 tokens per chunk,** with 10% to 20% overlap. Tune this with your evaluation set, not by feel.
- **Keep context with each chunk.** Prefix every chunk with its document title and section path, for example `Returns policy > Electronics > Laptops`. A bare sentence like "This does not apply to sale items" is useless without knowing what "this" refers to.
- **Keep tables whole.** A table split across chunks loses its column headers.

## Embeddings and the vector store

The embedding model turns text into vectors so that similar meanings land close together. Choose it for your language and domain, and test it on your own questions. A general model that works well in English may be weak on Vietnamese legal text, for example.

**Practices:**

- **Embed queries and documents with the same model.** Mixing models silently ruins retrieval.
- **Store metadata with each vector** (source, date, region, access group) so you can filter before or during search.
- **Plan for re-indexing.** Keep the source document ID and a content hash per chunk so you can update only what changed.
- **Version your index.** When you change the chunking or the model, build a new index next to the old one and compare before switching.

## Retrieval: beyond "top 4 by cosine similarity"

Pure vector search misses exact matches such as product codes, error messages, or names. Keyword search (BM25) catches them but misses paraphrases. Production systems usually combine both.

**Practices:**

- **Use hybrid search.** Run vector and keyword search, then merge the results (reciprocal rank fusion is a simple, robust choice).
- **Retrieve more, then rerank.** Fetch 20 to 50 candidates cheaply, then rerank the top ones with a cross-encoder or a reranking model. Reranking often improves precision more than changing the embedding model.
- **Tune k.** Too few chunks miss the answer. Too many dilute it and push the relevant text toward the middle of the prompt, where models attend least. Start with 3 to 6 chunks and measure.
- **Apply filters before ranking,** not after. Filtering a top-10 list down to two results leaves you with too little.

Example of hybrid merge:

```python
def rrf(rankings: list[list[str]], k: int = 60) -> list[str]:
    # Reciprocal rank fusion: each list contributes 1 / (k + rank)
    scores = {}
    for ranking in rankings:
        for rank, doc_id in enumerate(ranking, start=1):
            scores[doc_id] = scores.get(doc_id, 0) + 1 / (k + rank)
    return sorted(scores, key=scores.get, reverse=True)

fused = rrf([vector_search(q), keyword_search(q)])
```

## Prompting with retrieved context

**Practices:**

- **State the rules plainly:** answer only from the sources, cite each claim, and say when the sources do not answer the question.
- **Mark the boundary.** Wrap retrieved text in clear delimiters such as `<source id="2">...</source>`. This helps the model separate your instructions from document content.
- **Treat retrieved text as data, not instructions.** A document can contain text like "ignore previous instructions." Do not let retrieved content change the task. This is the main defense against indirect prompt injection in RAG systems.
- **Ask for a structured answer when you can.** For example, an answer field plus a list of cited source IDs. Your application can then check that every cited ID was actually retrieved.

## Evaluation: the part most teams skip

Without an evaluation set, you cannot tell whether a change helped. Build one early.

**How to build it:**

1. Collect 50 to 200 real questions from users, support tickets, or search logs.
2. For each question, record the document and passage that should answer it.
3. Include hard cases: questions with no answer in the corpus, questions with conflicting sources, and questions where the wording differs from the document.

**What to measure:**

- **Retrieval quality:** recall@k (did the right chunk appear in the top k?) and MRR (how high did it rank?). Measure retrieval separately from generation, so you know which part to fix.
- **Answer faithfulness:** does every claim in the answer appear in the cited sources? Automated checks and LLM-as-judge methods help, but spot-check them by hand.
- **Abstention:** on questions the corpus cannot answer, does the system say so?
- **Latency and cost** per question, since hybrid search and reranking add both.

Run this evaluation on every change to chunking, the embedding model, the prompt, or k.

## Common failure modes and fixes

| Symptom | Likely cause | Fix |
|---|---|---|
| Answer is fluent but wrong | Right document, wrong chunk, or no retrieval hit | Check recall@k first; improve chunking and hybrid search |
| Answer cites a real source but says something it does not contain | Weak prompt or too much context | Tighten the instruction; reduce k; rerank |
| Answer uses an outdated policy | Stale index or missing date filter | Add `effective_date` filters; re-index on change |
| Answer ignores the relevant detail in a long context | "Lost in the middle" effect | Put the most relevant chunks first and last; use fewer, better chunks |
| Answer leaks content the user should not see | No access control at retrieval time | Filter by user permissions in the index query, not in the UI |
| Answer follows instructions hidden in a document | Prompt injection through retrieved text | Delimit sources, treat them as data, and limit what tools the model can call |

## Security and access control

Enforce permissions where data is retrieved, not where it is displayed. If a user cannot read a document in your document system, the retrieval query must never return its chunks to that user. Store an access group on each chunk and apply it as a filter on every search. Log which chunks were used for each answer, so you can audit what the model saw.

## Going beyond basic RAG

Once the basics work, consider:

- **Query rewriting:** turn a vague or follow-up question ("what about for students?") into a standalone query before searching.
- **Multi-step retrieval:** let the model search again when the first results are not enough, with a limit on steps.
- **Structured data:** for numbers and tables, a SQL or API lookup often beats text retrieval. Use RAG for the text and tools for the facts.
- **Knowledge graphs or GraphRAG** for questions that need links across many documents. This adds cost and complexity, so start with it only when simpler methods fail your evaluation set.

## Summary

A good RAG system is mostly careful data work: sensible chunks with context, metadata for filtering, hybrid retrieval with reranking, a prompt that enforces grounding and citations, and access control at retrieval time. Build an evaluation set first, measure retrieval and answers separately, and change one thing at a time. The model matters, but the retrieval pipeline usually decides whether users trust the answers.
