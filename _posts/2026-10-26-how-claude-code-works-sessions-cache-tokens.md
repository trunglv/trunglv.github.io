---
title: "How Claude Code works: the loop, sessions, the prompt cache, and where your tokens go"
date: 2026-10-26 08:30:00 +0700
categories: [ai]
lang: en
---

This is a long working note on how Claude Code works underneath, written for myself and for anyone who uses it daily and wants to understand the bill. It answers the questions I kept asking: what is actually sent to the model, how a session is stored, whether saved history makes the next session cheaper, whether MCP servers save tokens, and what to do about all of it.

Everything here comes from the official docs at code.claude.com and platform.claude.com as of October 2026, plus measurements from my own session transcript. Where I measured something myself, I say so. Where the docs were unclear, I say that too. Claude Code changes often, so check the docs before relying on a specific number.

{% include toc.html %}

## At a glance

| Question | Short answer |
|---|---|
| What does the model see on each request? | Everything, every time: system prompt, CLAUDE.md, tool definitions, the whole conversation, and your new message. The model keeps nothing between requests. |
| How many API requests is one turn? | One per model reply. A turn with ten tool calls is about eleven requests, each carrying the whole conversation. |
| Where is my session saved? | A plain-text JSONL file under `~/.claude/projects/<project>/`. It keeps every message, tool call, result, and token count. |
| Does saved history make the next session cheaper? | No. Resuming re-sends the whole conversation. What makes it cheaper is the prompt cache, and only while the cache is still warm. |
| What actually saves tokens inside a session? | The prompt cache. In my session, 96.7% of all prompt tokens were cache reads, billed at a fraction of the normal price. |
| Do MCP servers save tokens? | Not by themselves. A good tool saves tokens when its answer replaces reading files. Its tool definitions and outputs cost tokens, which Claude Code now limits by default. |
| What costs the most? | Reading large files and command outputs into context, long sessions without `/clear`, extended thinking, and subagents that run their own conversations. |

## Part 1: What happens in one turn

The model behind Claude Code is stateless. It does not remember your last message, your project, or the file it read a minute ago. Every API request must contain everything the model needs. Claude Code is the program that assembles that request, runs the tools the model asks for, and keeps the conversation going. The docs call it the agentic harness: the layer around the model that provides the tools and manages the context the model sees.

{% include cc-turn-loop.html %}

A turn works like this:

1. You type a prompt.
2. Claude Code builds a request: the system prompt, your CLAUDE.md files and auto memory, the tool definitions, every earlier message and tool result, and your new message.
3. The model replies. The reply is either text for you, or an instruction to run a tool with certain arguments.
4. If it is a tool call, Claude Code runs the tool on your machine (reading a file, running a shell command, calling an MCP server), appends the result to the conversation, and sends the whole conversation again.
5. This repeats until the model replies with text only. Then the turn ends.

Two consequences follow. First, one turn can be many requests. The docs put it plainly: each time Claude uses tools, it sends another request carrying that batch of tool results. Second, every one of those requests carries everything that came before, so the cost of a request grows with the length of the conversation. This is why the prompt cache (Part 4) matters so much. Without it, a long session would be unaffordable.

## Part 2: The context window

The context window is the maximum amount of text the model can take in one request. Everything in the request counts against it: the conversation, file contents, command outputs, CLAUDE.md, auto memory, loaded skills, system instructions, and the model's own output.

### Sizes

Current models default to a 1 million token window, including Fable 5.1, Fable 5, Sonnet 5 and later, Haiku 5.5, and Opus 4.7 and later. Opus 4.6 and Sonnet 4.6 default to 200K, with a 1M variant available by adding `[1m]` to the model name. A million tokens is roughly 750,000 English words, which sounds like a lot until you watch a test suite's output land in context.

### What happens when it fills up

Claude Code compacts automatically as you approach the limit: it summarises the conversation so far and continues with the summary plus the most recent messages. You can move that point earlier with `/autocompact <size>` (for example `/autocompact 500k`), the `--autocompact` flag, the `CLAUDE_CODE_AUTO_COMPACT_WINDOW` variable, or `autoCompactWindow` in settings.

You can also compact by hand, and this is more useful than it sounds:

- `/compact` summarises the conversation and frees context. Pass focus instructions to control what the summary keeps: `/compact focus on the auth bug fix`.
- `/clear` starts a new conversation with empty context. The docs recommend `/compact` when you want to continue the same work, and `/clear` between unrelated tasks.
- `/context` shows a coloured grid of what is using the window, with suggestions about context-heavy tools and memory bloat. It also shows which CLAUDE.md and memory files loaded, and which MCP tools are deferred.

