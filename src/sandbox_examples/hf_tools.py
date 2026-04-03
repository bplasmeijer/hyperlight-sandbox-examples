import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def _read_token_from_env_files():
    # Keep this tiny and dependency-free to work in minimal environments.
    for filename in [".env.local", ".env"]:
        if not os.path.exists(filename):
            continue
        try:
            with open(filename, "r", encoding="utf-8") as f:
                for line in f:
                    stripped = line.strip()
                    if not stripped or stripped.startswith("#"):
                        continue
                    if "=" not in stripped:
                        continue
                    key, value = stripped.split("=", 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    if key in {"HF_TOKEN", "HUGGINGFACEHUB_API_TOKEN", "HUGGING_FACE_HUB_TOKEN"} and value:
                        return value, filename
        except OSError:
            continue
    return "", None


def _resolve_hf_token():
    env_keys = ["HF_TOKEN", "HUGGINGFACEHUB_API_TOKEN", "HUGGING_FACE_HUB_TOKEN"]
    for key in env_keys:
        value = os.getenv(key, "").strip()
        if value:
            return value, f"env:{key}"

    file_value, source = _read_token_from_env_files()
    if file_value:
        return file_value, f"file:{source}"
    return "", None


def _token_lookup_hint():
    return {
        "env_keys": ["HF_TOKEN", "HUGGINGFACEHUB_API_TOKEN", "HUGGING_FACE_HUB_TOKEN"],
        "files": [".env.local", ".env"],
    }


def _normalize_token(raw_token):
    token = (raw_token or "").strip().strip('"').strip("'")
    if token.lower().startswith("bearer "):
        token = token.split(None, 1)[1].strip()
    # Defensive cleanup for accidental whitespace-separated values.
    if " " in token:
        token = token.split(" ", 1)[0].strip()
    return token


def _post_json(url, payload, token):
    request = Request(url=url, data=json.dumps(payload).encode("utf-8"), method="POST")
    request.add_header("Authorization", f"Bearer {token}")
    request.add_header("Content-Type", "application/json")
    request.add_header("Accept", "application/json")
    request.add_header("User-Agent", "hyperlight-sandbox-examples/1.0")

    try:
        with urlopen(request, timeout=60) as response:
            status = response.getcode()
            body = response.read().decode("utf-8", errors="replace")
        return {"ok": True, "status": status, "body": body, "url": url}
    except HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace")
        return {
            "ok": False,
            "status": exc.code,
            "error": error_body[:300],
            "error_type": "HTTPError",
            "url": url,
        }
    except URLError as exc:
        return {
            "ok": False,
            "status": None,
            "error": str(exc),
            "error_type": "URLError",
            "url": url,
        }


def _get_json(url, token=None):
    request = Request(url=url, method="GET")
    if token:
        request.add_header("Authorization", f"Bearer {token}")

    try:
        with urlopen(request, timeout=60) as response:
            status = response.getcode()
            body = response.read().decode("utf-8", errors="replace")
        return {"ok": True, "status": status, "body": body, "url": url}
    except HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace")
        return {
            "ok": False,
            "status": exc.code,
            "error": error_body[:300],
            "error_type": "HTTPError",
            "url": url,
        }
    except URLError as exc:
        return {
            "ok": False,
            "status": None,
            "error": str(exc),
            "error_type": "URLError",
            "url": url,
        }


def _fetch_router_models(token):
    response = _get_json("https://router.huggingface.co/v1/models", token=token)
    if not response.get("ok"):
        return {
            "ok": False,
            "error": response.get("error") or response.get("status"),
            "status": response.get("status"),
            "models": [],
            "url": response.get("url"),
        }

    try:
        parsed = json.loads(response.get("body", "{}"))
    except json.JSONDecodeError:
        return {
            "ok": False,
            "error": "Model catalog response is not valid JSON",
            "status": response.get("status"),
            "models": [],
            "url": response.get("url"),
        }

    data = parsed.get("data") if isinstance(parsed, dict) else None
    models = []
    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                model_id = item.get("id")
                if isinstance(model_id, str) and model_id:
                    models.append(model_id)

    return {
        "ok": True,
        "status": response.get("status"),
        "models": models,
        "url": response.get("url"),
    }


def _dedupe_keep_order(values):
    out = []
    seen = set()
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        out.append(value)
    return out


def _extract_generated_text(parsed):
    # hf-inference style: [{"generated_text": "..."}]
    if isinstance(parsed, list) and parsed and isinstance(parsed[0], dict):
        value = parsed[0].get("generated_text")
        if value:
            return value

    # OpenAI-completions style: {"choices": [{"text": "..."}]}
    if isinstance(parsed, dict):
        choices = parsed.get("choices")
        if isinstance(choices, list) and choices and isinstance(choices[0], dict):
            text_value = choices[0].get("text")
            if text_value:
                return text_value

            # OpenAI-chat-completions style: {"choices": [{"message": {"content": "..."}}]}
            message = choices[0].get("message")
            if isinstance(message, dict):
                content_value = message.get("content")
                if content_value:
                    return content_value

    return None


def hf_generate_text(prompt="", model="openai-community/gpt2", max_new_tokens=64):
    token, token_source = _resolve_hf_token()
    token = _normalize_token(token)
    if not token:
        return {
            "ok": False,
            "status": None,
            "token_source": None,
            "token_lookup": _token_lookup_hint(),
            "error": (
                "No Hugging Face token found. Create one at "
                "https://huggingface.co/settings/tokens and set one of: "
                "HF_TOKEN, HUGGINGFACEHUB_API_TOKEN, HUGGING_FACE_HUB_TOKEN "
                "or put HF_TOKEN=... in .env.local/.env"
            ),
        }

    router_models_info = _fetch_router_models(token=token)

    completions_payload = {
        "model": model,
        "prompt": prompt,
        "max_tokens": int(max_new_tokens),
    }
    chat_completions_payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": int(max_new_tokens),
    }

    candidate_models = [model]
    router_models = router_models_info.get("models", [])
    router_model_set = set(router_models)
    if router_models:
        preferred = [
            "Qwen/Qwen2.5-7B-Instruct",
            "mistralai/Mistral-7B-Instruct-v0.3",
            "meta-llama/Llama-3.1-8B-Instruct",
            "google/gemma-2-9b-it",
            "google/gemma-4-27b-it",
        ]
        for pref in preferred:
            if pref in router_model_set:
                candidate_models.append(pref)

        # Include a few catalog models as a last resort to avoid hard-coded dead ends.
        candidate_models.extend(router_models[:8])

    candidate_models = _dedupe_keep_order(candidate_models)

    endpoint_kinds = ["router_completions", "router_chat_completions"]

    def make_url_and_payload(candidate_model, endpoint_kind):
        if endpoint_kind == "router_completions":
            payload = dict(completions_payload)
            payload["model"] = candidate_model
            return ("https://router.huggingface.co/v1/completions", payload)

        payload = dict(chat_completions_payload)
        payload["model"] = candidate_model
        return ("https://router.huggingface.co/v1/chat/completions", payload)

    attempt_details = []
    response = None
    selected_model = None
    selected_endpoint_kind = None
    for candidate in candidate_models:
        for endpoint_kind in endpoint_kinds:
            url, payload = make_url_and_payload(candidate, endpoint_kind)
            candidate_response = _post_json(url=url, payload=payload, token=token)

            parsed = None
            generated_text = None
            if candidate_response.get("ok"):
                body = candidate_response.get("body", "")
                try:
                    parsed = json.loads(body)
                    generated_text = _extract_generated_text(parsed)
                except json.JSONDecodeError:
                    parsed = None

            attempt_details.append({
                "model": candidate,
                "endpoint_kind": endpoint_kind,
                "status": candidate_response.get("status"),
                "ok": candidate_response.get("ok"),
                "url": candidate_response.get("url"),
                "error_type": candidate_response.get("error_type"),
                "error_preview": candidate_response.get("error"),
                "generated_text_found": bool(generated_text),
            })

            response = candidate_response

            if candidate_response.get("ok") and generated_text:
                response["parsed"] = parsed
                response["generated_text"] = generated_text
                selected_model = candidate
                selected_endpoint_kind = endpoint_kind
                break

            # Invalid credentials or quota failures should stop immediately.
            # Do not stop on 403 because a different model/provider may still work.
            if candidate_response.get("status") in {401, 402, 429}:
                selected_model = candidate
                selected_endpoint_kind = endpoint_kind
                break

        if selected_model and selected_endpoint_kind:
            break

    if response is None:
        response = {"ok": False, "status": None, "error": "No response from router"}

    if not response.get("ok") or not response.get("generated_text"):
        auth_hint = None
        if response.get("status") == 401:
            auth_hint = (
                "Router returned 401. Verify your token is valid and not a login password. "
                "Use a Hugging Face access token (starts with hf_) and set only the token value "
                "(without 'Bearer ')."
            )
        return {
            "ok": False,
            "status": response["status"],
            "token_source": token_source,
            "router_model_catalog_status": router_models_info.get("status"),
            "router_model_catalog_url": router_models_info.get("url"),
            "router_model_count": len(router_models),
            "router_model_sample": router_models[:10],
            "attempted_models": _dedupe_keep_order([item["model"] for item in attempt_details]),
            "attempt_details": attempt_details,
            "last_url": response.get("url"),
            "auth_hint": auth_hint,
            "error": (
                f"HF router did not return generated text. "
                f"Last error/status: {response.get('error') or response.get('status')}"
            ),
        }

    status = response["status"]
    parsed = response.get("parsed")
    generated_text = response.get("generated_text")

    return {
        "ok": True,
        "status": status,
        "model": selected_model,
        "endpoint_kind": selected_endpoint_kind,
        "token_source": token_source,
        "router_model_catalog_status": router_models_info.get("status"),
        "router_model_catalog_url": router_models_info.get("url"),
        "router_model_count": len(router_models),
        "router_model_sample": router_models[:10],
        "attempted_models": _dedupe_keep_order([item["model"] for item in attempt_details]),
        "attempt_details": attempt_details,
        "generated_text": generated_text,
        "raw": parsed,
    }
