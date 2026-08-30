# Reproduction Guide

## 1. Environment Setup

```bash
git clone https://github.com/YOUR_USERNAME/micro1-frontier-challenge-2026.git
cd micro1-frontier-challenge-2026
python -m venv venv
source venv/bin/activate        # Linux/Mac
# venv\Scripts\activate         # Windows
pip install -r requirements.txt
```

Requires a **free Groq API key** (used for `qwen/qwen3.8-27b` via Groq's OpenAI-compatible endpoint). Get one at https://console.groq.com/keys, then create a `.env` file in the project root:



## 2. Get the Test Repositories

```bash
mkdir test_repos
cd test_repos
git clone https://github.com/psf/requests.git repo_high_quality
git clone https://github.com/psf/black.git repo_medium_quality
git clone https://github.com/public-apis/public-apis.git repo_low_quality
cd ..
```

## 3. Run the Baseline

```bash
python -m src.baseline.naive_solution
```

**Expected output:** a naive score (out of 10) for each of the three repos, driven by file count and lines of code, saved to `baseline_results.json`. `black` scores highest despite being the "medium quality" repo — this is the intended baseline flaw.

## 4. Run the Advanced Agentic Solution

Run each repo separately (each run takes roughly 10–30 seconds, mostly Groq API latency; no cost, as Groq's API is free at this usage level):

```bash
python -m src.advanced.agentic_solution test_repos/repo_high_quality run_high_quality
python -m src.advanced.agentic_solution test_repos/repo_medium_quality run_medium_quality
python -m src.advanced.agentic_solution test_repos/repo_low_quality run_low_quality
```

**Expected output:** each run prints an evidence-based quality assessment (complexity, test coverage, dependency health) ending in a Quality Score out of 10. Expected scores: `requests` → 9/10, `black` → 7/10, `public-apis` → 3/10.

Note: the `public-apis` run may trigger one or more `[⚠️ HUMAN CHECKPOINT]` prompts — type `yes` to approve and let the agent continue.

## 5. View the Trajectories

```bash
cat trajectories/run_high_quality_trajectory.md
cat trajectories/run_medium_quality_trajectory.md
cat trajectories/run_low_quality_trajectory.md
```

Each file shows the agent's full reasoning trace: which tools it called, what arguments it passed, what each tool returned, and any human-approval checkpoints it hit along the way.

## Versions

- Python 3.11
- Key dependencies: `langgraph==0.2.60`, `langchain-openai`, `radon`, `pytest==8.3.3` (see `requirements.txt` for full pinned list)
- LLM: `qwen/qwen3.8-27b` via Groq's OpenAI-compatible API
