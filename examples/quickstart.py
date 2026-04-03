"""Smallest runnable sandbox example."""

from _common import build_sandbox, run_guest_code


def add(a=0, b=0):
	return a + b


def main():
	sandbox = build_sandbox(
		tools=[("add", add)],
		domains=["https://httpbin.org"],
	)

	guest_code = """
	total = call_tool('add', a=3, b=4)
	resp = http_get('https://httpbin.org/get')
	print(f"3 + 4 = {total}, HTTP status: {resp['status']}")
	"""
	run_guest_code(sandbox, guest_code)


if __name__ == "__main__":
	main()
