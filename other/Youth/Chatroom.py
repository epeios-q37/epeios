import atlastk

BODY = """
<fieldset style="width: min-content; height: 100%; display: flex; flex-flow: column; box-sizing: border-box;">
  <fieldset id="Output" style="display: flex; flex-direction: column-reverse; height: 100%; overflow: auto; overflow-wrap: anywhere;">
  </fieldset>
  <p style="height: 10px; margin: 0px;"/>
  <div style="display: flex;">
    <input id="Input" xdh:onevent="Submit" type="text" placeholder="pseudo"/>
    <button xdh:onevent="Submit">Submit</button>
  </div>
</fieldset>
"""

class Profile:
  def __init__(self):
    self.pseudo = ""

def acConnect(profile, dom):
  dom.inner("", BODY)
  dom.focus("Input")

def acSubmit(profile, dom):
  input = dom.getValue('Input').strip()

  if input:
    if profile.pseudo:
      dom.begin("Output", f"<div><span style='color: red;'>{profile.pseudo}</span>: {input}!</div>")
    else:
      profile.pseudo = input
      dom.begin("Output", f"<div>Hello, <i>{input}</i>!</div>")
      dom.setAttribute("Input", "placeholder", "Message");

  dom.setValue("Input", "")
  dom.focus("Input")

CALLBACKS = {
  "": acConnect,
  "Submit": acSubmit
}

atlastk.launch(CALLBACKS, Profile)