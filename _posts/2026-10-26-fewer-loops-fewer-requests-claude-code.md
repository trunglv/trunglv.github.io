---
title: "Fewer loops, fewer requests: managing what a task costs in Claude Code"
date: 2026-10-26 19:30:00 +0700
categories: [ai]
lang: en
---

A task in Claude Code is not one request to the model. It is a loop of requests, and the number of requests, times the size of each, is what you pay. This post is about managing that number: how to see it, how to work so it stays small, which tools and models to route work to, and, if you run Claude Code from an automated pipeline, how to evaluate a prompt *before* it is sent so a vague one never starts an expensive loop.

It builds on the [post about how Claude Code works]({% post_url 2026-10-26-how-claude-code-works-sessions-cache-tokens %}), which explains the turn loop, the prompt cache, and the token kinds. Here the question is narrower and more practical: what do I do with that knowledge, day to day and in automation?

{% include toc.html %}

## At a glance

| Question | Short answer |
|---|---|
| Is one loop one request? | One *iteration* is one request. One task is usually many iterations: tool calls + 1 |
| What does a task cost? | Roughly (context size × number of requests × cache-read price) + output tokens × output price |
| The two levers | Fewer requests, and a smaller context in each request |
| How to see it | Status line, `/context`, `/usage` or `/cost`, the session JSONL files |
| How to route it | Model and effort chosen per session, subagents on a cheaper model, local models for trivia |
| How to enforce it | Hooks, `--max-turns`, plan mode, permission allowlists |
| Before sending, in automation | A gate: rule checks, `count_tokens`, a cheap classifier, then a decision |

## 1. What a loop is, and why one message costs many requests

When you send a message, Claude Code does the following:

1. It sends the whole conversation plus your message to the model. That is one request.
2. The model answers with either text, which ends the turn, or a tool call: read this file, run this command, edit that line.
3. Claude Code runs the tool, appends the result to the conversation, and sends everything again. Another request.
4. This repeats until the model answers with text only.

So one *turn* (one message from you) is one loop of N requests, where N is the number of tool calls plus one. A message like "push it" can be four requests: the commit, the push, a check that the deploy finished, and the reply. A refactor across several files can be fifty. In the session analysed in the earlier post, 1,593 requests were spread across far fewer messages; that ratio is normal.

Every request re-sends the full context. Most of it is served from the prompt cache at a fraction of the price, which is why the cache hit rate matters so much, but a cache read is not free, and the context grows with every tool result that lands in it. The cost of a task is therefore:

> **(context size × number of requests × cache-read price) + (output tokens × output price)**

Output includes thinking tokens, which were 28.7% of output in that session. Two levers follow: make fewer requests, and keep each one smaller.

## 2. See it: the measurement tools

You cannot manage what you do not see, and most of the seeing is built in.

| Tool | What it shows | When to use it |
|---|---|---|
| Status line | Context size, model, and cost live in the terminal bar | Always on; `/statusline` sets it up once |
| `/context` | What is in the window right now, by component: system prompt, CLAUDE.md, memory, MCP tools, messages, and how full it is | Before deciding to `/compact` or `/clear`. It tells you *what* is bloating the requests |
| `/usage` (subscription) or `/cost` (API key) | Tokens and cost for the session, and plan limits | Once an hour in a long session |
| Session files `~/.claude/projects/<project>/*.jsonl` | Every request with its usage: input, cache read, cache write, output | For analysis: requests per task, cache hit rate, thinking share. A short script does it |
| `ccusage` (community CLI, `npx ccusage`) | Daily and monthly totals read from those JSONL files | A weekly look at where the money went |
| OpenTelemetry export (`CLAUDE_CODE_ENABLE_TELEMETRY=1`) | Metrics and events to Prometheus, Grafana, or any OTel backend | Teams and several machines; more than one person needs |

The single most useful habit is to glance at the context size in the status line. When it passes about half the window, every request costs roughly double what it did at the start, and that is the moment to decide whether the old context is still earning its place.

## 3. Work so the loop stays short

### Before the task: load context in one message, not through exploration

- Name the files, the function, the expected behaviour, and the constraints in the first message. Every "which file is it?" the model answers by reading is one to three requests you could have skipped.
- Put stable facts in `CLAUDE.md`: the build command, the test command, where things live. They are read once from cache instead of rediscovered each session.
- For a non-trivial change, use plan mode first. One short loop produces a plan, you approve it, and the execution loop runs without mid-course corrections. A correction after the fact costs the whole redo loop.

