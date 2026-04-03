# Hyperlight Sandbox Examples

This repository now includes five runnable examples.

## 1) `examples/quickstart.py`

Smallest possible demo:
- Register one host tool (`add`)
- Allow one domain (`https://httpbin.org`)
- Run guest code with one function call and one HTTP call

Run with:

```bash
make run
```

## 2) `examples/real_example.py`

A realistic checkout flow:
- Calculates line totals with tax
- Applies coupon discounts
- Pings outbound HTTP endpoints
- Prints a transaction-style report

It uses shared functions imported from `src/sandbox_examples/shared_tools.py` and registers them as sandbox tools.

Run with:

```bash
make run-real
```

## 3) `examples/function_call_example.py`

A second scenario focused on cross-file function calls:
- Imports `calc_line_total`, `discount_for_coupon`, `shipping_for_weight_kg`, `utc_now_iso` from `src/sandbox_examples/shared_tools.py`
- Registers all imported functions as tools
- Runs a quote flow that combines tax, shipping, coupon discount, and HTTP validation

Run with:

```bash
make run-fn
```

## 4) `examples/huggingface_example.py`

Hugging Face API demo:
- Allow-lists `https://huggingface.co`
- Calls public search endpoint `/api/models?search=distilbert-base-uncased&limit=1`
- Prints HTTP status from inside the sandbox

Run with:

```bash
make run-hf
```

## 5) `examples/hf_llm_example.py`

Authenticated real LLM inference demo:
- Calls Hugging Face router endpoints through a host tool
- Uses `HF_TOKEN` from environment for Authorization
- Discovers router-supported models from `/v1/models`
- Prints generated text for the given prompt when auth/model access is valid
- Prints verbose diagnostics (token source, attempted models/endpoints, error previews) when inference fails
- Uses default model `meta-llama/Llama-3.1-8B-Instruct`

Create a token here: https://huggingface.co/settings/tokens

Run with:

```bash
export HF_TOKEN=hf_xxx
make run-hf-llm
```

Optional model override:

```bash
HF_MODEL="meta-llama/Llama-3.1-8B-Instruct" make run-hf-llm
```

Also supported:
- `HUGGINGFACEHUB_API_TOKEN`
- `HUGGING_FACE_HUB_TOKEN`
- `.env.local` or `.env` containing `HF_TOKEN=hf_xxx`

## Shared function module

`src/sandbox_examples/shared_tools.py` contains reusable host-side business functions. Both `examples/real_example.py` and `examples/function_call_example.py` import from it, so function definitions live in one place.

`src/sandbox_examples/hf_tools.py` contains the authenticated Hugging Face inference helper used by `examples/hf_llm_example.py`.

Pattern:

```python
from sandbox_examples.shared_tools import calc_line_total

sandbox.register_tool("calc_line_total", calc_line_total)
```

This keeps examples clear and makes it easy to add new scenarios without duplicating logic.
