# Google ADK Interview Agents

Three small agents built with Google's **Agent Development Kit (ADK)** for Python.
Each one is a realistic business use case for a cloud services company.

| Agent | Pattern | What it shows |
|---|---|---|
| `support_triage_agent` | 1 agent + 3 tools | Tools are plain Python functions; the LLM reads docstrings to decide when to call them; tools chain (classify -> plan -> priority) |
| `cloud_ops_agent` | 1 agent + infra tools | Mock inventory standing in for real Azure/AWS APIs; a tool that *changes* state (restart); guardrails in the instruction |
| `customer_service_hub` | multi-agent | Root orchestrator delegates to `billing_agent` and `tech_support_agent` via `sub_agents`; each specialist has its own tools |

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env   # then paste your Gemini API key from https://aistudio.google.com/apikey
```

## Run

```bash
adk web        # from this folder - pick an agent in the dropdown, chat in the browser
# or
adk run support_triage_agent
```

## How an ADK agent works (the 30-second version)

1. You define an `Agent` with a `name`, `model` (Gemini), an `instruction` (its job description) and `tools`.
2. A tool is a normal Python function. ADK reads its **name, docstring and type hints** and shows that schema to the model.
3. On each user message the model decides: answer directly, or call a tool. Tool results go back to the model, which writes the final reply.
4. `adk web` runs a local dev UI where you can chat and inspect every tool call.
5. Multi-agent: put agents inside another agent's `sub_agents` list; the root agent's `description` fields tell it who does what, and it delegates.
