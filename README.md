# Hyperlight Sandbox Quick Start

A minimal demo of [hyperlight-sandbox](https://github.com/hyperlight-dev/hyperlight-sandbox) — a multi-backend sandboxing framework for running untrusted code with controlled host capabilities built on [Hyperlight](https://github.com/hyperlight-dev/hyperlight).

## Requirements

- Linux with KVM (`/dev/kvm`)
- [uv](https://github.com/astral-sh/uv)
- Python 3.12 (installed automatically by `make setup`)

## KVM access

Hyperlight requires access to `/dev/kvm`. The device is owned by the `kvm` group (`crw-rw---- root kvm`), so your user must either be a member of that group or have an explicit ACL entry.

**Option 1 — add your user to the `kvm` group (recommended):**

```bash
sudo usermod -aG kvm $USER
# then log out and back in (or run: newgrp kvm)
```

**Option 2 — grant access via ACL (no re-login needed):**

```bash
sudo setfacl -m u:$USER:rw /dev/kvm
```

Verify access with:

```bash
ls -la /dev/kvm          # should show rw for your user or kvm group
getfacl /dev/kvm         # shows any ACL entries
```

> **Note:** `/dev/kvm` only exists if your CPU supports hardware virtualisation (`vmx` on Intel, `svm` on AMD) and the `kvm` kernel module is loaded. Check with:
> ```bash
> grep -m1 'vmx\|svm' /proc/cpuinfo   # must print something
> lsmod | grep kvm                     # should show kvm and kvm_intel/kvm_amd
> ```

## WSL (Windows Subsystem for Linux)

KVM passthrough in WSL2 requires **Windows 11 build 22000+** and a WSL2 kernel that exposes `/dev/kvm`.

### 1. Enable nested virtualisation

Open **PowerShell as Administrator**:

```powershell
# Enable nested virtualisation for the WSL2 VM
wsl --set-default-version 2
```

Then in `.wslconfig` (`%USERPROFILE%\.wslconfig`):

```ini
[wsl2]
nestedVirtualization=true
```

Restart the WSL VM:

```powershell
wsl --shutdown
wsl
```

### 2. Verify KVM is available inside WSL

```bash
ls /dev/kvm          # must exist
grep -m1 'vmx\|svm' /proc/cpuinfo
```

If `/dev/kvm` is missing, your Windows/WSL version may not support KVM passthrough. Update to the latest WSL kernel:

```powershell
wsl --update
```

### 3. Install dependencies inside WSL

Install `uv` if not present:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Install `make` if not present:

```bash
sudo apt update && sudo apt install -y make
```

Then follow the normal [Setup & Run](#setup--run) steps.

### 4. Grant KVM access (same as native Linux)

```bash
sudo usermod -aG kvm $USER   # then open a new WSL terminal
# or immediately via ACL:
sudo setfacl -m u:$USER:rw /dev/kvm
```

## Setup & Run

```bash
make setup   # create venv + install dependencies
make run     # run the quick start script
make run-real # run a realistic checkout + HTTP example
make run-fn   # run function-call example using shared tools
make run-hf   # run Hugging Face API example
make run-hf-llm # run authenticated Hugging Face LLM inference example
```

Or in one step:

```bash
make
```

## Examples

This repository includes five runnable examples.

Quick links:
- [`examples/quickstart.py`](examples/quickstart.py)
- [`examples/real_example.py`](examples/real_example.py)
- [`examples/function_call_example.py`](examples/function_call_example.py)
- [`examples/huggingface_example.py`](examples/huggingface_example.py)
- [`examples/hf_llm_example.py`](examples/hf_llm_example.py)

### 1) [`examples/quickstart.py`](examples/quickstart.py)

Smallest possible demo:
- Register one host tool (`add`)
- Allow one domain (`https://httpbin.org`)
- Run guest code with one function call and one HTTP call

Run with:

```bash
make run
```

### 2) [`examples/real_example.py`](examples/real_example.py)

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

### 3) [`examples/function_call_example.py`](examples/function_call_example.py)

A scenario focused on cross-file function calls:
- Imports `calc_line_total`, `discount_for_coupon`, `shipping_for_weight_kg`, `utc_now_iso` from `src/sandbox_examples/shared_tools.py`
- Registers all imported functions as tools
- Runs a quote flow that combines tax, shipping, coupon discount, and HTTP validation

Run with:

```bash
make run-fn
```

### 4) [`examples/huggingface_example.py`](examples/huggingface_example.py)

Hugging Face API demo:
- Allow-lists `https://huggingface.co`
- Calls public search endpoint `/api/models?search=distilbert-base-uncased&limit=1`
- Prints HTTP status from inside the sandbox

Run with:

```bash
make run-hf
```

### 5) [`examples/hf_llm_example.py`](examples/hf_llm_example.py)

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

Shared helpers:
- [`src/sandbox_examples/shared_tools.py`](src/sandbox_examples/shared_tools.py)
- [`src/sandbox_examples/hf_tools.py`](src/sandbox_examples/hf_tools.py)

## What it does

`examples/quickstart.py` creates a Wasm-backed Python sandbox, registers a host `add` tool, allows outbound HTTP to `httpbin.org`, then runs untrusted code inside the micro-VM that calls both.

Expected output:

```
3 + 4 = 7, HTTP status: 200
```

## Cross-file function example

`examples/function_call_example.py` imports shared host functions from `src/sandbox_examples/shared_tools.py` and registers them as tools:

```python
from sandbox_examples.shared_tools import calc_line_total

sandbox.register_tool("calc_line_total", calc_line_total)
```

This pattern keeps host logic reusable across multiple sandbox scenarios.
