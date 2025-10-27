import atlastk

HEAD = """
<title>Hello, World! | Zelbinium</title>
<link rel="icon" type="image/png" href="https://zelbinium.org/Avatar.png" />
"""

BODY = """
<fieldset>
  <input id="input" maxlength="20" placeholder="Enter a name here" type="text"
      xdh:onevent="Submit" value="World"/>
  <button xdh:onevent="Submit">Submit</button>
  <hr/>
  <fieldset>
    <output id="output"></output>
  </fieldset>
</fieldset>
"""

def acConnect(dom):
  dom.inner("", BODY )
  dom.focus( "input")


def acSubmit(dom):
  dom.setValue("output", "Hello, {}!".format(dom.getValue("input")))
  dom.setValue("input", "")
  dom.focus( "input")


CALLBACKS = {
  "": acConnect,
  "Submit": acSubmit,
}

atlastk.launch(CALLBACKS, headContent=HEAD)
