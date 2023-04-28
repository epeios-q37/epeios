import atlastk

BODY = """
<div>
<fieldset style="width: max-content; height: 100%; display: flex; flex-flow: column;">
  <div>
  <input type="text">
  <button>Submit</button>
    </div>
  <p style="height: 10px; margin: 0px;"/>
  <fieldset style="flex-grow: 1;"></fieldset>
</fieldset>
</div>
"""

def acConnect(dom):
  dom.inner("", BODY)

CALLBACKS = {
  "": acConnect
}

atlastk.launch(CALLBACKS)