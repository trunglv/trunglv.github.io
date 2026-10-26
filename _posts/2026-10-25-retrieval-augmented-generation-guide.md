---
title: "Retrieval-Augmented Generation (RAG): a practical guide with examples and best practices"
date: 2026-10-25 10:00:00 +0700
categories: [ai]
lang: en
---

Large language models know a lot, but they do not know your documents, your product catalog, or yesterday's policy change. They also make things up when they are unsure. Retrieval-Augmented Generation (RAG) fixes both problems by fetching relevant text at question time and giving it to the model as context. This guide explains how RAG works, walks through a small example, and lists the practices that separate a demo from a system people trust.

{% include toc.html %}

## At a glance

| Stage | What happens | Best practice |
|---|---|---|
| 1. Chunk | Split documents into small, focused pieces | Split by headings first; aim for 300 to 800 tokens; keep the section title with each chunk |
| 2. Embed | An embedding model turns each chunk into a vector | Use the same model for documents and questions; choose a multilingual model for Vietnamese |
| 3. Store | Save the vectors with the chunk text and metadata | Store source, date and access group; record the model name and version |
| 4. Retrieve | Embed the question and find the closest chunks | Combine vector and keyword search; rerank; filter by user permissions |
| 5. Prompt | Put the top chunks and the question into the prompt | Number the sources; allow "I don't know"; treat sources as data, not instructions |
| 6. Generate | The LLM writes the answer from the sources | Require citations; check that every cited source was retrieved |
| 7. Evaluate | Measure retrieval and answers on real questions | Build a test set early; change one thing at a time |

Each stage is explained below. The guide first covers what RAG is and the key terms, then how to build a small working system, then the practices that make it reliable.

## What RAG is

RAG has two phases.

1. **Indexing (offline):** split your documents into chunks, turn each chunk into a vector (an embedding), and store the vectors with their text and metadata.
2. **Answering (online):** turn the user's question into a vector, find the most similar chunks, and place them in the prompt next to the question. The model answers using that context.

The model does not learn your data. It reads the retrieved text each time. That is why RAG is usually cheaper and easier to update than fine-tuning (retraining the model on your own data): when a document changes, you re-index it.

{% include llm-rag-diagram.html %}

{% include rag-steps.html %}

## Key terms: chunk and vector, with an example

Two words come up constantly in RAG. Here is what they mean, using one short document. The same document is used in every example in this guide.

**Chunk:** a piece of a document that is small enough to fit in a prompt and specific enough to answer one kind of question. Chunks are the units that get searched and returned.

**Vector (embedding):** a list of numbers that represents the meaning of a piece of text. An embedding model reads the text and outputs the list. Texts with similar meaning get lists of numbers that point in similar directions, so you can find related text by comparing lists instead of matching words.

### The example document

Imagine a file called `returns-policy.md` with this text:

> Customers may return most items within 30 days of delivery. Electronics have a 15-day window and must include all accessories. Sale items are final and cannot be returned.

### Step 1: split it into chunks

The simplest rule is to split by sentence. For this short document, that gives three chunks, one per sentence:

| Chunk | Text | Index |
|---|---|---|
| A | Customers may return most items within 30 days of delivery. | 0 |
| B | Electronics have a 15-day window and must include all accessories. | 1 |
| C | Sale items are final and cannot be returned. | 2 |

Each chunk keeps some context with it. In a real system, chunk B would also carry the document name and section, for example "returns-policy.md, Returns policy", so the model knows where the sentence came from.

### Step 2: turn each chunk into a vector

An embedding model converts each chunk into a vector. Real models typically use between 384 and 3,072 numbers per vector. For illustration, here is chunk B with only 8 numbers: 0.12, -0.53, 0.88, 0.04, -0.31, 0.27, 0.66, -0.09.

Each number is one coordinate. No single number means anything by itself. What matters is the whole list: a question about electronics returns produces a vector that lands close to the vector for chunk B, and a question about sale items lands close to the vector for chunk C.

### Choosing an embedding model

Not all embedding models are the same. They differ in which languages they understand, how large their vectors are, and where they run. There are three broad kinds.

**English-only models** are trained mainly on English text. They are small and fast, and they work well when all your documents and questions are in English. A common example produces 384-number vectors. The weakness is that they often understand other languages poorly, so a Vietnamese question may land far from the English chunk that answers it, even when the meaning matches.

