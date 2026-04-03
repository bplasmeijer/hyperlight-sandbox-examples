import json
import os

from _common import build_sandbox, run_guest_code

from sandbox_examples.hf_tools import hf_generate_text
from sandbox_examples.shared_tools import utc_now_iso


DEFAULT_MODEL = "meta-llama/Llama-3.1-8B-Instruct"


def build_guest_code(model):
    model_literal = json.dumps(model)
    return f"""
    print('== Hugging Face Real LLM Call Example ==')

    prompt = 'Write one concise sentence about running untrusted code safely.'
    model = {model_literal}

    stamp = call_tool('utc_now_iso')
    result = call_tool('hf_generate_text', prompt=prompt, model=model, max_new_tokens=48)
    meta = http_get(f'https://huggingface.co/api/models?search={{model}}&limit=1')

    print(f'timestamp: {{stamp}}')
    print(f'model metadata status: {{meta["status"]}}')
    print(f'model metadata url: https://huggingface.co/api/models?search={{model}}&limit=1')
    print(f'router model catalog status: {{result.get("router_model_catalog_status")}}')
    print(f'router model catalog url: {{result.get("router_model_catalog_url")}}')
    print(f'router model count: {{result.get("router_model_count")}}')
    print(f'router model sample: {{result.get("router_model_sample")}}')

    if result.get('ok'):
        print(f'inference status: {{result["status"]}}')
        print(f'token source: {{result.get("token_source")}}')
        print(f'selected model: {{result.get("model")}}')
        print(f'endpoint kind: {{result.get("endpoint_kind")}}')
        print('prompt:')
        print(f'  {{prompt}}')
        print('completion:')
        print(f'  {{result.get("generated_text")}}')
    else:
        print('inference call not completed')
        print(f'token source: {{result.get("token_source")}}')
        print(f'token lookup: {{result.get("token_lookup")}}')
        if result.get('auth_hint'):
            print(f'auth hint: {{result.get("auth_hint")}}')
        print(f'last url: {{result.get("last_url")}}')
        print(f'attempted models: {{result.get("attempted_models")}}')
        details = result.get('attempt_details') or []
        for d in details:
            print(
                "  attempt -> "
                f"model={{d.get('model')}}, endpoint_kind={{d.get('endpoint_kind')}}, "
                f"status={{d.get('status')}}, ok={{d.get('ok')}}, "
                f"error_type={{d.get('error_type')}}, url={{d.get('url')}}"
            )
            if d.get('error_preview'):
                print(f"    error_preview={{d.get('error_preview')}}")
        print(f'error: {{result.get("error")}}')
    """


def main():
    selected_model = os.getenv("HF_MODEL", DEFAULT_MODEL)
    sandbox = build_sandbox(
        tools=[
            ("utc_now_iso", utc_now_iso),
            ("hf_generate_text", hf_generate_text),
        ],
        domains=["https://huggingface.co"],
    )
    run_guest_code(sandbox, build_guest_code(selected_model))


if __name__ == "__main__":
    main()