One detail that surprised me: output tokens count too. Raising `CLAUDE_CODE_MAX_OUTPUT_TOKENS` reduces the context available before auto-compaction triggers, because Claude Code reserves room for the reply.

## Part 3: Sessions and history

### Where a session lives

While you work, Claude Code appends every event to a transcript file:

```
~/.claude/projects/<project>/<session-id>.jsonl
```

`<project>` is your working directory path with non-alphanumeric characters replaced by `-`. The file is JSON Lines: one JSON record per line. I opened the transcript of the session that wrote this post. It had 8,385 lines and about 26 MB, and the records included user messages, assistant replies, tool results, file snapshots, and, on every assistant reply, a usage block with the exact token counts for that request. That usage block is where the numbers in Part 4 come from.

Two warnings from the docs. The record format is internal and changes between versions, so scripts that parse it directly can break; use `/export` if you want a stable copy. And transcripts are deleted after `cleanupPeriodDays`, which is 30 days by default.

{% include cc-session-resume.html %}

### Resuming

| Command | What it does |
|---|---|
| `claude --continue` | Reopen the most recent session in the current directory |
| `claude --resume` | Pick a session from a list |
| `claude --resume <name or path>` | Reopen a named session or a transcript file |
| `/resume` | Switch session from inside Claude Code |
| `--fork-session` or `/branch` | Copy the history into a new session ID, leaving the original alone |

Resuming reopens the session under the same ID and appends new messages to it. It restores the history, the model, the permission mode, and interrupted tool calls (marked as cut off). If the session was compacted before, it continues from the last summary plus everything after it.

### Does saved history make the next session cheaper?

No, and this is the most common misunderstanding. The history on disk is just a file. It costs nothing to keep, and it saves nothing by itself. When you resume, the docs are explicit: Claude Code sends the whole conversation again, and the request reads from the cache whatever part of its prefix is unchanged and still within the cache lifetime.

So resuming a long session costs input tokens for the entire history. If the cache is still warm (Part 4), most of those tokens are cheap cache reads. If it has expired, the first request after resume writes it all into the cache again at a premium, and later requests are cheap again. On Pro and Max plans, the resume dialog shows an estimate of how much of your usage limit the saved conversation will take, which is a hint of this cost.

What does carry over cheaply between sessions is knowledge, not conversation: CLAUDE.md and auto memory (Part 5) are small and loaded every time, so Claude does not have to rediscover how your project works. A new session starts with a fresh context window, and that is usually what you want.

## Part 4: The prompt cache, the thing that actually saves tokens

### How it works

Prompt caching is a feature of the Claude API. When a request's beginning (its prefix) is identical to a recent request's beginning, the API reuses its processing of that prefix instead of redoing it, and charges much less for it. Claude Code uses it automatically.

The docs describe the cached prefix as three layers, in this order:

| Layer | Contents | Changes when |
|---|---|---|
| 1 | System prompt, core instructions, tool definitions | The tool set changes (for example, an MCP server is added or removed) |
| 2 | Project context: CLAUDE.md, auto memory, rules without a path scope | At session start, or after `/clear` or `/compact` |
| 3 | The conversation | Every turn, but only by appending at the end |

Because each turn appends to the end, the earlier prefix is unchanged and comes from the cache. Only the new exchange is processed at full price.

{% include cc-context-growth.html %}

### What it costs

The platform docs give the multipliers relative to the normal input price:

| Operation | Price |
|---|---|
| Normal input | 1x |
| Cache write, 5-minute lifetime | 1.25x |
| Cache write, 1-hour lifetime | 2x |
| Cache read | 0.1x. Lower on newer models: 0.05x on Opus 5.5 and Sonnet 5.5, 0.025x on Fable 5.1 and Mythos 5.1 |

Writing to the cache costs a little more than normal input once. Reading from it costs a tenth or less, every time after that.

### How long it lasts

The cache lifetime is 5 minutes by default, and each use refreshes it for free. Claude Code gives the main conversation a 1-hour lifetime on a Claude subscription within plan usage, and 5 minutes on an API key, usage credits, or a cloud provider. You can set it with `promptCacheTtl` in settings or `CLAUDE_CODE_PROMPT_CACHE_TTL` (`5m` or `1h`).

This is the answer to "will it be cheaper when I come back?" If you come back within the lifetime, yes. If you come back tomorrow, the first request rebuilds the cache.

### What breaks it

