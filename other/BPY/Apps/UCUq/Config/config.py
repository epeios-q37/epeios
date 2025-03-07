import os, sys, json

import atlastk

# BEGIN BRY
from browser.local_storage import storage

def isDev():
  return False

CONFIG_ITEM = "ucuq-config"

def getConfig():
  if CONFIG_ITEM in storage:
    return json.loads(storage[CONFIG_ITEM])
  else:
    return {
      K_DEVICE: {},
      K_PROXY: {
        K_PROXY_HOST: DEFAULT_HOST,
        K_PROXY_PORT: DEFAULT_PORT
      }
    }
  

def save(config):
  storage[CONFIG_ITEM] = json.dumps(config, indent=2)


def delete():
  del storage[CONFIG_ITEM]
# END BRY

# BEGIN PYH
def isDev():
  return "Q37_EPEIOS" in os.environ

CONFIG_FILE = ( "/home/csimon/q37/epeios/tools/ucuq/remote/wrappers/PYH/" if isDev() else "../" ) + "ucuq.json"


def getConfig():
  if os.path.isfile(CONFIG_FILE):
    with open(CONFIG_FILE, "r") as file:
      return json.load(file)
  else:
    return {
      K_DEVICE: {},
      K_PROXY: {}
    }
  

def save(config):
  with open(CONFIG_FILE, "w") as file:
    json.dump(config, file, indent=2)


def delete():
    os.remove(CONFIG_FILE)
# END PYH

DEFAULT_HOST = "ucuq.q37.info"
DEFAULT_PORT = "53800"

# Keys
K_DEVICE = "Device"
K_DEVICE_TOKEN = "Token"
K_DEVICE_ID = "Id"
K_PROXY = "Proxy"
K_PROXY_HOST = "Host"
K_PROXY_PORT = "Port"

# Widgets
W_PROXY = "Proxy"
W_HOST = "Host"
W_PORT = "Port"
W_TOKEN = "Token"
W_ID = "Id"
W_OUTPUT = "Output"

# Style
S_HIDE_PROXY = "HideProxy"


def getConfigProxy():
  config = getConfig()

  if K_PROXY in config:
    return config[K_PROXY]
  else:
    return {}


def getConfigDevice():
  return getConfig()[K_DEVICE]


async def setAsHidden(dom, id):
  await dom.setAttribute(id, "placeholder", "<hidden>")


async def updateUI(dom):
  values = {}

  proxy = getConfigProxy()

  if K_PROXY_HOST in proxy:
    values[W_HOST] = proxy[K_PROXY_HOST]
  else:
    await setAsHidden(dom, W_HOST)

  if K_PROXY_PORT in proxy:
    values[W_PORT] = proxy[K_PROXY_PORT]
  else:
    await setAsHidden(dom, W_PORT)

  device = getConfigDevice()

  if K_DEVICE_TOKEN in device:
    await setAsHidden(dom, W_TOKEN)

  if K_DEVICE_ID in device:
    values[W_ID] = device[K_DEVICE_ID]

  if values:
    await dom.setValues(values)

  await dom.focus(W_TOKEN if not K_DEVICE_TOKEN in device else W_ID)


async def atk(dom):
  await dom.inner("", BODY)

# BEGIN PYH
  dom.disableElement(S_HIDE_PROXY)
# END PYH

  await updateUI(dom)


async def atkSave(dom):
  host, port, token, id = (value.strip() for value in (await dom.getValues([W_HOST, W_PORT, W_TOKEN, W_ID])).values())

  device = getConfigDevice()

  if not token and K_DEVICE_TOKEN not in device:
    await dom.alert("Please enter a token value!")
    await dom.focus(W_TOKEN)
    return

  if token:
    device[K_DEVICE_TOKEN] = token

  if id:
    device[K_DEVICE_ID] = id

  proxy = getConfigProxy()

  if not host and not port:
    proxy = None
  elif host:
    if not port:
      await dom.alert("Please enter a port!")
      await dom.focus(W_PORT)
      return

    proxy[K_PROXY_HOST] = host
  elif port:
    if not host:
      await dom.alert("Please enter a host!")
      await dom.focus(W_HOST)
      return
    
  config = getConfig()

  config[K_DEVICE] = device

  if proxy:
    config[K_PROXY] = proxy
  else:
    del config[K_PROXY]

  save(config)

  await dom.setValue(W_OUTPUT, "Config file updated!")


async def atkDelete(dom):
  if isDev():
    await dom.alert("You are in development environment, deleting config file is not possible!")
  elif await dom.confirm("Are you sure you want to delete config file ?"):
    delete()
    await dom.removeAttribute(W_TOKEN, "placeholder")
    await dom.setValues({W_TOKEN: "", "Id": ""})
    await dom.focus(W_TOKEN)
    await dom.setValue(W_OUTPUT, "Config deleted!")

