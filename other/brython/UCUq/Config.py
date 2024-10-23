import json
from browser.local_storage import storage

import atlastk

CONFIG_ITEM = "ucuq-config"

config = {}

BODY = """
<fieldset>
  <fieldset style="display: flex; flex-direction: column">
    <legend>Device</legend>
    <label style="display: flex; justify-content: space-between; margin: 5px;">
      <span>Token:</span>
      <input id="Token">
    </label>
    <label style="display: flex; justify-content: space-between; margin: 5px;">
      <span>Id:</span>
      <input id="Id">
    </label>
  </fieldset>
  <div style="display: flex; justify-content: space-around; margin: 5px;">
    <button xdh:onevent="Save">Save</button>
    <button xdh:onevent="Delete">Delete</button>
  </div>
</fieldset>
"""


async def acConnect(dom):
  await dom.inner("", BODY)

  if "Token" in device:
    await dom.setAttribute("Token", "placeholder", "<hidden>")
    await dom.focus("Id")
  else:
    await dom.focus("Token")

  if "Id" in device:
    await dom.setValue("Id", device["Id"])


async def acSave(dom):
  token, id = (await dom.getValues(["Token", "Id"])).values()

  token = token.strip()
  id = id.strip()

  if token == "" and not "Token" in device:
    await dom.alert("Please entre a token value!")
    await dom.focus("Token")
    return
  
  if token != "":
    device["Token"] = token

  if id != "":
    device["Id"] = id

  config["Device"] = device

  storage[CONFIG_ITEM] = json.dumps(config, indent=2)

  await dom.alert("Config file updated!")


async def acDelete(dom):
  global device

  if await dom.confirm("Are you sur you want to delete config ?"):
    config["Device"] = {}
    del storage[CONFIG_ITEM]
    await dom.removeAttribute("Token", "placeholder")
    await dom.setValues({"Token": "", "Id": ""})
    await dom.focus("Token")
    await dom.alert("Config deleted!")


if CONFIG_ITEM in storage:
  config = json.loads(storage[CONFIG_ITEM])
else:
  config["Device"] = {}

device = config["Device"]

CALLBACKS = {
  "": acConnect,
  "Save": acSave,
  "Delete": acDelete
}

atlastk.launch(CALLBACKS)