The docs list actions that invalidate the cache mid-session: switching models with `/model`, changing the effort level on most models, toggling fast mode, connecting or removing an MCP server when its tools are loaded upfront, compaction, and upgrading Claude Code. After any of these, the next request pays to rebuild the prefix.

Editing CLAUDE.md during a session does not invalidate the cache, but the edit also does not apply until you `/clear`, `/compact`, or restart.

The cache is effectively scoped to one machine and directory, because the system prompt embeds the working directory and memory paths. Two sessions in the same directory started one after another share a prefix only when the git status snapshot taken at startup matches.

### My own numbers

I summed the usage blocks across the transcript of the session that wrote this post. It spanned 1,593 model replies.

| Measure | Tokens | Share of prompt tokens |
|---|---|---|
| Uncached input | 4,162 | 0.0% |
| Written to cache | 19,927,225 | 3.3% |
| Read from cache | 588,975,357 | 96.7% |
| Output | 1,361,765 | not a prompt token |

Two individual requests show the pattern. An early request: 2 uncached tokens, 25,506 written, 30,989 read. Request number 400: 2 uncached, 346 written, 225,081 read. The prompt had grown to a quarter of a million tokens, and almost all of it was a cheap read.

Using the standard multipliers (write 1.25x, read 0.1x), the prompt side of this session cost about 86% less than it would have without caching. On models with the 0.05x or 0.025x read price, the saving is larger. This is the single biggest reason long sessions are affordable, and it is also why anything that breaks the cache in a long session is expensive.

### How to check your own cache

`/usage` shows a "Prompt cache (main)" line with the share of input tokens served from the cache, the misses, and whether the cache is warm or cold (this line needs Claude Code 2.1.251 or later). A custom status line can show `cache_read_input_tokens` and `cache_creation_input_tokens` live.

## Part 5: CLAUDE.md and memory

CLAUDE.md files are instructions and project knowledge that Claude Code loads into the request. They are the one form of persistence that is cheap, because they are small and stable, and the cache treats them as part of the fixed prefix.

### What loads, and when

| File | Loads |
|---|---|
| Managed policy CLAUDE.md (set by an organisation) | At launch |
| `~/.claude/CLAUDE.md` (your personal file) | At launch |
| `./CLAUDE.md` or `./.claude/CLAUDE.md` in the working directory and every directory above it | At launch, concatenated from the root down |
| `./CLAUDE.local.md` (personal, keep out of git) | At launch |
| `.claude/rules/*.md` without a `paths` field | At launch, same priority as `.claude/CLAUDE.md` |
| `.claude/rules/*.md` with a `paths` field, and CLAUDE.md in subdirectories | On demand, when Claude touches a matching file |
| Auto memory: `~/.claude/projects/<project>/memory/MEMORY.md` | The first 200 lines or 25 KB, whichever comes first, at the start of every conversation |
| Skills | Descriptions at start; the full body only when used |

If no CLAUDE.md exists above the working directory, Claude Code reads `AGENTS.md` instead.

### What it costs

The docs are direct about this: CLAUDE.md is loaded into context at session start, and those tokens are present even when you are doing unrelated work. The guidance is to keep each file under 200 lines, and to ask of every line, "would removing this cause Claude to make mistakes?" If not, cut it. Imports with `@path` do not reduce the cost, because imported files load with the file that imports them. Knowledge that is only relevant sometimes belongs in a skill or a path-scoped rule, which load on demand.

`/memory` opens these files for editing, and `/init` generates a starter CLAUDE.md.

## Part 6: Do MCP servers save tokens?

An MCP server gives Claude extra tools: a database query, a code graph, a ticket system. Three things about it cost tokens, and one thing about it can save them.

### Cost 1: tool definitions

Every tool has a name and a description that the model must see to use it. In older versions, all of them loaded into every request. Claude Code now uses tool search by default on supported models: at session start only the tool names and the server's instructions load, and the model fetches a tool's full definition when it needs it, through a built-in `ToolSearch` tool.

You can tune this with `ENABLE_TOOL_SEARCH`: unset defers all MCP tools; `auto` loads them upfront while their total stays under 10% of the context window and switches to deferral above that; `auto:5` sets a different percentage; `false` loads everything upfront. A server can be pinned upfront with `alwaysLoad: true` in its config. `/context` labels each MCP tool as deferred or loaded on demand.

### Cost 2: tool output

Whatever a tool returns enters the conversation and stays there. Claude Code warns when any MCP tool output exceeds 10,000 tokens, and caps output at 25,000 tokens by default, adjustable with `MAX_MCP_OUTPUT_TOKENS`. Successful text results over 50,000 characters are written to a file instead of being placed in context.

