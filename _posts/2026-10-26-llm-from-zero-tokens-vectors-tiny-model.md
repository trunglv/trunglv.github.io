---
title: "LLMs from zero: tokens, vectors, and a tiny model you can run"
date: 2026-10-26 09:00:00 +0700
categories: [ai]
lang: en
---

This post is for people who are new to large language models (LLMs) and want to understand the two ideas everything else rests on: the **token** and the **vector**. It ends with a small model you can run on your own computer in under a minute, so the ideas stop being abstract.

You do not need to know calculus or machine learning libraries. You do need to be comfortable with a few numbers and a few lines of Python if you want to run the model yourself.

{% include toc.html %}

## At a glance

| Idea | What it is, in one line | Where it shows up |
|---|---|---|
| Language model | A program that predicts the next piece of text | Every LLM, from the smallest to the largest |
| Token | A piece of text, the unit the model reads and writes | Prices, context limits, and the length of every prompt |
| ID | A number that stands for one token | The model's internal view of text |
| Vector | A list of numbers that describes one token | Where meaning is stored |
| Parameter | A number inside the model, learned during training | Model sizes such as "7B" |
| Probability | How likely each possible next token is | The model's answer, before one token is chosen |
| Training | Adjusting the numbers until predictions improve | How the model is built |

## 1. What an LLM actually does

An LLM does one thing: given some text, it predicts what comes next. Everything it writes is a long chain of these small predictions.

Take the start of a sentence: "The cat sat on the". A model that has read a lot of text might assign these probabilities to the next word:

| Next word | Probability |
|---|---|
| mat | 0.45 |
| floor | 0.20 |
| sofa | 0.15 |
| roof | 0.05 |
| everything else together | 0.15 |

The probabilities add up to 1. The model does not "know" a mat is correct; it has learned that "mat" is the most likely continuation in this kind of sentence. To write a paragraph, it picks one word, appends it, and repeats. Chatting is the same loop, one token at a time.

## 2. Tokens: how text becomes numbers

A computer cannot predict "words" directly. It needs numbers, so the text is first split into **tokens**, and each token is given a number, its **ID**.

What is a token? It depends on how the text is split. There are three common choices:

| Splitting method | Example: "unbelievable" | Trade-off |
|---|---|---|
| By character | u · n · b · e · l · i · e · v · a · b · l · e (12 tokens) | Simple, but very long sequences |
| By word | unbelievable (1 token) | Short sequences, but every new word needs its own entry |
| By subword (what LLMs use) | un · believ · able (3 tokens) | Common pieces get their own token; rare words are built from pieces |

Modern LLMs use subwords. A vocabulary of tens of thousands of pieces covers almost any text, including names and code, because anything unfamiliar can still be spelled out in pieces.

Here is the idea in miniature. Suppose the vocabulary is only these eight characters:

| Character | t | h | e | space | c | a | s | . |
|---|---|---|---|---|---|---|---|---|
| ID | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |

Then "the cat sat." becomes the sequence 0, 1, 2, 3, 4, 5, 0, 3, 6, 5, 0, 7. The model never sees letters at all, only these numbers. It is also why a model can be surprisingly weak at counting the letters in a word: it sees the pieces, not the letters.

Two practical consequences:
- **Cost and limits are counted in tokens.** A rule of thumb for English is about four characters per token, or three-quarters of a word.
- **Languages with accents or unusual scripts often need more tokens** for the same meaning, because their pieces are shorter.

## 3. Vectors: where the meaning is stored

An ID is just a label. "Token 4234" tells the model nothing about what the token means. The fix is to replace each ID with a **vector**: a list of numbers, one row per token, that the model learns during training.

Think of a vector as a set of coordinates. A word becomes a point in a space, and the coordinates describe where it sits. Here is a toy example with two numbers per word, where the first roughly measures "royalty" and the second roughly measures "gender":

| Word | Royalty | Gender | Vector |
|---|---|---|---|
| king | 0.9 | 0.4 | [0.9, 0.4] |
| queen | 0.9 | -0.4 | [0.9, -0.4] |
| man | 0.1 | 0.4 | [0.1, 0.4] |
| woman | 0.1 | -0.4 | [0.1, -0.4] |
| apple | -0.8 | 0.1 | [-0.8, 0.1] |

