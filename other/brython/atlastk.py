import javascript

javascript.import_js("atlastk.js", alias="atlastkjs")

def launch(callbacks, userCallback = None, headContent = None):
  atlastkjs.launch(callbacks)