import json
from browser.local_storage import storage

import atlastk

CONFIG_ITEM = "ucuq-config"

# Config keys
K_DEVICE = "Device"
K_DEVICE_ID = "Id"
K_DEVICE_TOKEN = "Token"

# Widgets
W_ID = "Id"
W_TOKEN = "Token"
W_OUTPUT = "Output"


def getConfig():
  if CONFIG_ITEM in storage:
    return json.loads(storage[CONFIG_ITEM])
  else:
    return {
      K_DEVICE: {}
    }
  

def getConfigDevice():
  return getConfig()[K_DEVICE]


async def acConnect(dom):
  await dom.inner("", BODY)

  device = getConfigDevice()

  if K_DEVICE_TOKEN in device:
    await dom.setAttribute(W_TOKEN, "placeholder", "<hidden>")
    await dom.focus(W_ID)
  else:
    await dom.focus(W_TOKEN)

  if K_DEVICE_ID in device:
    await dom.setValue(W_ID, device[K_DEVICE_ID])


async def acSave(dom):
  token, id = (await dom.getValues([W_TOKEN, W_ID])).values()

  device = getConfigDevice()

  token = token.strip()
  id = id.strip()

  if token == "" and not K_DEVICE_TOKEN in device:
    await dom.alert("Please enter a token value!")
    await dom.focus("Token")
    return
  
  if token != "":
    device[K_DEVICE_TOKEN] = token

  if id != "":
    device[K_DEVICE_ID] = id

  config = getConfig()

  config[K_DEVICE] = device

  storage[CONFIG_ITEM] = json.dumps(config, indent=2)

  await dom.setValue(W_OUTPUT, "Config file updated!")


async def acDelete(dom):

  if await dom.confirm("Are you sur you want to delete config ?"):
    del storage[CONFIG_ITEM]
    await dom.removeAttribute("Token", "placeholder")
    await dom.setValues({"Token": "", "Id": ""})
    await dom.focus("Token")
    await dom.setValue("Output", "Config deleted!")


CALLBACKS = {
  "": acConnect,
  "Save": acSave,
  "Delete": acDelete
}

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
  <fieldset>
    <output id="Output">Enter token and/or id.</output>
  </fiedlset>
</fieldset>
"""

atlastk.launch(CALLBACKS)