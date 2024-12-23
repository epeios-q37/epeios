import atlastk, ucuq, json

def acConnect(dom):
  infos = ucuq.ATKConnect(dom, BODY)
  dom.setValue("Infos", json.dumps(infos, indent=2))

BODY = """
<fieldset>
  <pre id="Infos"/>
</fieldset>
"""

atlastk.launch({"": acConnect})
