"""A tiny language model, written so every step is visible.

It learns to predict the next character from the previous one, using a
table of vectors (the embeddings) and one weight matrix. It is not a
transformer, but it uses the same ideas: tokens become IDs, IDs become
vectors, vectors become a probability for every possible next token, and
training nudges the numbers so the right token gets a higher probability.

Only numpy is needed:  pip install numpy
Run:                   python tiny_llm.py
"""

import numpy as np

# 1. The corpus: a tiny text the model will learn from.
TEXT = (
    "the cat sat on the mat. the dog sat on the rug. "
    "the cat chased the dog. the dog chased the cat. "
    "a cat is a small animal. a dog is a loyal animal. "
) * 20

# 2. Tokens: here one token is one character. The vocabulary maps each
#    distinct character to an integer ID.
vocab = sorted(set(TEXT))
stoi = {ch: i for i, ch in enumerate(vocab)}   # character -> ID
itos = {i: ch for ch, i in stoi.items()}       # ID -> character
V = len(vocab)

ids = np.array([stoi[ch] for ch in TEXT])
print(f"vocabulary size: {V} tokens")
print(f"first 10 characters -> IDs: {[(TEXT[i], int(ids[i])) for i in range(10)]}")

# 3. Vectors: every token ID gets a row of D numbers. These rows are the
#    embedding table. At the start they are random; training shapes them.
D = 8
rng = np.random.default_rng(0)
E = rng.normal(0, 0.1, size=(V, D))    # embedding table: V tokens x D numbers
W = rng.normal(0, 0.1, size=(D, V))    # output layer: turns a vector into V scores

def softmax(z):
    z = z - z.max(axis=1, keepdims=True)
    e = np.exp(z)
    return e / e.sum(axis=1, keepdims=True)

# 4. Training: for each position, the input is the current token and the
#    target is the next token. The model guesses a probability for every
#    token; the loss is small when the right token gets high probability.
x = ids[:-1]          # current token IDs
y = ids[1:]           # next token IDs
N = len(x)
LR = 0.5              # learning rate: how big each nudge is
STEPS = 2000

# On some macOS builds numpy's BLAS reports spurious divide/overflow flags
# on matmul; the explicit finiteness check below is what guards the numbers.
with np.errstate(divide="ignore", over="ignore", invalid="ignore"):
    for step in range(1, STEPS + 1):
        h = E[x]                          # look up a vector for each current token
        logits = h @ W                    # score every possible next token
        p = softmax(logits)               # turn scores into probabilities
        loss = -np.log(p[np.arange(N), y] + 1e-12).mean()

        # Gradient: how much each number should change to lower the loss.
        dlogits = p.copy()
        dlogits[np.arange(N), y] -= 1
        dlogits /= N
        dW = h.T @ dlogits
        dh = dlogits @ W.T
        dE = np.zeros_like(E)
        np.add.at(dE, x, dh)              # send gradients back to the used rows

        assert np.isfinite(logits).all() and np.isfinite(dW).all() and np.isfinite(dE).all(), f"non-finite values at step {step}"
        W -= LR * dW                      # nudge the numbers a little
        E -= LR * dE

        if step % 500 == 0 or step == 1:
            print(f"step {step:5d}  loss {loss:.3f}")

# 5. Generation: start from one character and sample the next one, again
#    and again, from the probabilities the model produces.
def generate(start, length=60, temperature=0.8, seed=1):
    rng2 = np.random.default_rng(seed)
    out = [stoi[start]]
    for _ in range(length):
        probs = softmax((E[out[-1]] @ W)[None, :])[0]
        probs = probs ** (1 / temperature)     # lower temperature = safer choices
        probs /= probs.sum()
        out.append(rng2.choice(V, p=probs))
    return "".join(itos[i] for i in out)

print("\nsample starting with 't':")
print(generate("t"))

# 6. Look at one vector: which tokens end up close to which?
def nearest(ch, k=3):
    v = E[stoi[ch]]
    sims = (E @ v) / (np.linalg.norm(E, axis=1) * np.linalg.norm(v) + 1e-12)
    order = np.argsort(-sims)
    return [(itos[i], round(float(sims[i]), 2)) for i in order if i != stoi[ch]][:k]

print("\nnearest tokens by cosine similarity (vector closeness):")
for ch in ["c", "d", "a"]:
    print(f"  {ch!r}: {nearest(ch)}")