### During the task: let one request do more

- Ask for the whole piece of work in one message: "add the section, the diagram, update the quiz, verify the build." Independent tool calls run in parallel inside a single request; the same work in three messages is three loops with three verifications.
- Say what verification you want ("run the tests, no screenshots"). Unasked verification is extra requests; asked-for verification is planned and cheap.
- Use `/btw` for side questions. The answer does not enter the conversation, so the question is not re-sent in every later request.
- If you already know you want to push, say "do X, then push." A separate "push" message is a separate loop.

### Big or unrelated subtasks: isolate them

- A subagent runs its own loop in its own context and returns only the result. Use it for a search or a review whose intermediate output you do not need; the main context stays small, so every later request is cheaper.
- Unrelated small tasks: `/clear` between them, or separate sessions. Carrying task A's sixty thousand tokens into task B makes every request in B pay for A.
- `/compact` when a long task is half done and the early exploration no longer matters.

### Shrink each request, not only the count

- Keep tool output small: `grep` instead of reading a 2,000-line file; `tail` a log. Every result is appended to the context and re-sent in every later request.
- Pick effort and model for the task. A routine edit at lower effort means fewer thinking tokens per request.
- Do not paste large files into the chat when the model can read the part it needs.

### The habit that covers most of it

Batch by day, as in the daily-routine section of the earlier post. Collect the small things, write one message with the list, let one loop handle them, review once, push once. Ten separate "fix this small thing" messages are ten loops, each re-sending the full context and each ending with its own verification.

## 4. Route it: models, effort, and where the work runs

| Lever | How | Effect |
|---|---|---|
| Model per session | `/model`, or `claude --model sonnet` | Routine edits, formatting, and test fixes on a mid-size model; design, hard debugging, and review on the strongest one. Switching mid-session invalidates the cache, so decide per session, not per message |
| Effort | `/effort`, or `--effort low\|medium\|high` | Lower effort means fewer thinking tokens per request. Thinking is billed as output |
| Subagents on a cheaper model | `model: haiku` in the frontmatter of `.claude/agents/<name>.md` | Searches, summaries, and "find where X is used" run on a cheap model in their own context and return a short result |
| Tool search | `ENABLE_TOOL_SEARCH` (auto by default) | Keeps MCP tool definitions out of every request until they are needed; matters once you have more than a handful of servers |
| A local model for trivia | Ollama with a 7B model, as in the [RAG post]({% post_url 2026-10-25-retrieval-augmented-generation-guide %}) | Grammar checks, quick lookups, commit messages. Not a replacement for Claude Code; it keeps the cheap questions out of the expensive loop |
| Fast mode | `/fast` | Same model, faster output. A latency tool, not a cost tool |

## 5. Enforce it: hooks, limits, and settings

Hooks run shell commands at fixed points in the loop. They are the only way to enforce a habit instead of remembering it.

- **PreToolUse on Bash**: refuse a `cat` of a huge file or a `git log` without `-n`, so oversized output never enters the context.
- **PostToolUse on Edit**: run the formatter or linter automatically, so the model does not spend a request on "now run the linter."
- **Stop**: print the context usage when a turn ends, so you see the size before writing the next message.
- **UserPromptSubmit**: runs *before* the prompt is processed. It can block the prompt (exit code 2 with a message), or add context by printing to stdout. Section 7 is built on this one.

Beyond hooks: permission allowlists so routine read-only commands do not stop for approval (each approval is a pause that breaks batching), and in headless runs `--max-turns N` as a hard ceiling on the loop.

## 6. In order, for one person

1. `/statusline` once, so the context size is always visible.
2. One `explore`-style subagent on a cheap model for searches.
3. A PreToolUse hook that limits `cat` and `head` output.
4. `npx ccusage` once a week to see the trend.
5. Model and effort chosen at the start of each session by the kind of work, and not switched mid-way.

## 7. Evaluate before you send: a gate for automated pipelines

Everything above assumes a person typing. If a tool produces the prompts, for example a ticket system, a scheduler, or your own harness that calls `claude -p` or the Agent SDK, you can do better than a person: evaluate every prompt before it starts a loop. The gate answers three questions: *how much will this cost*, *is it worth sending at all*, and *with which model and limits*.

{% include cc-gate-pipeline.html %}

### Step 1. Rule checks, which cost nothing

