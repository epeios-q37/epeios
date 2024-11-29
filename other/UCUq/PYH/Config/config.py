import os, sys, json

os.chdir(os.path.dirname(os.path.realpath(__file__)))
sys.path.append("../../atlastk.zip")

import atlastk

DEFAULT_HOST = "ucuq.q37.info"
DEFAULT_PORT = "53800"

def isDev():
  return "Q37_EPEIOS" in os.environ

CONFIG_FILE = ( "/home/csimon/q37/epeios/tools/ucuq/remote/wrappers/PYH/" if isDev() else "../" ) + "ucuq.json"

DEVICE_LABEL = "Device"
DEVICE_TOKEN_LABEL = "Token"
DEVICE_ID_LABEL = "Id"
PROXY_LABEL = "Proxy"
PROXY_HOST_LABEL = "Host"
PROXY_PORT_LABEL = "Port"

config = {}

def setAsHidden(dom, id):
  dom.setAttribute(id, "placeholder", "<hidden>")


def updateUI(dom):
  values = {}

  if PROXY_HOST_LABEL in proxy:
    values[PROXY_HOST_LABEL] = proxy[PROXY_HOST_LABEL]
  else:
    setAsHidden(dom, PROXY_HOST_LABEL)

  if PROXY_PORT_LABEL in proxy:
    values[PROXY_PORT_LABEL] = proxy[PROXY_PORT_LABEL]
  else:
    setAsHidden(dom, PROXY_PORT_LABEL)

  if DEVICE_TOKEN_LABEL in device:
    setAsHidden(dom, DEVICE_TOKEN_LABEL)

  if DEVICE_ID_LABEL in device:
    values[DEVICE_ID_LABEL] = device[DEVICE_ID_LABEL]

  if values:
    dom.setValues(values)

  dom.focus(DEVICE_TOKEN_LABEL if not DEVICE_TOKEN_LABEL in device else DEVICE_ID_LABEL)


def acConnect(dom):
  dom.inner("", BODY)

  updateUI(dom)


def acSave(dom):
  global proxy, device

  host, port, token, id = (value.strip() for value in dom.getValues([PROXY_HOST_LABEL, PROXY_PORT_LABEL, DEVICE_TOKEN_LABEL, DEVICE_ID_LABEL]).values())

  if not token and DEVICE_TOKEN_LABEL not in device:
    dom.alert("Please enter a token value!")
    dom.focus(DEVICE_TOKEN_LABEL)
    return

  if token:
    device[DEVICE_TOKEN_LABEL] = token

  if id:
    device[DEVICE_ID_LABEL] = id

  if not host and not port:
    proxy = None
  elif host:
    if not port:
      dom.alert("Please enter a port!")
      dom.focus(PROXY_PORT_LABEL)
      return

    proxy[PROXY_HOST_LABEL] = host
  elif port:
    if not host:
      dom.alert("Please enter a host!")
      dom.focus(PROXY_HOST_LABEL)
      return

  config[DEVICE_LABEL] = device

  if proxy:
    config[PROXY_LABEL] = proxy
  else:
    del config[PROXY_LABEL]

  with open(CONFIG_FILE, "w") as file:
    json.dump(config,file, indent=2)

  dom.setValue("Output", "Config file updated!")


def acDelete(dom):
  if isDev():
    dom.alert("You are in development environment, deleting config file is not possible!")
  elif dom.confirm("Are you sur you want to delete config file ?"):
    os.remove(CONFIG_FILE)

if os.path.isfile(CONFIG_FILE):
  with open(CONFIG_FILE, "r") as file:
    config = json.load(file)
else:
  config[DEVICE_LABEL] = {}
  config[PROXY_LABEL] = {}

device = config[DEVICE_LABEL]
proxy = config[PROXY_LABEL]

CALLBACKS = {
  "": acConnect,
  "Save": acSave,
  "Delete": acDelete
}

BODY = """
<fieldset>
  <details>
    <summary style="cursor: pointer">Show/hide proxy settings</summary>
    <fieldset>
      <legend>Proxy</legend>
      <label style="display: flex; justify-content: space-between; margin: 5px;">
        <span>Host:</span>
        <input id="Host">
      </label>
      <label style="display: flex; justify-content: space-between; margin: 5px;">
        <span>Port:</span>
        <input id="Port">
      </label>
    </fieldset>
  </details>
  <fieldset>
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
  </fieldset>
</fieldset>
"""

atlastk.launch(CALLBACKS)