Nobody wrote "royalty" or "gender" into the model. Those labels are ours, for explaining the picture. In a real model, training discovers its own directions, and there are hundreds or thousands of them.

{% include llm-vector-plane.html %}

Two things follow from the picture:

- **Similarity is distance or angle.** King and queen share a royalty value, so they sit near each other. Apple sits far from all of them. The standard way to measure closeness is the cosine similarity: 1 means the same direction, 0 means unrelated, and negative values mean opposite directions. In our toy numbers, king and queen have a cosine of 0.67, clearly similar, while king and apple have -0.86, pointing the opposite way. One caution about a two-dimensional sketch: with only a gender axis to separate them, man and woman come out as near opposites (-0.88), which is an artefact of having two dimensions. A real model has thousands, most of which the two words share, so they come out similar.
- **Directions can carry relationships.** In our numbers, king minus man gives [0.8, 0], and queen minus woman also gives [0.8, 0]. The same step in the space turns a man into a woman as turns a king into a queen. This is the famous analogy that made embeddings popular: "king − man + woman ≈ queen". Real embeddings show this pattern approximately, not exactly.

So a vector is the model's stored meaning of a token, and the arithmetic on vectors is how it relates one meaning to another.

## 4. What are the parameters?

A **parameter** is one number inside the model whose value is learned during training. When people say a model has "7 billion parameters", they mean it has 7 billion such numbers, all tuned by the training loop in section 6.

Parameters are not text, not tokens, and not memory of your conversation. They are the fixed numbers that turn an input into a prediction. The same parameters are used for every question.

Where they live in a model:

| Part of the model | What its parameters are | Size, in the example model |
|---|---|---|
| Embedding table | One vector per token in the vocabulary | 18 tokens × 8 numbers = 144 |
| Output layer | Turns a vector into one score per token | 8 × 18 = 144 |
| **Total** | | **288 parameters** |

That is the whole tiny model in `tiny_llm.py`. You can count its parameters by hand, and that is the point of the example.

A real transformer has more parts, and the count grows fast. Here is a worked example for a model with a 50,000-token vocabulary, 768-number vectors, 12 layers, and a feed-forward size of 3,072:

| Part | Formula | Parameters |
|---|---|---|
| Embedding table | 50,000 × 768 | 38.4 million |
| Attention, per layer | 4 × 768 × 768 (query, key, value, output) | 2.36 million |
| Feed-forward, per layer | 2 × 768 × 3,072 | 4.72 million |
| One layer | attention + feed-forward | 7.08 million |
| 12 layers | 12 × 7.08 million | 84.9 million |
| **Total** | embedding + 12 layers | **about 123 million** |

The output layer that turns the final vector back into token scores usually reuses the embedding table, so it is not counted twice, and small extras such as biases and normalisation weights are left out. Two things to notice. The embedding table depends on the vocabulary and the vector size. Most of the parameters in a deep model sit in the repeated layers, and the layers' size grows with the square of the vector size. That is why doubling the vector size roughly quadruples the layer parameters.

### Parameters are not the same as tokens or context

| Word | What it means | Example |
|---|---|---|
| Parameter | A learned number inside the model, fixed after training | 123 million in the example above |
| Token | A piece of text in one input or output | "unbelievable" = 3 tokens |
| Context window | The maximum number of tokens the model can read at once | 1 million tokens |

A model with more parameters can learn more patterns, but it does not read more text. Context is a separate limit, set by how the model was built.

### How much memory parameters take

Each parameter is stored as a number, and the precision decides the size. A common format uses 2 bytes per parameter (16-bit floats):

- The 123-million-parameter example: about 247 MB at 2 bytes each.
- A 7-billion-parameter model: about 14 GB at 2 bytes each, before any working memory for the conversation.

This is why large models need powerful graphics cards to run, and why compressing them to fewer bits per parameter, a process called quantization, is a common way to make them fit on a laptop.

### Where the numbers come from

