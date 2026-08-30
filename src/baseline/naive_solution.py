# src/baseline/naive_solution.py
import os
import sys
import json

def evaluate_repo_baseline(repo_path):
    """
    Naive baseline: Scores a repo purely on volume (files, lines of code) 
    and the mere existence of a README.
    """
    repo_name = os.path.basename(repo_path)
    
    # 1. Count files (ignoring .git)
    file_count = 0
    loc = 0 # Lines of Code
    has_readme = False
    
    for root, dirs, files in os.walk(repo_path):
        if '.git' in root:
            continue
        
        # Check for README
        if 'README.md' in files:
            has_readme = True
            
        for file in files:
            if file.endswith('.py'):
                file_count += 1
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        loc += sum(1 for _ in f)
                except Exception:
                    pass

    # 2. Calculate Naive Score (Max 10)
    score = 0
    if file_count > 50: score += 3
    elif file_count > 10: score += 1
    
    if loc > 10000: score += 4
    elif loc > 1000: score += 2
    
    if has_readme: score += 2
    
    # Participation point
    score += 1 

    return {
        "repo": repo_name,
        "baseline_score": score,
        "python_files": file_count,
        "lines_of_code": loc,
        "has_readme": has_readme
    }

def run_baseline():
    print("🚀 Running Naive Baseline Evaluation...\n")
    
    # Path to our cloned repos
    test_dir = "test_repos"
    repos = [
        os.path.join(test_dir, "repo_high_quality"),
        os.path.join(test_dir, "repo_medium_quality"),
        os.path.join(test_dir, "repo_low_quality")
    ]
    
    results = []
    for repo in repos:
        if os.path.exists(repo):
            result = evaluate_repo_baseline(repo)
            results.append(result)
            print(f" {result['repo']}: Score {result['baseline_score']}/10 | Files: {result['python_files']} | LOC: {result['lines_of_code']}")
        else:
            print(f"⚠️ Warning: {repo} not found. Did you run the git clone commands?")

    # Save results to a JSON file for the judges to see
    with open("baseline_results.json", "w") as f:
        json.dump(results, f, indent=4)
    print("\n✅ Baseline results saved to baseline_results.json")

if __name__ == "__main__":
    run_baseline()
