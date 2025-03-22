import atlastk


async def atk(dom):
  await dom.inner("", BODY)
  await dom.focus("input")


async def atkSubmit(dom):
  await dom.setValue("output", f"Hello, {await dom.getValue('input')}!")
  await dom.setValue("input", "")
  await dom.focus("input")


ATK_HEAD = """
  <title>Hello</title>
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

atlastk.launch(globals=globals())  
