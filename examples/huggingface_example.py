from _common import build_sandbox, run_guest_code

from sandbox_examples.shared_tools import utc_now_iso


def main():
	sandbox = build_sandbox(
		tools=[("utc_now_iso", utc_now_iso)],
		domains=["https://huggingface.co"],
	)

	guest_code = """
	print('== Hugging Face Example ==')
	import json

	model_id = 'distilbert-base-uncased'
	url = f'https://huggingface.co/api/models?search={model_id}&limit=1'
	resp = http_get(url)
	stamp = call_tool('utc_now_iso')

	print(f'timestamp: {stamp}')
	print(f'model: {model_id}')
	print(f'GET {url} -> status: {resp["status"]}')

	body = resp.get('body', '')
	results = []
	if body:
		try:
			parsed = json.loads(body)
			if isinstance(parsed, list):
				results = parsed
		except Exception as e:
			print(f'warning: could not parse response body as JSON: {e}')

	if results:
		top = results[0]
		print('top search result:')
		print(f"  id: {top.get('id', '<unknown>')}")
		print(f"  downloads: {top.get('downloads', '<n/a>')}")
		print(f"  likes: {top.get('likes', '<n/a>')}")
		print(f"  pipeline_tag: {top.get('pipeline_tag', '<n/a>')}")
	else:
		print('no search results returned')
	"""
	run_guest_code(sandbox, guest_code)


if __name__ == "__main__":
	main()