### Cost 3: cache invalidation

Adding or removing a server whose tools are loaded upfront changes layer 1 of the cache, so the next request rebuilds the prefix. Do that at the start of a session, not in the middle of a long one.

### The saving

A tool saves tokens when its answer replaces something more expensive, usually reading files. The code-graph-rag post on this blog is the clearest example: asking the graph "who calls this function" returns a short list, where the alternative is grepping and reading several files into context. The same logic applies to any tool: a precise answer of a few hundred tokens beats a raw dump of a few thousand.

So the honest answer is that MCP servers are neutral. A focused tool with small outputs saves tokens. A chatty server with dozens of tools and large outputs costs them. The docs' own advice is to prefer CLI tools over MCP servers where a CLI exists, and to disable servers you are not using with `/mcp`. `/usage` can attribute recent usage to individual servers, which tells you which ones earn their keep.

## Part 7: Subagents

A subagent is a separate conversation that Claude Code starts to do a job and report back. Each subagent runs in its own context window, with its own system prompt and tool access. It does not see your conversation or the files you already read. When it finishes, only its summary returns to your conversation.

This is the main way to keep noisy work out of your context: run the test suite in a subagent and get back only the failures, or have one investigate a bug and return the cause. The noise stays in the subagent's window and is discarded.

It is not free. A subagent sends its own requests, which count toward the same usage limits as your main conversation, and the docs warn that each subagent spends tokens of its own while it runs. Two settings help: route simple subagents to a cheaper model with `model: haiku` in their definition, and set `omitClaudeMd: true` to start them without your CLAUDE.md when they do not need it. A forked subagent (`fork`) is the exception: it inherits your full conversation, which is useful when it needs the context and costly when it does not.

## Part 8: Thinking and effort

Extended thinking is the model reasoning before it answers. Those tokens are billed as output tokens, and the default budget can be tens of thousands of tokens per request depending on the model. Thinking cannot be turned off on Opus 5.5, Sonnet 5.5, Haiku 5.5, or Fable, but it can be lowered with `/effort`, in `/config`, or with `MAX_THINKING_TOKENS` on models that use a fixed budget. For routine edits, a lower effort level is often enough and noticeably cheaper.

## Part 9: Seeing where the tokens go

- **`/usage`** (`/cost` is an alias) shows, for the session: total cost, API time, wall time, code changes, and a breakdown by model of input, output, cache read, cache write, and dollars. The dollar figure is computed locally at list price and is an estimate; the Console usage page is authoritative. Totals reset on `/clear`.
- **`/context`** shows what is in the window right now, including CLAUDE.md, memory, and MCP tools.
- **A custom status line** can show live token counts, including cache reads and writes, and the percentage of the window used.
- **The transcript file** has the exact usage of every request, if you want to analyse a session after the fact, with the caveat that its format is internal.

## Part 10: Tips

These are the practices that follow from everything above, with the reason for each.

1. **`/clear` between unrelated tasks.** The previous task's files and outputs are still in every request until you do. The docs say to use it frequently.
2. **`/compact` with focus instructions when you want to continue.** `/compact focus on the payment refactor` keeps what matters and drops the rest. Compacting resets the cache, so do it at a natural break, not mid-investigation.
3. **Use `/btw` for side questions.** The answer never enters the conversation history, so a quick "what does this flag mean?" does not follow you around for the rest of the session.
4. **Keep sessions on one topic.** A long session is cheap per request thanks to the cache, but every request still carries the whole history. Ten focused sessions cost less than one sprawling one.
5. **Do not switch models or effort levels mid-session without a reason.** Each switch invalidates the cache and the next request rebuilds the prefix at the premium price.
6. **Connect MCP servers before you start, not during.** Same reason: adding one changes the tool definitions at the front of the cache.
7. **Keep CLAUDE.md under 200 lines, and cut anything that does not prevent a mistake.** It is loaded into every request of every session.
8. **Move occasional knowledge into skills or path-scoped rules.** They load only when relevant. Imports do not help; they load with the file that imports them.
9. **Let auto memory do its job, and prune MEMORY.md occasionally.** Only its first 200 lines or 25 KB load, so stale entries push out useful ones.
10. **Scope what Claude reads.** Point it at the function or the file section, not the directory. Ask for `grep` results before full files. The context-heavy tools `/context` flags are usually file reads and command outputs.
11. **Pre-filter command output.** `BASH_MAX_OUTPUT_LENGTH` caps shell output (30,000 characters by default). The docs also show PreToolUse hooks that filter output before it reaches context.
12. **Use subagents for noisy work, and put them on Haiku when the job is simple.** Test runs, log searches, and broad code surveys belong in a subagent that returns a summary.
13. **Prefer a CLI to an MCP server when both exist, and disable unused servers.** Fewer tool definitions, smaller outputs, and a cache that is not disturbed.
14. **Lower the effort level for routine work.** Thinking tokens are output tokens, and output is the most expensive kind.
15. **Resume within the cache lifetime when you can.** Coming back to a session an hour later on a subscription, or five minutes later on an API key, keeps the history as cheap reads. Coming back the next day rebuilds it.
16. **Check `/usage` once in a while.** If the cache share is low or one MCP server dominates, you have found the next thing to fix.