**Multilingual models** are trained on text from many languages at once, usually including Vietnamese. They place a sentence and its translation close together, and they handle a question in one language against a document in another. The family of models called bge-m3 is one example. It produces 1024-number vectors and accepts long inputs, so it suits real documents. Multilingual models are larger and slower than English-only models, so they need more memory and a little more time per chunk.

**Domain or hosted models** are tuned for a field such as law or medicine, or are offered as an API by a vendor. A hosted model removes the work of running it yourself, but your text leaves your system on every request, so check the privacy terms before you send private documents.

These are the points to compare when you choose:

| What to compare | Why it matters |
|---|---|
| Languages covered | Your users' questions and your documents must both be understood well |
| Vector size (for example 384, 768, 1024) | Larger vectors use more storage and search time, but can capture finer differences |
| Maximum input length | If a model accepts only short text, long chunks get cut off and lose meaning |
| Where it runs | On your own machine or server, or through an API with a cost per request |
| Test results on your own questions | Public benchmarks are a starting point; your evaluation set decides |

For a Vietnamese returns policy, a multilingual model lets a question such as "Có được trả hàng sau 20 ngày không?" find the English or Vietnamese chunk about the electronics window. An English-only model would likely miss it. Still, test the model on real Vietnamese questions before you rely on it, because some multilingual models handle Vietnamese well and others handle it only moderately.

Whichever model you choose, use the same one for indexing and for every question. If you change the model, every chunk must be embedded again.

### Step 3: search with a question

The question is also turned into a vector. Retrieval then compares it with every chunk vector using cosine similarity, a score from -1 to 1 where higher means closer in meaning. Here is an illustrative run for the question "Can I return a TV after 20 days?":

| Chunk | Similarity score | Result |
|---|---|---|
| B (electronics window) | 0.82 | Top match |
| A (30-day general window) | 0.61 | Second match |
| C (sale items) | 0.18 | Not relevant |

The top chunk, B, goes into the prompt. The model then answers from that text: the electronics window is 15 days, so a TV at day 20 is not eligible.

Note that the question contains "TV", not "electronics", and the document never says "TV". Vector search still finds the right chunk because the meanings are close. Keyword search alone would miss it.

### How the data is stored on disk

Three kinds of data are kept, and they can be separate files or one database.

1. **The raw document,** unchanged, as the source of truth. For example, a file named `returns-policy.md` in a `raw` folder.

2. **The chunks,** one record per chunk. Each record holds an ID (for example, `returns-policy#0`), the document name, the section, the chunk number, the text, and metadata such as region and effective date. Store them one record per line in a plain text file, so each line can be read on its own.

3. **The vectors,** stored as a table of numbers where row *i* is the vector for chunk *i*. For three chunks of 384 numbers stored as 32-bit floats, the file is about 4.6 KB. The row order must match the order of the chunk records, so row 0 belongs to the first chunk record, row 1 to the second, and so on.

In production, a vector database such as pgvector, Qdrant, or Milvus keeps the same information. It stores each vector with its ID and metadata, and it builds an index structure so search does not compare the question against every row. The principle stays the same: the text and metadata live in one place, the vectors live with them, and every vector can be traced back to the exact chunk and document it came from.

Keep the raw file. If the policy changes, you re-chunk the new version, re-embed only the changed chunks, and write a new index next to the old one.

## A minimal example: the prompt

The minimal example is the prompt that the application builds once the relevant chunks are found. The retrieval step can use any of the approaches described in this guide. The prompt is what makes the answer grounded. It contains three parts: the instructions, the numbered sources, and the question.

> Answer using only the sources below. Cite sources as [n]. If the sources do not contain the answer, say you do not know.
>
> Sources:
> [1] Electronics have a 15-day window and must include all accessories.
> [2] Customers may return most items within 30 days of delivery.
>
> Question: Can I return a TV after 20 days?

Three things in this prompt matter more than they look. It tells the model to answer only from the sources. Each source has a number, so the answer can cite it. And it gives the model an explicit way to say "I don't know," which prevents most made-up answers.

## Build a simple RAG step by step

This section explains how to build a working RAG system from a small project with local files. It needs no database server. You can run the embedding model and the LLM on your own computer, or call them through an API.

### The process

{% include rag-algorithm-flowchart.html %}

The process has two parts. Part 1 runs once, or whenever your documents change, and writes an index to disk. Part 2 runs on every question and reads that index.

### Step 1: prepare the project

Create one folder for the project. Inside it, create a folder for your documents, and a folder that the indexing step will fill with the index files. Put your text file in the documents folder.

