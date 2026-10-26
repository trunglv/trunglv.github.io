---
title: "Indexing source code with code-graph-rag: MCP in Claude Code, architecture diagrams, and token savings"
date: 2026-10-26 08:00:00 +0700
categories: [ai]
lang: en
---

This is a working note for myself. The goal is to index a codebase with [code-graph-rag](https://github.com/vitali87/code-graph-rag), use it from Claude Code through MCP, use the graph to draw diagrams that show the quality and architecture of the code, and answer one side question: does it save tokens, and if so, what does that look like?

Everything here is based on the project's own documentation at the time of writing (October 2026). The project moves fast, so check the docs before relying on a command.

{% include toc.html %}

## At a glance

| I want to | Use | Notes |
|---|---|---|
| Index a repository | `cgr start --repo-path . --update-graph --capture io` the first time; the same command again, or the MCP tool `update_repository`, to refresh | The graph is stored in a local SQLite file by default |
| Use the graph from Claude Code | `claude mcp add ... code-graph-rag mcp-server` | Most tools need no LLM at all |
| Navigate code precisely | MCP tools `resolve`, `definition`, `callers`, `callees`, `importers`, `tests_reaching` | Fixed graph queries: same graph, same answer |
| Give Claude a small, focused context | MCP tool `context` with a token budget | The main token saver |
| Assess architecture | Ask Claude to draw diagrams from `importers` and `callers` | There is no built-in diagram renderer |
| Find quality problems | `cgr dead-code`, `cgr duplicates`, `cgr check` | `cgr check` reports new import cycles against a git ref |

## What code-graph-rag is, and how it differs from text RAG

The RAG guide on this blog splits documents into chunks and finds them by meaning. Code needs something different. A function is defined in one file, called from ten others, and tested from three more. Splitting files into text chunks loses those links.

code-graph-rag parses the code with Tree-sitter (and compiler front ends for some languages) and stores its structure as a knowledge graph:

- **Nodes:** folders, files, modules, classes, functions, methods.
- **Relationships:** which function calls which, which module imports which, which class inherits from which. From these, the tool derives answers such as which tests reach a function.

Questions about code are mostly questions about these links, so the graph answers them directly instead of by similarity. Semantic search by meaning is still available as an option, for questions like "where do we validate addresses?".

It supports Python, TypeScript and JavaScript, Go, Java, PHP, C and C++, C#, Rust, and several others. The graph lives in an embedded SQLite file, so there is no database server or Docker to run. Memgraph and Neo4j are optional back ends for larger setups.

## Part 1: Use it in Claude Code through MCP

### Install

The tool needs Python 3.12 or newer and `ripgrep`. Install it once, with the language grammars, structural search, and semantic search extras:

```bash
uv tool install "code-graph-rag[treesitter-full,ast-grep,semantic]"
```

### Index the repository

From the root of the project:

```bash
cgr start --repo-path . --update-graph --capture io
```

The first run parses every file. Later runs of the same command update the graph incrementally. `--capture io` adds data-flow information to the index; it must match the `CGR_CAPTURE=io` setting of the MCP server below, otherwise the server will ask you to index again. Avoid the `--clean` option unless you mean it: it wipes every project in the shared graph, not just the current one, after asking for confirmation.

### Connect it to Claude Code

Register the MCP server for the project. This version points the tools that need an LLM at a local Ollama model, so code does not leave the machine. It assumes Ollama is installed and running, with the model already pulled (`ollama pull qwen2.5-coder`):

```bash
claude mcp add --transport stdio code-graph-rag \
  --env TARGET_REPO_PATH=/absolute/path/to/project \
  --env CGR_CAPTURE=io \
  --env CYPHER_PROVIDER=ollama \
  --env CYPHER_MODEL=qwen2.5-coder \
  -- code-graph-rag mcp-server
```

Then run `claude mcp list` and confirm the server shows as connected.

Three things are worth knowing about this setup:

- **Most tools need no LLM.** Indexing and the precise lookup tools run fixed graph queries. Only `query_code_graph` (plain-English questions about the graph) needs the model set with `CYPHER_*`, and `ask_agent` needs its own model.
- **`CGR_CAPTURE=io` adds data-flow information,** which the `flow_verdict`, `explain_traceback`, and `rank_root_causes` tools use. It must match the `--capture io` used when indexing. If you add or change it later, restart the server and index again.
- **One server per repository.** For several repositories, add one named server for each, or serve a whole workspace from one server.

### The tools I actually use

| Tool | What it answers | When to use it |
|---|---|---|
| `resolve` | Which definition does this name or `file:line` refer to? | Before any other lookup, to get the exact qualified name |
| `definition` | The source, file, and lines of one definition | Instead of opening the whole file |
| `callers` / `callees` | Who calls this, and what does it call (with `depth` for more levels) | Before changing a function's signature or behaviour |
| `importers` | Which modules import this module | To see who depends on a module, and to draw dependency diagrams |
| `implementors` / `overrides` | Subclasses, implementations, and overridden methods | Before changing a base class or interface |
| `tests_reaching` | Which tests reach this function | To know which tests to run after an edit |
| `context` | A small, ranked bundle of everything relevant, within a token budget | First step for any task on a function |
| `find_duplicate_code` | Copy-pasted and near-duplicate functions | Before writing a new helper |
| `query_code_graph` | Open questions in plain English | When you do not know the exact name |

The lookup tools `callers`, `callees`, `implementors`, `overrides`, `importers`, and `tests_reaching` refuse, with close matches, when the name is not in the graph. For them, an empty list means "the name exists, and nothing matches", which you can trust. `resolve` is the exception: it returns an empty list when no name matches, and `definition` answers `found: false`.

### Keep the graph in sync

The graph is only as good as its last update. After editing, the `reingest` tool updates just the changed files and their dependents: typically well under a second, a few seconds for a file that many others import. For a large change, run `update_repository`, or keep `cgr watch` running while you work.

The tools that write code through the server (`write_file`, `surgical_replace_code`, `structural_replace`) re-index the touched files automatically and append a structural report: dangling callers, signature changes, new duplicates, new import cycles, and the tests that reach the edited code. That report is a useful check before the next edit. If Claude edits files with its own Edit tool instead, the server does not see the change: ask it to call `reingest` for the touched files, or keep `cgr watch` running.

Be careful with two tools: `index_repository` clears the project's existing data before rebuilding it, and `wipe_database` removes every project. Use `update_repository` for normal updates.

## Part 2: Draw diagrams to assess quality and architecture

### What the tool does and does not do

code-graph-rag has no built-in diagram renderer. What it provides is the data that diagrams need: imports between modules, calls between functions, and inheritance between classes. There are two practical ways to turn that into a picture:

1. **Ask Claude Code.** Claude calls `importers` and `callers` through MCP, then writes a Mermaid or Graphviz diagram from the results. This is the fastest way for a one-off review.
2. **Export and script it.** `cgr export -o graph.json --project <name>` writes the whole graph as JSON. A short script can turn it into a diagram, or into numbers you can track over time.

### What a useful diagram looks like

{% include cgr-architecture-diagram.html %}

A module dependency diagram is the most useful single picture. Read it for four things:

| What to look for | What it means | How the graph shows it |
|---|---|---|
| Arrows pointing up, against the layers | A lower layer depends on a higher one, so the layers are not real | `importers` and `callers` between modules in different layers |
| Cycles | Two modules cannot change or be tested on their own | `cgr check` reports new import cycles against a git ref |
| Hotspots with many incoming arrows | A change there ripples everywhere; a candidate to split or stabilise | Count `importers` per module |
| Modules nobody imports | Dead code, or an entry point you forgot | `cgr dead-code` |

### Other quality checks the graph gives you

- **`cgr dead-code`** lists code that appears unreachable from known entry points. Treat it as a review list, not a list of things to delete, since plugins and reflection can hide real callers.
- **`cgr duplicates`** finds copy-pasted functions, including renamed and lightly edited copies. Use `--fail-on-found` to stop a CI run when new duplicates appear.
- **`cgr check`** compares the working tree against a git ref and reports dangling callers, wrong argument counts, new duplicates, new import cycles, and the tests that reach the changed code. It works well as a pre-merge check.
- **`endpoints` and `remote_dependencies`** (MCP tools) list the routes a service exposes and the network calls it makes. With several services indexed, this becomes a service dependency map.

### Prompts I use in Claude Code

> Using the code-graph-rag tools, list the top-level modules under src/ and, with importers, find every import between them. Draw a Mermaid diagram with one node per module, mark cycles in red, and mark imports that go from a lower layer to a higher one. The intended layers, top to bottom, are: api, services, domain, repository.

> For the function OrderService.create_order, use callers with depth 2 and tests_reaching. Draw a call diagram, and list the tests I must run if I change its signature.

> Run find_duplicate_code with the default threshold and summarise the three largest clone groups, with file and line for each copy.

Asking for the intended layers explicitly matters. The graph shows what the code does; only you know what the architecture is supposed to be, and the diagram is most useful when it shows the difference.

## Part 3: Does it save tokens?

### Short answer

Yes, for the most common work in a codebase: finding where something is defined, who uses it, and what a change will affect. It saves tokens by replacing "read whole files to find the answer" with "ask the graph for the answer".

### How to picture it

{% include cgr-token-diagram.html %}

Without the graph, Claude finds things the way a person new to the code would: search for the name, open the files it finds, read them, and repeat. Most of what it reads is unrelated to the question, but it all enters the context and is paid for.

With the graph, the same question becomes a few small, structured answers:

- `callers` returns a list of call sites (file, line, argument count), not the files around them.
- `tests_reaching` returns the exact tests, so Claude does not read the test folder to guess.
- `context` returns the function's source, the lines that call it, the signatures of what it calls, its types, and the tests that reach it, ranked by how close they are in the graph and trimmed to a token budget you choose. Each piece says why it was included.

A good mental model is a map versus walking every street. The graph is the map: Claude looks up the route, and only walks the streets it actually needs to change.

### When it does not save tokens

- **Tool definitions cost tokens.** The server exposes more than 30 tools, and some have long descriptions. Depending on how your client loads tool definitions, part or all of that text takes up context in every session; `/context` in Claude Code shows the actual amount. On a small repository, or for a short session, that fixed cost can be larger than what the tools save.
- **A stale graph costs more.** If the graph is out of date, Claude gets a wrong answer, then reads the files anyway. Keep it in sync with `reingest` or `cgr watch`.
- **Plain-English questions use another model.** `query_code_graph` and `ask_agent` call the configured LLM. What that model consumes does not count against Claude's context, but it is not free unless the model runs locally. The results it returns enter Claude's context like any other tool result.
- **Editing still needs the real file.** The graph helps you find what to edit; making the edit still means reading that part of the file.

### How to measure it on your own code

Pick a task you do often, such as "rename this function's parameter and update every caller". Run it twice in Claude Code from a fresh session: once with the MCP server disabled, once with it enabled and the prompt asking Claude to use the graph tools first. After each run, check the session's usage with `/cost`, and look at `/context` to see how much of the window the tool definitions take. Compare the totals and the number of files Claude opened. A few runs on real tasks tell you more than any general claim.

## Summary

code-graph-rag turns a codebase into a graph of definitions and relationships. Through MCP, Claude Code can ask that graph precise questions instead of reading files, which makes its answers more reliable and usually its sessions cheaper. The same graph is the raw material for architecture diagrams and quality checks, as long as you bring the intended architecture to compare against. Keep the graph in sync, prefer the deterministic tools and `context`, and measure the savings on your own tasks rather than assuming them.
