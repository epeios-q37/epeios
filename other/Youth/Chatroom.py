import atlastk

BODY = """
<fieldset style="width: max-content; height: 100%; display: flex; flex-flow: column; box-sizing: border-box;">
  <fieldset style="flex-grow: 1;">
    <div>test</div>
  </fieldset>
  <p style="height: 10px; margin: 0px;"/>
  <div>
    <input type="text">
    <button>Submit</button>
  </div>
</fieldset>
"""

def acConnect(dom):
  dom.inner("", BODY)

CALLBACKS = {
  "": acConnect
}

atlastk.launch(CALLBACKS)