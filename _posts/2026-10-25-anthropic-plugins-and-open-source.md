---
title: "Anthropic's open-source plugins and tools, updated in week 43 of 2026"
date: 2026-10-25 09:10:00 +0700
categories: [ai]
lang: en
---

Several Anthropic repositories for plugins and open-source tools were updated this week. These are the ones that matter for builders, based on each repo's README on GitHub. The dates below are the latest commit dates, not the original release dates.

## Knowledge work plugins for Claude Cowork

The [knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins) repo contains plugins that turn Claude into a specialist for a job function. Anthropic open-sourced 11 of them, covering productivity, sales, customer support, product management, marketing, legal, finance, data, enterprise search, bio research and plugin management. Each plugin bundles skills, connectors, slash commands and sub-agents. You can install them in Cowork, or in Claude Code through the marketplace.

## Official Claude Code plugin directory

The [claude-plugins-official](https://github.com/anthropics/claude-plugins-official) repo is a curated directory of plugins for Claude Code. Install one with `/plugin install {plugin-name}@claude-plugins-official`, or browse it under `/plugin > Discover`. Anthropic says third-party plugins must pass quality and security review before they are listed, and it warns users to check a plugin before installing it.

## Community marketplace

The [claude-plugins-community](https://github.com/anthropics/claude-plugins-community) repo is a read-only mirror of a community plugin marketplace for Cowork and Claude Code. Developers submit plugins through a separate form rather than through this repo.

## Claude for Legal

The [claude-for-legal](https://github.com/anthropics/claude-for-legal) repo is a suite of plugins for legal work, including in-house commercial, privacy, employment and litigation. It includes named agents such as a Vendor Agreement Reviewer and an NDA Triager. The README says every output is a draft for attorney review, not legal advice.

## Sandbox runtime

The [sandbox-runtime](https://github.com/anthropics/sandbox-runtime) repo, called `srt`, is a beta research preview. It enforces filesystem and network limits on processes at the OS level, without a container. It can sandbox agents, local MCP servers and shell commands. Install it with `npm install -g @anthropic-ai/sandbox-runtime`. The README says APIs and configuration formats may change.

## What it means for you

If you build agent workflows, the plugin repos are a working reference for connectors, skills and sub-agents. The sandbox runtime matters if you run agents on machines that hold real data.
