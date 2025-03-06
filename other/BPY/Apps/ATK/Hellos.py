import atlastk

async def acConnect(dom):
  await dom.inner("", BODY)
  await dom.focus("Input")
 

async def acSubmit(dom):
  global name
  name = await dom.getValue("Input")
  await dom.setValue("Input", "")
  await dom.focus("Input")
  atlastk.broadcastAction("Refresh")


async def acDisplay(dom):
  await dom.begin("Output", f"<div>Hello, {name}!</div>")


CALLBACKS = {
  "": acConnect,
  "Submit": acSubmit,
  "Refresh": acDisplay
}
 

HEAD = """
<title>Hello, World! (shared)</title>
"""
 
BODY = """
<fieldset>
 <input id="Input" data-xdh-onevent="Submit" placeholder="Enter a name here" value="World"/>
 <button data-xdh-onevent="Submit">Hello</button>
 <hr/>
 Output shared between all sessions.
 <hr/>
 <fieldset>
  <output id="Output"></output>
 </fieldset>
</fieldset>
"""


atlastk.launch(CALLBACKS, headContent=HEAD)