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

Use `git clone` (not a zip download) for all three — the agent's `check_maintenance_health` tool reads each repo's `.git` history to check contributor concentration and staleness, and needs that history intact. A normal `git clone` includes it by default.

## 3. Run the Baseline

```bash
python -m src.baseline.naive_solution
```

**Expected output:** a naive score (out of 10) for each of the three repos, driven by file count and lines of code, saved to `baseline_results.json`. `black` scores highest despite being the "medium quality" repo, this is the intended baseline flaw.

## 4. Run the Advanced Agentic Solution

Run each repo separately (each run takes roughly 10–30 seconds, mostly Groq API latency; no cost, as Groq's API is free at this usage level):

```bash
python -m src.advanced.agentic_solution test_repos/repo_high_quality run_high_quality
python -m src.advanced.agentic_solution test_repos/repo_medium_quality run_medium_quality
python -m src.advanced.agentic_solution test_repos/repo_low_quality run_low_quality
```

**Expected output:** each run prints an evidence-based quality assessment covering four dimensions: code complexity, test coverage, dependency health, and maintenance health (contributor concentration and days since last commit) — ending in a Quality Score out of 10. Expected scores: `requests` → 9/10, `black` → 7/10, `public-apis` → 3/10.

Note: the `public-apis` run may trigger one or more `[⚠️ HUMAN CHECKPOINT]` prompts: type `yes` to approve and let the agent continue if this happens. This became less frequent once all four analysis tools were available.

## 5. View the Trajectories

```bash
cat trajectories/run_high_quality_trajectory.md
cat trajectories/run_medium_quality_trajectory.md
cat trajectories/run_low_quality_trajectory.md
```

Each file shows the agent's full reasoning trace: which tools it called (including `check_maintenance_health`), what arguments it passed, what each tool returned, and any human-approval checkpoints it hit along the way.

## Tools Used by the Agent

- `analyze_code_complexity` — average cyclomatic complexity via `radon`
- `check_test_coverage` — presence and count of test files
- `check_dependency_health` — presence of `requirements.txt` / `pyproject.toml`
- `check_maintenance_health` — contributor concentration ("bus factor") and days since last commit, via `git log` (requires the repo's `.git` history — see Step 2)
- `execute_consequential_action` — sandboxed tool for anything beyond read-only analysis, gated behind human approval

## Versions

- Python 3.11
- Key dependencies: `langgraph==0.2.60`, `langchain-openai`, `radon`, `pytest==8.3.3` (see `requirements.txt` for full pinned list)
- LLM: `qwen/qwen3.8-27b` via Groq's OpenAI-compatible API
