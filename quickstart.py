from hyperlight_sandbox import Sandbox

sandbox = Sandbox(backend="wasm", module="python_guest.path")
sandbox.register_tool("add", lambda a=0, b=0: a + b)
sandbox.allow_domain("https://httpbin.org")

result = sandbox.run("""
total = call_tool('add', a=3, b=4)
resp = http_get('https://httpbin.org/get')
print(f"3 + 4 = {total}, HTTP status: {resp['status']}")
""")
print(result.stdout)
