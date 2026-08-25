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

## 2. Run the Baseline

```bash
python -m src.baseline.naive_solution
```

## 3. Run the Advanced Agentic Solution

```bash
python -m src.advanced.agentic_solution
```

## 4. View the Trajectory

Open `trajectories/run_001_trajectory.md`