For the example, use the same returns policy as above, with each sentence as its own paragraph, separated by blank lines:

- Customers may return most items within 30 days of delivery.
- Electronics have a 15-day window and must include all accessories.
- Sale items are final and cannot be returned.

Each paragraph will become one chunk.

Next, choose two models. The first is an embedding model, which turns text into vectors. The second is an LLM, which writes the answer. Install both with the tools you prefer. You can run them on your own computer or call them through an API. For English content, a small English embedding model is enough. For Vietnamese content, choose a multilingual model such as bge-m3 or a multilingual E5 model, and test it on your own Vietnamese questions before you rely on it.

### Step 2: index the documents

Indexing runs once, or whenever the documents change. It has five parts:

1. **Read** each file in the documents folder.
2. **Split** each file into chunks. For this short file, one chunk per paragraph is enough. For real documents, split by headings first, then by size, as described in the chunking section below.
3. **Embed** each chunk. Send the text of each chunk to the embedding model, which returns one vector per chunk. Send chunks in batches, because batching is much faster than one request per chunk.
4. **Store** the results. Save the vectors in one file, and save each chunk's text and metadata (document, section, chunk number) in a second file, one record per chunk. Row *i* of the vectors must belong to record *i* of the chunks file.
5. **Record the model name and version** next to the index. If you change the model later, you must re-embed every chunk, and the record tells you when that is needed.

For the example file, the result is three chunks, three vectors, and two files in the index folder.

### Step 3: answer a question

Answering runs on every question. It has six parts:

1. **Embed the question** with the same embedding model used for indexing. This gives a vector for the question.
2. **Compare** the question vector with every stored chunk vector, and score how close each one is.
3. **Check the threshold.** If even the best score is below a minimum you choose, stop and reply that the answer is not in the sources. Tune this minimum with your evaluation set.
4. **Keep the top chunks.** For this tiny example, keep two. In practice, start with three to six, as discussed in the retrieval section below.
5. **Build the prompt** from those chunks, using the template in the minimal example above: the instructions, the numbered sources, and the question.
6. **Ask the LLM** for the answer. The LLM reads only the prompt. It does not search the index.

The application returns the answer with the citation numbers, so the user can check each source.

### What you should see

The retrieval step scores the three chunks against the question. The electronics chunk (B) should rank first, because the question is about a TV and the chunk talks about electronics. The 30-day chunk (A) comes second, and the sale-items chunk (C) is left out. The prompt then contains B and A as sources [1] and [2], exactly as in the minimal example above, and the model should reply with something like:

> No. Electronics have a 15-day window [1].

If the answer is wrong, check the retrieval step before changing the prompt. Look at the top chunks for the question and confirm the electronics chunk is among them. Most problems start there.

### What this simple version leaves out

This setup is a good starting point, and it has clear limits:

- **Scale:** the whole index sits in memory, and every question compares against every chunk. That is fine for thousands of chunks, not millions.
- **Updates:** indexing rebuilds everything. A production system re-embeds only changed chunks.
- **Access control:** there is no per-user filter. Add one before you connect real private data.
- **Quality:** no hybrid search, no reranking, and no evaluation set.

The rest of this guide covers each of these. When you need them, move the index into a vector database such as pgvector or Qdrant, and keep the same process. Run the database and the application as separate services, and the change touches only the storage part.

## A worked example: the returns assistant in production

Now suppose the same store grows. It sells in several countries, updates its policy twice a year, and has an FAQ. It wants a chatbot that answers returns questions across all of that.

- **Documents:** the policy pages for each country, plus the FAQ, exported as Markdown. Each file has metadata: region, effective date, and product category.
- **Chunking:** split by heading first, then by size. A section called "Electronics returns" becomes one chunk, not a fragment cut in the middle of a sentence.
- **Question:** "Can I return a laptop I bought in Germany 40 days ago?"
- **Retrieval:** filter by region = Germany and by the current effective date, then search within that subset.
- **Prompt:** the top chunks, with the question, and the instruction to cite sources.
- **Answer:** "No. Electronics have a 15-day window [1]." The citation lets a support agent check the source in one click.

The metadata filter is the key step. Without it, the model may cite last year's 60-day policy, or the policy for another country, and sound confident about it.

## Chunking

Chunking has the largest effect on answer quality, and it is the step most teams give the least thought.

**Practices:**