- The prompt asks for a code change but names no file, function, or test. Send it back for detail.
- The prompt is very short, or is mostly a pasted log. Trim the log to the failing lines before sending.
- The prompt matches one that already ran (compare against the history from step 4). Return the earlier result or ask whether to redo it.
- The current context, from the session file, is above a threshold such as 70% of the window. Start a fresh session for this prompt.

### Step 2. Count tokens, and estimate the loop

The API has a `count_tokens` endpoint, free of charge, that accepts the same system prompt, tools, and messages as a real request and returns the input token count. That gives the exact size of the first request.

The first request is not the loop. Estimate the loop with the formula from section 1, using two inputs you already have:

- the current context size, from the `usage` field of the last request in the session JSONL;
- the number of requests a task of this type usually takes, from your own history: explain or read tasks take about two to four, a single-file edit five to ten, a multi-file refactor twenty or more. Your numbers will differ; the point is to record them.

For a large task, a dry run is cheaper than a guess: `claude -p "..." --permission-mode plan` spends a short loop and returns a plan that lists the files it would touch. The pipeline reads the plan and decides whether to run it for real.

### Step 3. Classify with a cheap model

Before the prompt goes anywhere near Claude Code, send it to a cheap model (the smallest Claude model, or a local 7B model through Ollama) with a fixed instruction: return a small JSON with the task type, how clear the prompt is, the recommended model and effort, and a turn limit. This costs a few hundred tokens.

| Classification | What the gate does |
|---|---|
| Knowledge question, no repository needed | Answer with the cheap or local model; Claude Code is never called |
| Vague: missing file, missing definition of done | Do not send. Return a clarifying question. One loop spent guessing costs more than one question |
| Small, clear edit | Mid-size model, low effort, `--max-turns 10` |
| Design, hard debugging, review | Strongest model, high effort, a generous turn limit |
| Duplicate of recent work | Return the earlier result, or ask |

### Step 4. Run with limits, then record the usage

In headless mode each call carries the limits the gate chose: `--model`, the effort, and `--max-turns`. With `--output-format json` the result includes the usage, which the pipeline writes to its history: task type, requests used, tokens, cost. That history is what makes step 2 accurate next time. If the turn limit is hit before the task is done, the pipeline decides whether to continue, instead of a loop that runs until something stops it.

### The same gate inside interactive Claude Code

If you type the prompts yourself, the `UserPromptSubmit` hook gives you the gate without an external tool. The hook receives the prompt on standard input and can:

- block it, with a message, when it is vague or when the context is already too full ("`/clear` first");
- add context by printing to standard output, for example the result of a `grep` for the function named in the prompt, so the model does not spend two or three requests finding it;
- call the classifier from step 3 and print a one-line suggestion, such as "this looks like a small edit; a lower effort would do."

You do not have to write this hook yourself. [prompt-improver](https://github.com/severity1/claude-code-prompt-improver) is a community plugin, not part of Claude Code, that does this kind of thing: it uses hooks on prompt submit, tool use, and subagent start to add context, and includes a `prompt-improver` skill for vague prompts. It is a reasonable place to start if you type prompts by hand and want the gate without building it. Read its hooks before you install it, since they run on every prompt, and treat it as one option next to writing your own. A similar hook-based project, [prompt-improver-r2r](https://github.com/evgenygurin/prompt-improver-r2r), uses a skill-based design; its README claims a large token reduction, which we have not verified. Plugin hooks have had installation problems in some Claude Code versions, so copying the hook into `settings.json` by hand is the more reliable route.

### What the gate costs

The rule checks are free, `count_tokens` is free, and the classifier is a few hundred tokens on a cheap model. A wasted loop on a vague prompt is five to twenty requests, each re-sending the whole context. The gate pays for itself the first time it sends a question back instead of a loop out.

## Summary

- One loop iteration is one request; one task is tool calls + 1 requests, each re-sending the full context. Cost is roughly context size × requests × cache-read price, plus output.
- See it with the status line, `/context`, `/usage` or `/cost`, and the session JSONL files.
- Keep loops short: full context in the first message, plan mode for big changes, one message for related work, `/btw` for side questions, subagents and `/clear` for isolation, small tool output.
- Route by session: model and effort by kind of work, cheap models for subagents and trivia.
- Enforce with hooks, `--max-turns`, and permission allowlists.
- In automation, put a gate in front: rule checks, `count_tokens`, a cheap classifier, then one of four decisions. Record the usage after each run so the next estimate improves.
