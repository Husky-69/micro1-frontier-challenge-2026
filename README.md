# Code Quality Agent: Is This Repository Actually Good?

**micro1 Agentic Workflows Hackathon — August 2026**

## The User & Their Bottleneck

Engineering teams, investors, and open-source maintainers regularly need to judge the quality of a repository they didn't build — before adopting it, contributing to it, or acquiring it. A README and a working demo tell you almost nothing about the code underneath: test coverage, cyclomatic complexity, dependency health, and technical debt are invisible unless someone manually opens the codebase and digs. That manual audit typically takes hours, and different reviewers looking at the same signals can reach different conclusions, so decisions end up resting on incomplete or inconsistent judgment.

## Why This Matters

A bad codebase hides real cost: technical debt that slows every future change, dependency risk that surfaces later as security or maintenance problems, and negotiating positions (in an acquisition or contribution decision) based on guesswork rather than evidence. A system that turns "does this look reasonable?" into a repeatable, evidence-backed score in seconds — rather than hours — changes how confidently that decision gets made.

## Baseline Solution

A naive script (`src/baseline/naive_solution.py`) that scores a repository purely on volume: file count, total lines of code, and whether a `README.md` exists. It has no way to tell a large, well-tested library from a large, untested one — it just rewards size.

## Advanced Agentic Solution

A LangGraph agent (`src/agent/graph.py`), running on Groq's `qwen/qwen3.8-27b`, that must gather real evidence before scoring a repository:

- **`analyze_code_complexity`** — average cyclomatic complexity via `radon`, sampled across the repo's Python files
- **`check_test_coverage`** — whether a `tests/`/`test/` directory exists and how many test files it contains
- **`check_dependency_health`** — whether dependencies are declared via `requirements.txt` or `pyproject.toml`
- **`execute_consequential_action`** — a sandboxed tool for anything beyond read-only analysis, gated behind a human-in-the-loop approval prompt

The agent is instructed not to guess: it must call the tools, synthesize their output, and justify its final 1–10 score against the actual evidence gathered.

## Measured Improvement

| Repository | Baseline Score | Agent Score | Ground Truth |
|---|---|---|---|
| `requests` (high quality) | 8/10 | **9/10** | High |
| `black` (medium quality) | **10/10** | 7/10 | Medium |
| `public-apis` (low quality) | 5/10 | 3/10 | Low |

**Baseline ranking:** black > requests > public-apis — the top two are swapped.
**Agent ranking:** requests > black > public-apis — matches ground truth exactly.

The baseline conflates codebase size with quality: `black`'s much larger file/LOC count earns it a perfect score despite a thin test-to-source ratio (15 test files for 345 source files). The agent's tool-based evidence — complexity, real test presence, dependency management — produces a ranking that matches expert judgment exactly. Measured as pairwise ranking accuracy across all 3 repositories, the baseline gets 2 of 3 orderings right (67%); the agent gets 3 of 3 (100%).

## Improvement Changelog

See [CHANGELOG.md](./CHANGELOG.md)

## Main Failure Mode & Hot Take

**Failure mode:** The agent's reasoning was correct from the start — it consistently chose to call `analyze_code_complexity`, `check_test_coverage`, and `check_dependency_health` by name. But the graph's tool-execution node was hardcoded to route every tool call through a single function (`execute_consequential_action`) regardless of which tool the model actually requested, and returned a generic `"Success"` message instead of real data. The agent had no way to know its tools weren't actually running — it just kept retrying, assuming a transient failure.

**Hot take:** An agent can reason correctly about *which* tool to call and still produce worthless output if the execution layer beneath it silently discards that reasoning. Trajectory logging caught this immediately once we looked at it — but if we'd only looked at the final score (a plausible-sounding number) instead of the underlying tool outputs, this bug would have shipped invisibly. Verification needs to check that tools *actually ran*, not just that the agent *called* them.

**Known issue (not yet fixed):** the low-quality repo run occasionally shows the human-approval checkpoint firing twice with an identical prompt. It doesn't affect the final score, but it's a loose end in the graph's retry logic worth investigating with more time.

## Reproduction

See [reproduction_guide.md](./reproduction_guide.md)
