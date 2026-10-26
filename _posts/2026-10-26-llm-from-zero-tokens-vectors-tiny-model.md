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
| king | 0.9 | 0.8 | [0.9, 0.8] |
| queen | 0.9 | -0.8 | [0.9, -0.8] |
| man | 0.1 | 0.8 | [0.1, 0.8] |
| woman | 0.1 | -0.8 | [0.1, -0.8] |
| apple | -0.8 | 0.1 | [-0.8, 0.1] |

Nobody wrote "royalty" or "gender" into the model. Those labels are ours, for explaining the picture. In a real model, training discovers its own directions, and there are hundreds or thousands of them.

{% include llm-vector-plane.html %}

Two things follow from the picture:

- **Similarity is distance or angle.** King and queen share a royalty value, so they sit near each other. Apple sits far from all of them. The standard way to measure closeness is the cosine similarity: 1 means the same direction, 0 means unrelated, and negative values mean opposite directions. In our toy numbers, king and queen have a cosine of 0.12 because they differ in gender, while king and apple have -0.66.
- **Directions can carry relationships.** In our numbers, king minus man gives [0.8, 0], and queen minus woman also gives [0.8, 0]. The same step in the space turns a man into a woman as turns a king into a queen. This is the famous analogy that made embeddings popular: "king − man + woman ≈ queen". Real embeddings show this pattern approximately, not exactly.

So a vector is the model's stored meaning of a token, and the arithmetic on vectors is how it relates one meaning to another.

## 4. From vectors to a prediction

Here is the full path from text to a next-token prediction. The model does five things, and training is the process of making steps 3 and 4 good.

{% include llm-pipeline-simple.html %}

1. **Tokens:** split the text into pieces.
2. **IDs:** look up a number for each piece.
3. **Vectors:** look up the row of numbers for each ID. This is the embedding.
4. **Scores:** multiply the vectors by a weight matrix to get one score per possible next token. A higher score means the model thinks that token is more likely.
5. **Probabilities:** turn the scores into probabilities with a function called softmax, which makes every value positive and the total 1. Then choose a token, usually one of the most likely.

A real LLM does the same five steps, with one large addition: between steps 3 and 4 it applies **attention**, which lets each token look at the tokens before it and mix in their information. That is how "bank" can mean a river edge in one sentence and a financial institution in another. We skip attention in the tiny model below and come back to it at the end.

## 5. Training: how the numbers get learned

At the start, the vectors are random, so the predictions are random too. Training fixes that with a simple loop.

1. **Show the model some text,** and hide the next token.
2. **Predict** a probability for every possible next token.
3. **Measure the error.** The loss is small when the true next token had high probability and large when it had low probability.
4. **Nudge every number** a little in the direction that would have lowered the loss. This is gradient descent. The size of each nudge is the learning rate.
5. **Repeat** millions of times on large amounts of text.

Nothing in this loop tells the model what a noun or a royalty is. It only learns to predict what comes next, and to get good at that it has to build useful vectors. That is the surprising part: prediction alone produces meaning.

## 6. Build a tiny model yourself

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

## 7. What is missing, and how a real LLM differs

The tiny model has one weakness that explains the whole field: it looks only at the previous character. A real LLM looks at thousands of previous tokens, and that is what attention adds.

| | Tiny model in this post | A real LLM |
|---|---|---|
| Unit | One character | Subword tokens, tens of thousands in the vocabulary |
| Context | The previous token only | Up to hundreds of thousands or millions of tokens |
| Vectors | 8 numbers per token | Thousands of numbers per token |
| Between vectors and scores | Nothing; one weight matrix | Many layers, each with attention and a small network |
| Parameters | About 300 numbers | Billions |
| Training data | About 2,900 characters | Trillions of tokens |

The ideas are the same at every scale. Only the size of the table, the number of layers, and the amount of data change. Once the pipeline in section 4 makes sense, the rest of an LLM is a matter of scale and of attention, which is the next thing to learn.

## Summary

An LLM predicts the next token. A token is a piece of text, turned into an ID, and an ID is turned into a vector: a list of numbers that holds the token's learned meaning. Closeness between vectors reflects closeness in meaning, and training is nothing more than nudging these numbers until the right next token gets a higher probability. Run the tiny model, change one thing at a time, and you will see each of these ideas working.
