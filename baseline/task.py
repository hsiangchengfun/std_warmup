"""
Baseline computation pipeline.

Intentionally inefficient but correct. The goal of the challenge is for an
agent to rewrite `run_task` (or its sub-steps) so that the same output is
produced faster.

Pipeline:
    step1: pairwise sum table        (O(n^2))
    step2: cumulative running max    (O(n^2))
    step3: nested duplicate counter  (O(n^2))
    final: aggregated signature
"""

from typing import List, Tuple


def step1_pairwise_sums(numbers: List[int]) -> List[int]:
    """For each index i, sum numbers[i] + numbers[j] for all j.

    Implemented with an explicit nested loop on purpose.
    """
    result = []
    for i in range(len(numbers)):
        total = 0
        for j in range(len(numbers)):
            total += numbers[i] + numbers[j]
        result.append(total)
    return result


def step2_running_max(values: List[int]) -> List[int]:
    """Running maximum, recomputed from scratch at each index."""
    result = []
    for i in range(len(values)):
        current_max = values[0]
        for j in range(i + 1):
            if values[j] > current_max:
                current_max = values[j]
        result.append(current_max)
    return result


def step3_duplicate_counts(values: List[int]) -> List[Tuple[int, int]]:
    """For each value, count how many times it appears in the list.

    Implemented with a nested loop instead of a hash map.
    """
    result = []
    for i in range(len(values)):
        count = 0
        for j in range(len(values)):
            if values[j] == values[i]:
                count += 1
        result.append((values[i], count))
    return result


def run_task(numbers: List[int]) -> int:
    """Full pipeline. Returns a single deterministic integer signature."""
    a = step1_pairwise_sums(numbers)
    b = step2_running_max(a)
    c = step3_duplicate_counts(b)

    signature = 0
    for value, count in c:
        signature = (signature * 31 + value * count) % (10 ** 9 + 7)
    return signature