Publicly, parameter counts are usually quoted as a single figure, such as 7B or 70B, without the breakdown above. The breakdown is how you can check such a figure: count the embedding table, the layers, and the output layer, and the total should land near the quoted number. Exact sizes of commercial models are not always published, so treat any specific number for them as an estimate unless the vendor states it.

## 5. From vectors to a prediction

Here is the full path from text to a next-token prediction. The model does five things, and training is the process of making steps 3 and 4 good.

{% include llm-pipeline-simple.html %}

1. **Tokens:** split the text into pieces.
2. **IDs:** look up a number for each piece.
3. **Vectors:** look up the row of numbers for each ID. This is the embedding.
4. **Scores:** multiply the vectors by a weight matrix to get one score per possible next token. A higher score means the model thinks that token is more likely.
5. **Probabilities:** turn the scores into probabilities with a function called softmax, which makes every value positive and the total 1. Then choose a token, usually one of the most likely.

A real LLM does the same five steps, with one large addition: between steps 3 and 4 it applies **attention**, which lets each token look at the tokens before it and mix in their information. That is how "bank" can mean a river edge in one sentence and a financial institution in another. We skip attention in the tiny model below and come back to it at the end.

## 6. Training: how the numbers get learned

At the start, the vectors are random, so the predictions are random too. Training fixes that with a simple loop.

1. **Show the model some text,** and hide the next token.
2. **Predict** a probability for every possible next token.
3. **Measure the error.** The loss is small when the true next token had high probability and large when it had low probability.
4. **Nudge every number** a little in the direction that would have lowered the loss. This is gradient descent. The size of each nudge is the learning rate.
5. **Repeat** millions of times on large amounts of text.

Nothing in this loop tells the model what a noun or a royalty is. It only learns to predict what comes next, and to get good at that it has to build useful vectors. That is the surprising part: prediction alone produces meaning.

## 7. Build a tiny model yourself

The file below contains a complete model with about 100 lines of Python and only numpy. It is not a transformer and has no attention, so it cannot write real sentences. It does contain every concept above: characters as tokens, a table of vectors, probabilities from a softmax, a loss, gradient-based training, and sampling. You can read every line and change it.

**Download:** [tiny_llm.py]({{ "/assets/downloads/tiny-llm/tiny_llm.py" | relative_url }})

**Run it:**

1. Install numpy once: `pip install numpy`
2. Save the file, open a terminal in its folder, and run `python tiny_llm.py`.

It takes about two seconds. The output looks like this, from a real run:

```
vocabulary size: 18 tokens
first 10 characters -> IDs: [('t', 15), ('h', 7), ('e', 5), (' ', 0), ...]
step     1  loss 2.889
step   500  loss 1.162
step  1000  loss 1.131
step  1500  loss 1.126
step  2000  loss 1.125
```

Read the output this way:

- **The vocabulary** is the set of distinct characters in the training text: 18 of them, including the space and the full stop. Each has an ID.
- **The loss** falls from 2.89 to 1.13. At the start, the model is guessing almost uniformly among the 18 characters; a guess that uniform gives a loss of about 2.89 (the log of 18). After training, the loss is much lower, so the model has learned which characters tend to follow which.

The script then prints a sample and the nearest tokens for a few characters. The sample reads something like `the t dog athe ca d che the cathathed...`. It contains the training text's letter patterns, but not real words, because the model only sees one character at a time. The "nearest tokens" lines are also weak for the same reason: with so little data and no context, the vectors are not yet meaningful. Both are useful to see, because they show where the simple model stops.

### What each part of the script does

| Part of the script | Concept |
|---|---|
| The corpus and the vocabulary | Tokens and IDs |
| The table `E` | The embedding table: one row of 8 numbers per token |
| The matrix `W` and `softmax` | Turning vectors into scores and probabilities |
| The loss | How wrong the prediction was |
| The gradient lines | How each number should move to reduce the loss |
| The training loop | Learning by nudging, repeated 2,000 times |
| `generate` | Sampling one token at a time, feeding each back in |
| `nearest` | Cosine similarity, measuring closeness of vectors |

### Things to try

