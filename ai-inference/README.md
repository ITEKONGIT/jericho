# AI Inference & Automation
This module handles localized LLM operations, ensuring offensive security queries, payload generation, and log analysis remain entirely on-premise without leaking data to third-party APIs.

## Newcomer ramp

**What this field is.** This isn't an attack module — it's *ops hygiene* for everything else in Jericho. LLM-assisted work (payload drafts, log triage, methodology questions) normally means pasting target context into a third-party API. This module keeps that loop on my own hardware: a local model server on one machine, a CLI bridge (`scripts/parrot_agent.py`) that pipes context from the test workstation's shell and returns the answer.

**Why people miss the point here.** The data-leak risk isn't hypothetical — target hostnames, tokens, and config snippets *are* the context an LLM workflow wants. The miss is treating convenience and authorization as the same conversation: an NDA doesn't extend to a third-party inference provider. If target details would be OK to email to a stranger, paste away; if not, they go through here.

**Read order.** [`scripts/parrot_agent.py`](scripts/parrot_agent.py) is the whole module — read its docstring/argparse, run it against the local server once, done. The Windows binder (`scripts/windows_ollama_bind.ps1`) is only for exposing the Ollama host. **Defer:** everything until you're mid-engagement and about to paste target data somewhere it shouldn't go — that's the moment this module exists for.

## Architecture
- **Inference Server (Host):** Dell Inspiron 16+ running the core models (e.g., Ollama, OpenCode).
- **Controller/Agent:** Parrot OS environment executing the prompts and handling the returned context.

## Core Components
- **scripts/parrot_agent.py**: A CLI bridge to send context from the Parrot OS terminal directly to the local inference server's API and parse the response back into the active shell.

## The Arsenal (Related Research)
- [Link to upcoming blog post on cocofelon.lol/blog/arsenal-local-ai]
