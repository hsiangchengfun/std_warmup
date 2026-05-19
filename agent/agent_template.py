"""
Skeleton for the optimization agent.

The LLM client is wired up to OpenRouter by default so students can swap
between free and paid models without touching any other code. Everything
else — prompt design, code extraction, the iteration loop, error handling —
is left for the student to implement.

A `log()` helper is provided. Use it liberally in your implementation so
every intermediate step (prompts, LLM responses, extracted code, eval
results) is visible in the console while the agent runs.

Set your key first:
    export OPENROUTER_API_KEY=sk-or-...

Default model is a free one (GPT-OSS 20B). To use a stronger model just
change `self.model`, e.g. "anthropic/claude-haiku-4-5".
"""

import os
from openai import OpenAI


class Agent:
    def __init__(
        self,
        model: str = "openai/gpt-oss-20b:free",
        max_iterations: int = 10,
        verbose: bool = True,
    ):
        self.model = model
        self.max_iterations = max_iterations
        self.verbose = verbose
        self.client = OpenAI(
            api_key=os.environ["OPENROUTER_API_KEY"],
            base_url="https://openrouter.ai/api/v1",
        )
        self.log("AGENT INIT", f"model={model}  max_iterations={max_iterations}")
        # TODO: store paths, best-score tracker, history, etc.

    def log(self, label: str, content, max_len: int = 4000) -> None:
        """Pretty-print an intermediate value with a labeled banner.

        Call this everywhere — prompts, LLM responses, extracted code,
        eval results, iteration headers — so the console trace tells the
        full story of what the agent did.
        """
        if not self.verbose:
            return
        text = str(content)
        if len(text) > max_len:
            text = text[:max_len] + f"\n... [truncated {len(text) - max_len} chars]"
        bar = "=" * 72
        print(f"\n{bar}\n[{label}]\n{bar}\n{text}\n", flush=True)

    def call_llm(self, prompt: str) -> str:
        """Send `prompt` to the LLM via OpenRouter and return the raw text."""
        self.log("LLM PROMPT", prompt)
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
        )
        content = response.choices[0].message.content
        self.log("LLM RESPONSE", content)
        return content

    def propose_code(self, current_code: str, last_result: dict) -> str:
        """Build a prompt from the current code + last benchmark result,
        call the LLM, and return the proposed replacement source code.

        TODO:
            1. Write a prompt that includes `current_code` and feedback
               from `last_result` (timings, correctness, errors).
            2. Call self.call_llm(prompt).
            3. Extract the python code block from the response and
               self.log("EXTRACTED CODE", code) before returning it.
        """
        raise NotImplementedError

    def write_candidate(self, code: str) -> None:
        """Persist the proposed code to agent/candidate.py so the runner
        can load it.

        TODO: implement. Consider self.log("WROTE CANDIDATE", path) so
        you can see when this fires.
        """
        raise NotImplementedError

    def evaluate(self) -> dict:
        """Invoke the benchmark on the current candidate and return its result.

        TODO: import benchmark.eval.evaluate, load candidate.run_task,
        load data/input.json, run evaluation, return the result dict.
        End with self.log("EVAL RESULT", result) so each iteration's
        timing and correctness shows up in the trace.
        """
        raise NotImplementedError

    def run(self) -> None:
        """Main optimization loop.

        TODO: iterate up to self.max_iterations times, calling
        propose_code -> write_candidate -> evaluate, tracking the best
        result seen so far. Handle LLM failures (bad syntax, timeouts,
        incorrect output) gracefully. Wrap each iteration with
        self.log(f"ITERATION {i}", ...) and finish with a final
        self.log("BEST SCORE", best) summary.
        """
        raise NotImplementedError


if __name__ == "__main__":
    Agent().run()