- **Change the text.** Replace the corpus with your own sentences and see what the sample looks like.
- **Change the vector size.** Set `D` to 2 and then to 32. Small vectors learn less; larger ones fit more detail, and the loss is lower.
- **Change the number of steps.** Compare the loss at 200 steps with the loss at 2,000.
- **Change the temperature.** It is set to 0.8 in `generate`. Lower values give safer, more repetitive text; higher values give more random text.

## 8. What is missing, and how a real LLM differs

The tiny model has one weakness that explains the whole field: it looks only at the previous character. A real LLM looks at thousands of previous tokens, and that is what attention adds.

| | Tiny model in this post | A real LLM |
|---|---|---|
| Unit | One character | Subword tokens, tens of thousands in the vocabulary |
| Context | The previous token only | Up to hundreds of thousands or millions of tokens |
| Vectors | 8 numbers per token | Thousands of numbers per token |
| Between vectors and scores | Nothing; one weight matrix | Many layers, each with attention and a small network |
| Parameters | 288 | Billions |
| Training data | About 2,900 characters | Trillions of tokens |

The ideas are the same at every scale. Only the size of the table, the number of layers, and the amount of data change. Once the pipeline in section 5 makes sense, the rest of an LLM is a matter of scale and of attention, which is the next thing to learn.

## 9. How a system like Claude is built

Anthropic does not publish every detail of how Claude is trained, so this is the general pipeline that most modern assistants follow. It shows how the ideas in this post grow into a product.

1. **Collect and filter data.** Large amounts of text and code are gathered and cleaned for quality and safety.
2. **Pretraining.** The model learns to predict the next token over this data. This is the same loop as the tiny model in this post, scaled up: a transformer with attention, billions of parameters, and far more text.
3. **Supervised fine-tuning.** The model is trained on examples of good conversations, so it learns the format and manners of an assistant instead of simply continuing text.
4. **Feedback-based training.** Responses are compared, and the model is tuned toward the ones people or a model judged better. Anthropic has described Constitutional AI, in which the model critiques and revises its own answers against a set of written principles.
5. **Evaluation and safety testing.** Capabilities and failures are measured before release. Problems found here send the team back to earlier steps.
6. **Serving.** The trained model runs on large clusters, with optimised inference, prompt caching, and limits on use.
7. **The products around the model.** System prompts, tools, and harnesses such as Claude Code shape what the model does in practice. The model requests a tool; the harness runs it and sends the result back.

The core is still a next-token predictor, the same kind of thing the tiny model learns. What changes from step to step is the data, the feedback, and the system around the model.

## 10. Serving a model: what a hosting server does

A trained model is a set of files. To answer anyone, a program has to load those numbers into memory and run the pipeline from section 5 for every request, fast, for many people at once. That program is an inference server. This section is what sits behind an API such as the one Ollama exposes in the RAG post's Docker setup.

### What the model is on disk

| File | What it holds | Why the server needs it |
|---|---|---|
| Weights | The parameters, as large arrays of numbers. Common formats: safetensors (used by the Hugging Face ecosystem) and GGUF (used by llama.cpp and Ollama). Big models are split into several files | This is the model. At 16-bit precision a 7B model is about 14 GB; quantized to 4 bits, about 3.5 GB |
| Tokenizer | The vocabulary and the rules for splitting text | Text must be turned into exactly the IDs the model was trained on. A mismatched tokenizer produces nonsense |
| Config | Number of layers, vector size, attention heads, context length, special tokens | Tells the server how to build the network before loading the weights into it |
| Chat template | How a list of messages becomes one token sequence, with markers for system, user, and assistant turns | A chat model expects its own markers; the wrong template degrades answers |

Ollama keeps these in its models directory, which is why the RAG post's `docker-compose.yml` mounts a volume at `/root/.ollama`: the files are downloaded once and survive restarts.

### Tools you need

