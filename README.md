# debate-research-agent

Multi-agent AI tool that finds credible citations for high school debate research, built for my daughter who chairs her school's debate team.

## The problem

The most time-consuming part of debate prep is finding credible sources. Hours of repetitive searches, manual citation checks, and tab-juggling. Her workflow was the blueprint.

## How it works

Three agents, each with its own prompt file:

1. **Source Finder** finds candidate sources for a debate topic.
2. **Validator** filters out blogs and opinion pieces. Whitelists credible domains (BBC, Brookings, CFR, and similar).
3. **Summarizer** drafts a tight summary of the validated sources.

A human-in-the-loop step sits between the Validator and the Summarizer. The user manually reviews and approves the validated sources before any summarization runs. This catches false positives before they propagate downstream into the most expensive step.

## Tech stack

- Python
- Streamlit for the front-end (`app_secure.py`)
- Claude (via Claude Code) for agent reasoning
- File-based prompting: each agent is a `.md` file with focused prompts, which keeps reasoning consistent across runs and avoids prompt drift
- Orchestration logic in `orchestrator_secure.py`

## Architecture decisions

- **Multi-agent over single prompt.** Each agent has one job and one prompt. Easier to debug, easier to swap in better prompts as I learn.
- **HITL before summarization, not after.** Summarization is the most expensive step. Validating sources first catches errors before they propagate.
- **Domain whitelist over keyword filters.** "Credible" is hard to define abstractly. Easier to maintain a whitelist of known credible domains.

## Run it

Detailed setup and deployment guidance lives in the sub-READMEs:

- [`README_SECURE.md`](README_SECURE.md) for the secure agent implementation
- [`README_MULTI_AGENT.md`](README_MULTI_AGENT.md) for the multi-agent orchestration patterns
- [`README_DEPLOYMENT.md`](README_DEPLOYMENT.md) for deployment
