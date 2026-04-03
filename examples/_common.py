"""Shared helpers for runnable sandbox examples."""

from textwrap import dedent

from hyperlight_sandbox import Sandbox


def build_sandbox(*, tools=None, domains=None):
    sandbox = Sandbox(backend="wasm", module="python_guest.path")

    for name, fn in (tools or []):
        sandbox.register_tool(name, fn)

    for domain in (domains or []):
        sandbox.allow_domain(domain)

    return sandbox


def run_guest_code(sandbox, code):
    result = sandbox.run(dedent(code).strip())
    print(result.stdout)
    if result.stderr:
        print("[guest stderr]")
        print(result.stderr)
