import os, time
from dataclasses import dataclass
from openai import OpenAI

client = OpenAI()  # uses OPENAI_API_KEY automatically

@dataclass
class RunResult:
    output_text: str
    latency_s: float
    total_tokens: int | None
    cost_usd: float | None

def run_prompt(prompt: str, model: str, max_tokens: int, temperature: float) -> RunResult:
    start = time.perf_counter()

    resp = client.responses.create(
        model=model,
        input=prompt,
        max_output_tokens=max_tokens,
        temperature=temperature,
    )

    latency = time.perf_counter() - start

    # Pull the text out (Responses API)
    output_text = resp.output_text if hasattr(resp, "output_text") else str(resp)

    # Usage/tokens (varies by response; handle safely)
    total_tokens = None
    if getattr(resp, "usage", None) and getattr(resp.usage, "total_tokens", None) is not None:
        total_tokens = resp.usage.total_tokens

    # Cost: leave None for now (we’ll wire real pricing next)
    return RunResult(
        output_text=output_text,
        latency_s=latency,
        total_tokens=total_tokens,
        cost_usd=None,
    )
