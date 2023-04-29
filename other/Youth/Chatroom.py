import atlastk

BODY = """
<div style="width: max-content; height: 100%; display: flex; flex-flow: column; border: solid 1px; padding: 5px;">
<legend>test</legend>
  <div>
  <input type="text">
  <button>Submit</button>
    </div>
  <p style="height: 10px; margin: 0px;"/>
  <div style="flex-grow: 1; border: solid  1px;">
  <div>test</div>
  </div>
</div>
"""

def acConnect(dom):
  dom.inner("", BODY)

CALLBACKS = {
  "": acConnect
}

atlastk.launch(CALLBACKS)