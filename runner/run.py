"""
Execution engine for the Autonomous Code Optimization Challenge.

Simulates an optimization loop:
    1. Load the baseline function.
    2. Try to load an agent-generated candidate function.
       (If none is available, fall back to the baseline so the loop still runs.)
    3. Repeatedly evaluate the candidate for a fixed number of rounds.
    4. Log per-iteration performance and print the best score.

Run with:
    python runner/run.py
"""

import importlib.util
import json
import os
import sys
from pathlib import Path

# Make the project root importable regardless of where the script is launched.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from baseline.task import run_task as baseline_run_task
from benchmark.eval import evaluate


MAX_ITERATIONS = 3
DATA_PATH = PROJECT_ROOT / "data" / "input.json"
CANDIDATE_PATH = PROJECT_ROOT / "agent" / "candidate.py"


def load_input():
    with open(DATA_PATH, "r") as f:
        payload = json.load(f)
    return payload["numbers"]


def load_candidate():
    """Load an agent-generated candidate function if one exists.

    The agent is expected to write a module at agent/candidate.py exposing
    a `run_task(numbers)` callable. If the file does not exist, we fall
    back to the baseline so the runner still demonstrates the loop.
    """
    if not CANDIDATE_PATH.exists():
        return baseline_run_task, "baseline (no candidate found)"

    spec = importlib.util.spec_from_file_location("candidate", CANDIDATE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if not hasattr(module, "run_task"):
        return baseline_run_task, "baseline (candidate missing run_task)"
    return module.run_task, "agent candidate"


def main():
    data = load_input()
    candidate, source_label = load_candidate()

    print(f"Loaded candidate: {source_label}")
    print(f"Input size: {len(data)}")
    print(f"Running optimization loop for {MAX_ITERATIONS} iterations.\n")

    best_score = 0.0
    best_iteration = -1
    history = []

    for iteration in range(1, MAX_ITERATIONS + 1):
        result = evaluate(candidate, baseline_run_task, data)
        history.append(result)

        status = "OK" if result["correct"] else "FAIL"
        print(
            f"[iter {iteration:02d}] "
            f"baseline={result['baseline_time']:.4f}s  "
            f"candidate={result['candidate_time']:.4f}s  "
            f"correct={status}  "
            f"score={result['score']:.3f}"
        )

        if result["score"] > best_score:
            best_score = result["score"]
            best_iteration = iteration

    print("\n--- Summary ---")
    print(f"Iterations run : {MAX_ITERATIONS}")
    print(f"Best score     : {best_score:.3f} (iteration {best_iteration})")
    avg_score = sum(h["score"] for h in history) / len(history)
    print(f"Average score  : {avg_score:.3f}")


if __name__ == "__main__":
    main()
