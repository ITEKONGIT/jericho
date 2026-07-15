# AI Inference & Automation
This module handles localized LLM operations, ensuring offensive security queries, payload generation, and log analysis remain entirely on-premise without leaking data to third-party APIs.

## Architecture
- **Inference Server (Host):** Dell Inspiron 16+ running the core models (e.g., Ollama, OpenCode).
- **Controller/Agent:** Parrot OS environment executing the prompts and handling the returned context.

## Core Components
- **scripts/parrot_agent.py**: A CLI bridge to send context from the Parrot OS terminal directly to the local inference server's API and parse the response back into the active shell.

## The Arsenal (Related Research)
- [Link to upcoming blog post on cocofelon.lol/blog/arsenal-local-ai]
