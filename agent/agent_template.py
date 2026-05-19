"""
Skeleton for the optimization agent.

The LLM client is wired up to OpenRouter by default so students can swap
between free and paid models without touching any other code. Everything
else — prompt design, code extraction, the iteration loop, error handling —
is left for the student to implement.

Set your key first:
    export OPENROUTER_API_KEY=sk-or-...

Default model is a free one (Llama 3.1 8B). To use a stronger model just
change `self.model`, e.g. "anthropic/claude-haiku-4-5".
"""

import os
from openai import OpenAI


class Agent:
    def __init__(
        self,
        model: str = "meta-llama/llama-3.1-8b-instruct:free",
        max_iterations: int = 10,
    ):
        self.model = model
        self.max_iterations = max_iterations
        self.client = OpenAI(
            api_key=os.environ["OPENROUTER_API_KEY"],
            base_url="https://openrouter.ai/api/v1",
        )
        # TODO: store paths, best-score tracker, history, etc.

    def call_llm(self, prompt: str) -> str:
        """Send `prompt` to the LLM via OpenRouter and return the raw text."""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content

    def propose_code(self, current_code: str, last_result: dict) -> str:
        """Build a prompt from the current code + last benchmark result,
        call the LLM, and return the proposed replacement source code.

        TODO:
            1. Write a prompt that includes `current_code` and feedback
               from `last_result` (timings, correctness, errors).
            2. Call self.call_llm(prompt).
            3. Extract the python code block from the response.
        """
        raise NotImplementedError

    def write_candidate(self, code: str) -> None:
        """Persist the proposed code to agent/candidate.py so the runner
        can load it.

        TODO: implement.
        """
        raise NotImplementedError

    def evaluate(self) -> dict:
        """Invoke the benchmark on the current candidate and return its result.

        TODO: import benchmark.eval.evaluate, load candidate.run_task,
        load data/input.json, run evaluation, return the result dict.
        """
        raise NotImplementedError

    def run(self) -> None:
        """Main optimization loop.

        TODO: iterate up to self.max_iterations times, calling
        propose_code -> write_candidate -> evaluate, tracking the best
        result seen so far. Handle LLM failures (bad syntax, timeouts,
        incorrect output) gracefully.
        """
        raise NotImplementedError


if __name__ == "__main__":
    Agent().run()
