import atlastk

BODY = """
<fieldset style="width: max-content; height: 100%; display: flex; flex-flow: column; box-sizing: border-box;">
  <fieldset style="flex-grow: 1;">
    <div id="Output" style="display: flex; flex-direction: column-reverse; height: 100%;"/>
  </fieldset>
  <p style="height: 10px; margin: 0px;"/>
  <div>
    <input id="Input" xdh:onevent="Submit" type="text" placeholder="pseudo"/>
    <button xdh:onevent="Submit">Submit</button>
  </div>
</fieldset>
"""

def acConnect(dom):
  dom.inner("", BODY)
  dom.focus("Input")

def acSubmit(dom):
  dom.begin("Output", f"<div>Hello, <i>{dom.getValue('Input')}</i>!</div>")
  dom.setAttribute("Input", "placeholder", "Message");
  dom.setValue("Input", "")
  dom.focus("Input")

CALLBACKS = {
  "": acConnect,
  "Submit": acSubmit
}

atlastk.launch(CALLBACKS)