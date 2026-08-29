# Code Quality Agent: Is this repository actually good?

## The User & Bottleneck
Engineering teams and investors often need to evaluate a code repository before adopting or purchasing it. The bottleneck is that READMEs and demos are misleading; true quality lies in test coverage, code complexity, and dependency health. Manually auditing this takes 10+ hours per repo.

## Why This Matters
A bad codebase introduces massive technical debt. Solving this allows teams to make data-driven decisions in minutes, not days.

## Baseline Solution
A simple script that counts lines of code and checks for a README. (See `src/baseline/naive_solution.py`). It fails because it equates "more code" with "better code".

## Advanced Agentic Solution
A LangGraph agent that clones the repo and uses specialized tools to analyze cyclomatic complexity, verify test directories, and check dependency health. It includes a Human-in-the-Loop checkpoint before executing analysis.

## Improvement Changelog
- **Baseline:** Simple file counting. Result: Inaccurate quality scores.
- **Iteration 1:** Added `check_test_coverage`. Result: Caught repos with no tests.
- **Iteration 2:** Added `analyze_code_complexity` using Radon. Result: Differentiated between clean code and messy "spaghetti" code.
- **Final:** Combined tools into a unified report.

## Main Failure Mode & Hot Take
**Failure Mode:** The agent initially tried to run `pytest` on every repo, which crashed due to missing environment dependencies. 
**Hot Take:** Agents need *static analysis* tools (like Radon) rather than *execution* tools for initial code audits. Execution is too fragile for unknown environments.