- **Split on structure first.** Headings, sections, list items, and code blocks are natural boundaries. Split by size only when a section is too large.
- **Start around 300 to 800 tokens per chunk** (a token is roughly three-quarters of a word in English), with 10% to 20% overlap. Tune this with your evaluation set, not by feel.
- **Keep context with each chunk.** Prefix every chunk with its document title and section path, for example "Returns policy > Electronics > Laptops". A bare sentence like "This does not apply to sale items" is useless without knowing what "this" refers to.
- **Keep tables whole.** A table split across chunks loses its column headers.

## Embeddings and the vector store

The embedding model turns text into vectors so that similar meanings land close together. Choose it for your language and domain, and test it on your own questions. A general model that works well in English may be weak on Vietnamese legal text, for example.

**Practices:**

- **Embed queries and documents with the same model.** Mixing models silently ruins retrieval.
- **Store metadata with each vector** (source, date, region, access group) so you can filter before or during search.
- **Plan for re-indexing.** Keep the source document ID and a content fingerprint per chunk so you can update only what changed.
- **Version your index.** When you change the chunking or the model, build a new index next to the old one and compare before switching.

## Retrieval: beyond simple similarity search

Pure vector search misses exact matches such as product codes, error messages, or names. Keyword search catches them but misses paraphrases. Production systems usually combine both.

**Practices:**

- **Use hybrid search.** Run vector search and keyword search separately, then merge the two result lists. Reciprocal rank fusion is a simple, robust way to merge them: each result earns points based on its position in each list, and the points are added together. A document near the top of both lists ends up at the top of the merged list.
- **Retrieve more, then rerank.** Fetch 20 to 50 candidates cheaply, then rerank the top ones with a cross-encoder or a reranking model. Reranking often improves precision more than changing the embedding model.
- **Tune k.** Too few chunks miss the answer. Too many dilute it and push the relevant text toward the middle of the prompt, where models attend least. Start with 3 to 6 chunks and measure.
- **Apply filters before ranking,** not after. Filtering a top-10 list down to two results leaves you with too little.

## Prompting with retrieved context

**Practices:**

- **State the rules plainly:** answer only from the sources, cite each claim, and say when the sources do not answer the question.
- **Mark the boundary.** Wrap each retrieved passage in a clear tag with its source number. This helps the model separate your instructions from document content.
- **Treat retrieved text as data, not instructions.** A document can contain text like "ignore previous instructions." Do not let retrieved content change the task. This is the main defense against indirect prompt injection in RAG systems.
- **Ask for a structured answer when you can.** For example, an answer plus a list of cited source numbers. Your application can then check that every cited number was actually retrieved.

## Evaluation: the part most teams skip

Without an evaluation set, you cannot tell whether a change helped. Build one early.

**How to build it:**

1. Collect 50 to 200 real questions from users, support tickets, or search logs.
2. For each question, record the document and passage that should answer it.
3. Include hard cases: questions with no answer in the corpus, questions with conflicting sources, and questions where the wording differs from the document.

**What to measure:**

- **Retrieval quality:** recall at k (did the right chunk appear in the top k?) and MRR, mean reciprocal rank (how high did it rank?). Measure retrieval separately from generation, so you know which part to fix.
- **Answer faithfulness:** does every claim in the answer appear in the cited sources? Automated checks and LLM-as-judge methods help, but spot-check them by hand.
- **Abstention:** on questions the corpus cannot answer, does the system say so?
- **Latency and cost** per question, since hybrid search and reranking add both.

Run this evaluation on every change to chunking, the embedding model, the prompt, or k.

## Common failure modes and fixes

| Symptom | Likely cause | Fix |
|---|---|---|
| Answer is fluent but wrong | Right document, wrong chunk, or no retrieval hit | Check recall at k first; improve chunking and hybrid search |
| Answer cites a real source but says something it does not contain | Weak prompt or too much context | Tighten the instruction; reduce k; rerank |
| Answer uses an outdated policy | Stale index or missing date filter | Add effective-date filters; re-index on change |
| Answer ignores the relevant detail in a long context | "Lost in the middle" effect | Put the most relevant chunks first and last; use fewer, better chunks |
| Answer leaks content the user should not see | No access control at retrieval time | Filter by user permissions in the search itself, not in the interface |
| Answer follows instructions hidden in a document | Prompt injection through retrieved text | Delimit sources, treat them as data, and limit what tools the model can call |

## Security and access control

Enforce permissions where data is retrieved, not where it is displayed. If a user cannot read a document in your document system, the retrieval step must never return its chunks to that user. Store an access group on each chunk and apply it as a filter on every search. Log which chunks were used for each answer, so you can audit what the model saw.

