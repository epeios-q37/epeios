import javascript

javascript.import_js("sandbox.js", alias="sandboxjs")

def test():
    print('Hello from Python!')
    sandboxjs.test()
