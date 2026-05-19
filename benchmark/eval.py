"""
Evaluation logic for the Autonomous Code Optimization Challenge.

A candidate function is scored by:
    1. Running it on the input.
    2. Checking that its output matches the baseline's output.
    3. Comparing its runtime to the baseline's runtime.

    score = baseline_time / execution_time   (if correct)
    score = 0                                (if incorrect)
"""

import time
from typing import Any, Callable, Dict


def _measure(func: Callable, data: Any) -> (float, Any):
    start = time.perf_counter()
    output = func(data)
    elapsed = time.perf_counter() - start
    return elapsed, output


def evaluate(
    candidate: Callable,
    baseline: Callable,
    data: Any,
) -> Dict[str, Any]:
    """Evaluate `candidate` against `baseline` on `data`.

    Returns a dict with keys:
        baseline_time, candidate_time, correct, score, baseline_output, candidate_output
    """
    baseline_time, baseline_output = _measure(baseline, data)
    candidate_time, candidate_output = _measure(candidate, data)

    correct = candidate_output == baseline_output

    if correct and candidate_time > 0:
        score = baseline_time / candidate_time
    else:
        score = 0.0

    return {
        "baseline_time": baseline_time,
        "candidate_time": candidate_time,
        "correct": correct,
        "score": score,
        "baseline_output": baseline_output,
        "candidate_output": candidate_output,
    }