## Run the system with Docker

When the simple version outgrows your laptop, or when a colleague needs to run it too, put each part in its own container. Docker packages each part with everything it needs, so the system starts the same way on any machine that has Docker.

{% include docker-architecture.html %}

### Use ready-made open-source images first

Build only the part you write yourself. For everything else, use an open-source image that already exists and is widely used. Here is what to choose:

| Container | Ready-made open-source option | Role | Data it keeps |
|---|---|---|---|
| App | Your own code, with a small build file that packages it | Receives questions, runs the ingestion job, builds the prompt, calls the LLM | None. It is stateless, so you can restart or replace it at any time |
| Database | `pgvector/pgvector:0.8.7-pg17`: Postgres 17 with the pgvector extension | Stores chunks, vectors, metadata, and the model version, and searches the vectors | Yes, in a volume |
| LLM server | `ollama/ollama:0.40.11`, serving the open-weight model `qwen2.5:7b` | Writes answers from the prompt | The downloaded model files, in a volume |
| Embedding server | The same Ollama container, serving `bge-m3` (multilingual, including Vietnamese, 1024-number vectors). Hugging Face Text Embeddings Inference is an alternative | Turns text into vectors | The model files, in the Ollama volume |

Choosing ready-made images has three benefits. You do not maintain the database or model server yourself, security fixes arrive as new image versions, and anyone who knows these tools can read your setup without learning a custom one.

### What each container does

A container that only holds a running program is disposable. A container that holds data needs a volume, so that the data stays when the container is rebuilt. In the table above, the app is the only container you build. The database and Ollama run from published images, and Ollama serves both the LLM and the embedding model, so the whole system needs only three long-running containers.

### Download the configuration

The three files below set up everything except your app. The image versions were current on 26 October 2026. Check for newer versions before you deploy.

- [docker-compose.yml]({{ "/assets/downloads/rag-docker/docker-compose.yml" | relative_url }}): the services, pinned images, health checks, volumes, and the one port the app exposes. It also contains a one-off job that downloads `bge-m3` and `qwen2.5:7b` into Ollama on first start, and a commented-out block for using an NVIDIA GPU.
- [init.sql]({{ "/assets/downloads/rag-docker/init.sql" | relative_url }}): runs once when the database starts for the first time. It enables pgvector, creates the chunks table with a 1024-number vector column to match `bge-m3`, and adds a similarity index and an access-group index.
- [env.example]({{ "/assets/downloads/rag-docker/env.example" | relative_url }}): copy it to a file named `.env` next to `docker-compose.yml`, and set a real database password.

Place them in the project folder next to an `app` folder (your code and its build file) and a `docs` folder (the documents to index).

#### docker-compose.yml

```yaml
# Simple RAG stack: your app + Postgres/pgvector + Ollama (LLM and embeddings).
# All images except the app are published open-source images, pinned to a version.
# Before the first start: copy env.example to .env and set a real password.

name: simple-rag

services:
  app:
    build: ./app                  # your own code; the only image you build
    ports:
      - "8000:8000"               # the only port exposed outside Docker
    environment:
      DATABASE_URL: postgresql://rag:${POSTGRES_PASSWORD}@db:5432/rag
      OLLAMA_URL: http://ollama:11434
      EMBED_MODEL: bge-m3         # multilingual (incl. Vietnamese), 1024-dimensional vectors
      LLM_MODEL: qwen2.5:7b       # open-weight LLM that writes the answers
    volumes:
      - ./docs:/app/docs:ro       # the documents to index
    depends_on:
      db:
        condition: service_healthy
      ollama-init:
        condition: service_completed_successfully
    restart: unless-stopped

  db:
    image: pgvector/pgvector:0.8.7-pg17
    environment:
      POSTGRES_USER: rag
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: rag
    volumes:
      - pgdata:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql:ro   # creates the table on first start
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U rag -d rag"]
      interval: 5s
      timeout: 3s
      retries: 20
    restart: unless-stopped

  ollama:
    image: ollama/ollama:0.40.11
    volumes:
      - ollama:/root/.ollama      # downloaded models survive restarts
    healthcheck:
      test: ["CMD", "ollama", "list"]
      interval: 10s
      timeout: 5s
      retries: 30
    restart: unless-stopped
    # NVIDIA GPU: uncomment if the host has a GPU and the NVIDIA Container Toolkit.
    # deploy:
    #   resources:
    #     reservations:
    #       devices:
    #         - driver: nvidia
    #           count: all
    #           capabilities: [gpu]

  ollama-init:                    # one-off job: download the two models, then exit
    image: ollama/ollama:0.40.11
    environment:
      OLLAMA_HOST: ollama:11434
    entrypoint: ["sh", "-c", "ollama pull bge-m3 && ollama pull qwen2.5:7b"]
    depends_on:
      ollama:
        condition: service_healthy
    restart: "no"

volumes:
  pgdata:
  ollama:
```

