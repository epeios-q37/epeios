import atlastk

HEAD = """
<title>Hello, World! (shared) | Zelbinium</title>
<link rel="icon" type="image/png" href="https://zelbinium.q37.info/Avatar.png" />
"""
 
BODY = """
<fieldset>
 <input id="Input" data-xdh-onevent="Submit" placeholder="Enter a name here" value="World"/>
 <button data-xdh-onevent="Submit">Hello</button>
 <hr/>
 <fieldset>
  <output id="Output"></output>
 </fieldset>
</fieldset>
"""
 
def acConnect(dom):
  dom.inner("", BODY)
  dom.focus("Input")
 
def acSubmit(dom):
  global name
  name = dom.getValue("Input")
  dom.setValue("Input", "")
  dom.focus("Input")
  atlastk.broadcastAction("Refresh")

def acDisplay(dom):
  dom.begin("Output", f"<div>Hello, {name}!</div>")
 
CALLBACKS = {
  "": acConnect,
  "Submit": acSubmit,
  "Refresh": acDisplay
}
 
atlastk.launch(CALLBACKS, headContent=HEAD)