## A suggested workflow

The tips above are easier to apply as a routine. This is the one I use, built around the one decision that matters most: after each task, is the next task related to this one?

{% include cc-workflow.html %}

**Set up once per project.** Write a short CLAUDE.md, move occasional knowledge into skills or path-scoped rules, keep only the MCP servers you need, cap shell and MCP output, and add a status line that shows context and cache usage. This is where most of the per-session fixed cost is decided.

**Start a session deliberately.** Open in the right directory, connect MCP servers before the first prompt, choose the model and effort level once, and begin with a prompt that names the files or functions involved. A specific first prompt avoids an exploration phase that fills the context with file reads.

**Work on one task at a time.** Ask for narrow reads, send noisy work to a subagent, use `/btw` for side questions, and if you have corrected Claude twice on the same point, `/clear` and write a better prompt rather than arguing in a long context.

**Decide after each task.** If the next task is related, keep the session and `/compact` with a focus at a natural break. If it is not, `/clear`. The history drops to zero, and the fixed prefix (system prompt, tools, CLAUDE.md) is small and, when unchanged and still within the cache lifetime, is served from the cache.

**End with intent.** If you will be back within the cache lifetime, resume. If not, start fresh next time and let CLAUDE.md and memory carry the knowledge. A long session resumed the next day re-sends its entire history.

### Many small, unrelated tasks

This is the case where the default habit, one long conversation, costs the most. Ten unrelated tasks in one session means the tenth task's requests carry the other nine tasks' files and outputs, and pay for them as cache reads on every request. The fix is to keep each task's context separate. These are the tools that do that, all built into Claude Code:

| Tool | Use it for | Why it saves tokens |
|---|---|---|
| `/clear` (also `/reset`, `/new`) | Moving to the next unrelated task in the same session | The conversation is emptied. Only the fixed prefix remains, and it is small |
| `/btw` | A quick question in the middle of a task | The answer is shown to you but never enters the history, so later requests do not carry it |
| A subagent (the Agent tool, or a custom one with `model: haiku`) | A self-contained job: run the tests, find where a setting is read, check a dependency | It runs in its own context window and returns only a summary. Add `omitClaudeMd: true` to a custom subagent that does not need your project instructions |
| `claude -p "..."` (print mode) | One scripted task from the shell, or a batch of them in a loop | Each call is a standalone request with no session to carry. Good for repetitive small jobs you can describe in one line |
| A skill or custom slash command | A small task you repeat often (format a changelog, write a migration) | The instructions live in the skill and load only when it runs, instead of being re-typed into every conversation |
| `claude --model haiku` for a session of trivial tasks | Renames, small fixes, questions about syntax | Cheaper per token, and starting the session on it avoids a mid-session switch that would rebuild the cache |

Two things to avoid. Do not use `/compact` as a substitute for `/clear` between unrelated tasks: the summary still carries the old task, and compaction itself is a request that produces a summary. And do not switch directories for every small task when they belong to the same project, because the cache prefix is scoped to the directory and each switch starts cold.

## Summary

Claude Code is a loop around a stateless model: every request carries the whole conversation, and a turn with tool calls is several requests. The context window is large but fills with file contents and outputs, and compaction trades detail for room. Sessions are saved as JSONL transcripts that cost nothing to keep and nothing to lose, but resuming one re-sends everything. The prompt cache is what makes long sessions affordable, with reads at a tenth of the price or less, as long as nothing disturbs the prefix. CLAUDE.md and memory are the cheap, persistent knowledge; MCP servers and subagents are neutral tools that save or cost tokens depending on how they are used. The practical rules are short: clear between tasks, compact with intent, keep the prefix stable, keep memory small, and keep the noise out of context.