#### init.sql

```sql
-- Runs once, on the first start of the database container.
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS chunks (
  id            text PRIMARY KEY,               -- for example returns-policy#0
  doc           text NOT NULL,                  -- source document
  section       text,                           -- section path inside the document
  chunk_index   integer NOT NULL,
  content       text NOT NULL,                  -- the chunk text shown as a source
  metadata      jsonb NOT NULL DEFAULT '{}',    -- region, effective date, ...
  access_group  text NOT NULL DEFAULT 'public', -- filter on this for every search
  embed_model   text NOT NULL,                  -- for example bge-m3; re-embed when it changes
  embedding     vector(1024) NOT NULL           -- 1024 matches bge-m3
);

-- Approximate nearest-neighbour index for cosine similarity search.
CREATE INDEX IF NOT EXISTS chunks_embedding_idx
  ON chunks USING hnsw (embedding vector_cosine_ops);

CREATE INDEX IF NOT EXISTS chunks_access_group_idx ON chunks (access_group);
```

#### env.example

```bash
# Copy this file to .env (in the same folder as docker-compose.yml)
# and replace the password. Never commit the real .env file.
POSTGRES_PASSWORD=change-me
```

### Set up the project

1. **Install Docker** on your machine, then check that it runs.
2. **Create the project folder.** Put the app code, the build file for the app, the documents folder, and one configuration file in it. The configuration file names the ready-made images from the table above, the port the app exposes, and the volumes they use.
3. **Keep secrets out of the code.** Store the database password and any API keys in an environment file that is not committed to version control. The configuration file refers to them by name.
4. **Let the database create its table.** The `init.sql` file creates one row per chunk, holding the ID, document, section, text, metadata, access group, model version, and the vector (1024 numbers for `bge-m3`), plus an index so search does not compare every row. If you choose a different embedding model, change the vector size to match it.
5. **Start everything** with one command from the project folder. The first start downloads the images, and the one-off job then downloads the two models. The models are several gigabytes together, so this takes a while once, and the volume keeps them for later starts.
6. **Run the ingestion job** inside the app container. It reads the documents, chunks them, embeds them in batches, and writes the rows into the database. Run it again whenever the documents change.
7. **Ask a question** through the app's API, or through a simple web page placed in front of it. The reply should contain the answer and the citation numbers.
8. **Check the logs** of each container if something fails. Most problems show up as a container that could not reach another one, or a model that was not downloaded yet.

### Before you put it in front of users

- **Restrict what is exposed.** Only the app should have a port open to users. The database and the LLM server should be reachable only inside the Docker network.
- **Add authentication** to the app, and enforce access groups in the database query, as described in the security section.
- **Back up the database volume** on a schedule, and test that a restore works.
- **Set resource limits** for each container, especially the LLM server, which needs much more memory than the others. A GPU speeds it up a great deal, if your machine or server has one.
- **Pin image versions** instead of always using the latest, so an update does not change the behaviour of your system without you noticing.
- **Log question and answer metadata,** but treat the logs as sensitive, as covered in the security section.

## Going beyond basic RAG

Once the basics work, consider:

- **Query rewriting:** turn a vague or follow-up question ("what about for students?") into a standalone question before searching.
- **Multi-step retrieval:** let the model search again when the first results are not enough, with a limit on the number of steps.
- **Structured data:** for numbers and tables, a database or API lookup often beats text retrieval. Use RAG for the text and tools for the facts.
- **Knowledge graphs or GraphRAG** for questions that need links across many documents. This adds cost and complexity, so start with it only when simpler methods fail your evaluation set.

## Summary

A good RAG system is mostly careful data work: sensible chunks with context, metadata for filtering, hybrid retrieval with reranking, a prompt that enforces grounding and citations, and access control at retrieval time. Build an evaluation set first, measure retrieval and answers separately, and change one thing at a time. The model matters, but the retrieval pipeline usually decides whether users trust the answers.
