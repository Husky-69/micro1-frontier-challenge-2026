# Code Quality Agent: Is This Repository Actually Good?

**micro1 Agentic Workflows Hackathon — August 2026**

## The User & Their Bottleneck

Picture a team about to adopt an open-source library, or an investor about to buy a piece of software. Neither one wrote the code. Both need to know: is it actually good?

Right now, that's guesswork. A README looks nice. A demo runs smoothly. But neither tells you what's underneath, is the code well-tested? Is it a tangled mess or a clean one? Are the dependencies safe and current? Is the project actually maintained, or one departed contributor away from going stale? To find out, someone has to open the codebase and dig by hand. That takes hours. And two people digging through the same repo can walk away with two different opinions.

## Why This Matters

Bad code doesn't announce itself. It hides. Then, months later, it shows up as a security hole, a dependency nobody dares update, or a "simple" feature that takes three times longer than it should. If you're negotiating a price to acquire that code, or deciding whether to build your product on top of it, you're negotiating blind.

What this project does: it turns "does this codebase look okay?" into a real, evidence-backed score, in seconds, not hours. Same question, but now with proof behind the answer.

## Baseline Solution

A naive script (`src/baseline/naive_solution.py`) that scores a repository purely on volume: file count, total lines of code, and whether a `README.md` exists. It has no way to tell a large, well-tested library from a large, untested one, it just rewards size.

## Advanced Agentic Solution

A LangGraph agent (`src/agent/graph.py`), running on Groq's `qwen/qwen3.8-27b`, that must gather real evidence before scoring a repository:

- **`analyze_code_complexity`** — average cyclomatic complexity via `radon`, sampled across the repo's Python files
- **`check_test_coverage`** — whether a `tests/`/`test/` directory exists and how many test files it contains
- **`check_dependency_health`** — whether dependencies are declared via `requirements.txt` or `pyproject.toml`
- **`check_maintenance_health`** — contributor concentration ("bus factor") and days since the last commit, using git history. Tests, complexity, and dependencies can all look fine on a project that's one departed maintainer away from going unmaintained.
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

The baseline conflates codebase size with quality: `black`'s much larger file/LOC count earns it a perfect score despite a thin test-to-source ratio (15 test files for 345 source files). The agent's tool-based evidence — complexity, real test presence, dependency management, produces a ranking that matches expert judgment exactly. Measured as pairwise ranking accuracy across all 3 repositories, the baseline gets 2 of 3 orderings right (67%); the agent gets 3 of 3 (100%).

**Maintenance Health (contributor concentration + staleness):** a 4th signal tests/complexity/dependencies, added to catch bus-factor risk the other three checks can't see on their own. On these 3 test repos it didn't flip any final scores — `requests`, `black`, and `public-apis` are all large, actively-maintained projects with well-distributed contributor bases, but it gives the agent's assessment a dimension none of the other checks cover, and would matter on a smaller or single-maintainer repository.

## Improvement Changelog

See [CHANGELOG.md](./CHANGELOG.md)

## Main Failure Mode & Hot Take

**Failure mode:** The agent's reasoning was correct from the start, it consistently chose to call `analyze_code_complexity`, `check_test_coverage`, and `check_dependency_health` by name. But the graph's tool-execution node was hardcoded to route every tool call through a single function (`execute_consequential_action`) regardless of which tool the model actually requested, and returned a generic `"Success"` message instead of real data. The agent had no way to know its tools weren't actually running it just kept retrying, assuming a transient failure.

**Hot take:** An agent can reason correctly about *which* tool to call and still produce worthless output if the execution layer beneath it silently discards that reasoning. Trajectory logging caught this immediately once I looked at it, but if I'd only looked at the final score (a plausible-sounding number) instead of the underlying tool outputs, this bug would have shipped invisibly. Verification needs to check that tools *actually ran*, not just that the agent *called* them.

**Known issue (not yet fixed):** the low-quality repo run occasionally shows the human-approval checkpoint firing twice with an identical prompt. It doesn't affect the final score, but it's a loose end in the graph's retry logic worth investigating.

## Reproduction

See [reproduction_guide.md](./reproduction_guide.md)

Project by Shallom Githui