| Layer | Role | Common open-source choices |
|---|---|---|
| Inference server | Loads the weights, exposes an API, batches requests, manages GPU memory | vLLM, SGLang, Text Generation Inference for GPU servers with many users; llama.cpp and Ollama for a laptop or a single consumer GPU |
| Runtime | Drivers and libraries that let the server use the hardware | NVIDIA drivers with CUDA (or ROCm for AMD, Metal on Apple silicon); Docker with the NVIDIA Container Toolkit to run it in a container |
| API | The interface clients call | HTTP, usually in the OpenAI-compatible shape (`/v1/chat/completions`), with streaming over server-sent events |
| Gateway | What sits in front of the server | A reverse proxy such as nginx or Caddy for TLS, API keys, and rate limits |
| Observability | Knowing what the server is doing | Logs plus metrics such as tokens per second, queue length, and GPU memory, typically with Prometheus and Grafana |
| Model source | Where the files come from | The Hugging Face Hub, or `ollama pull` for Ollama's library |

### Memory: what has to fit on the GPU

Two things live in GPU memory while the server runs, and the second one is the one people forget.

- **The weights,** loaded once and fixed: about 14 GB for a 7B model at 16 bits.
- **The KV cache,** one per active request, which grows with every token in that request. It stores the attention state so the model does not recompute the whole conversation for each new token. For a 7B-class model with standard attention (32 layers, vectors of 4,096 numbers, 16-bit values), it costs 2 × 32 × 4,096 × 2 bytes, about 0.5 MB per token. A 4,000-token conversation uses about 2 GB; eight such conversations at once use about 17 GB, more than the weights themselves. Many recent models use grouped-query attention, which cuts this several times.

So the server size is decided by context length and concurrency as much as by parameter count. Quantizing the weights frees memory for more cache, at some cost in quality. vLLM's paged attention manages the cache in fixed blocks, like an operating system paging memory, so long and short requests can share the GPU without wasting space.

### What happens when a request arrives

{% include llm-serving-flow.html %}

1. **The client sends a request** over HTTP: a list of messages, the model name, and settings such as temperature and the maximum number of output tokens.
2. **Template and tokenize.** The server applies the chat template to turn the messages into one string, then the tokenizer turns the string into IDs. This is where the token count of your prompt is decided.
3. **Schedule.** A scheduler adds the request to the batch that is already running. Modern servers use continuous batching: new requests join and finished ones leave at every step, instead of waiting for a whole batch to finish.
4. **Prefill.** All prompt tokens go through the model in one parallel pass, which produces the KV cache for the request and the first output token. If a prompt cache is enabled and the prompt shares a prefix with a recent request, that part of the cache is reused instead of recomputed. This is the prompt cache from the Claude Code post, seen from the server side.
5. **Decode.** The model produces one token per step for every request in the batch, samples it according to temperature and the other settings, appends it, and extends the KV cache. Each token is detokenized and streamed to the client as it is produced, which is why replies appear word by word.
6. **Stop.** The reply ends at a stop token, the output limit, or a stop sequence. The KV cache is freed, and the response carries the usage: prompt tokens, output tokens, and, where supported, cached tokens.

### Why this shapes cost and speed

- **Prefill is parallel, decode is sequential.** Prefill is limited by raw compute; decode is limited by how fast the GPU can read the weights for each step. That is the mechanical reason output tokens are slower and pricier than input tokens.
- **Batching raises throughput.** Many requests share each decode step, so the server produces far more tokens per second in total, at a small cost in latency for each user.
- **Memory decides how many users fit.** Once the KV cache fills the GPU, new requests queue. Shorter contexts, quantization, and grouped-query attention all raise the number of concurrent users.

### A minimal setup to try

On a laptop, Ollama is the simplest path: `ollama pull qwen2.5:7b` downloads the files, and `ollama serve` exposes an API at `http://localhost:11434`. The Docker Compose in the RAG post does exactly this in a container. For a server with a real GPU and several users, run vLLM in Docker with the model name as an argument; it exposes an OpenAI-compatible API, and a reverse proxy in front of it adds TLS and API keys.

## Check yourself

{% include llm-quiz.html %}

## Summary

An LLM predicts the next token. A token is a piece of text, turned into an ID, and an ID is turned into a vector: a list of numbers that holds the token's learned meaning. Closeness between vectors reflects closeness in meaning, and training is nothing more than nudging these numbers until the right next token gets a higher probability. Run the tiny model, change one thing at a time, and you will see each of these ideas working.
