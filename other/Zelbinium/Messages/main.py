import atlastk

HEAD = """
<title>Messages | Zelbinium</title>
<style>
.me, .other {
  border-radius: 10px;
  padding: 5px;
  margin: 1px;
}
.me {
  margin-left: 15px;
  background-color: lightcyan;
}
.other {
  margin-right: 15px;
  background-color: lightyellow;
}
</style>
"""

BODY = """
<fieldset style="width: min-content; height: 100%; max-height: 500px; display: flex; flex-flow: column; box-sizing: border-box;">
  <output id="Output" style="display: flex; flex-direction: column-reverse; height: 100%; overflow: auto; overflow-wrap: anywhere;">
  </output>
  <p style="height: 10px; margin: 0px;"/>
  <div style="display: flex;">
    <input id="Input" xdh:onevent="Submit" type="text" placeholder="Pseudo"/>
    <button xdh:onevent="Submit">Submit</button>
  </div>
</fieldset>
"""

message = ""

class Profile:
  def __init__(self):
    self.pseudo = ""


def acConnect(profile, dom):
  dom.inner("", BODY)
  dom.enableElement("XDHFullHeight")
  dom.focus("Input")


def acSubmit(profile, dom):
  global message
  input = dom.getValue('Input').strip()

  if input:
    if profile.pseudo:
      dom.begin("Output", f"<div class='me'>{input}</div>")
      message = input
      atlastk.broadcastAction("Display", str(profile.pseudo))
    else:
      profile.pseudo = input
      dom.begin("Output", f"<div>Hello, <i>{input}</i>!</div>")
      dom.setAttribute("Input", "placeholder", "Message");

  dom.setValue("Input", "")
  dom.focus("Input")


def acDisplay(profile, dom, id):
  if id != profile.pseudo:
    dom.begin("Output", f"<div class='other'><span style='font-style: oblique;'>{id}</span>: {message}</div>")


CALLBACKS = {
  "": acConnect,
  "Submit": acSubmit,
  "Display": acDisplay
}

atlastk.launch(CALLBACKS, Profile, HEAD)