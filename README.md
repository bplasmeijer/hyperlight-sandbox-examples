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
```

Or in one step:

```bash
make
```

## What it does

`quickstart.py` creates a Wasm-backed Python sandbox, registers a host `add` tool, allows outbound HTTP to `httpbin.org`, then runs untrusted code inside the micro-VM that calls both.

Expected output:

```
3 + 4 = 7, HTTP status: 200
```
