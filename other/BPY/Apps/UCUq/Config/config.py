import os, sys, json

import atlastk

# Languages
L_FR = 0
L_EN = 1

ATK_L10N = (
  (
    "en",
    "fr"
  ),
  (
    "Show/hide proxy settings",
    "Afficher/Masquer réglages proxy"
  ),
  (
    "Save",
    "Sauver"
  ),
  (
    "Delete",
    "Effacer"
  ),
  (
    "Enter <em>Token</em> and/or <em>Id</em>",
    "Saisir <em>Token</em> et/ou <em>Id</em>."
  ),
  (
    "Please enter a value for <em>Token</em>!",
    "Veuillez saisir une value pour <em>Token</em> !"
  ),
  (
    "Please enter a value for <em>Port</em>!",
    "Veuillez saisir une value pour <em>Port</em> !"
  ),
  (
    "Please enter a value for <em>Host</em>!",
    "Veuillez saisir une value pour <em>Host</em> !"
  ),
  (
    "Config file updated!",
    "Fichier de configuration mis à jour !"
  ),
  (
    "Deleting config file is not possible in development mode!",
    "Effacer le fichier de configuration n'est pas possible en mode développement !"
  ),
  (
    "Are you sure you want to delete config file?",
    "Êtes-vous sûr de vouloir supprimer le fichier de configuration ?"
  ),
  (
    "Config file deleted!",
    "Fichier de configuration supprimé !"
  )
)

def isDev():
  return atlastk.isDev()

# BEGIN BRY
from browser.local_storage import storage

CONFIG_ITEM = "ucuq-config"

def getConfig():
  if CONFIG_ITEM in storage:
    return json.loads(storage[CONFIG_ITEM])
  else:
    return {
      K_DEVICE: {},
      K_PROXY: {
        K_PROXY_HOST: DEFAULT_PROXY_HOST,
        K_PROXY_PORT: DEFAULT_PROXY_PORT,
        K_PROXY_SSL: DEFAULT_PROXY_SSL
      }
    }
  

def save(config):
  storage[CONFIG_ITEM] = json.dumps(config, indent=2)


def delete():
  del storage[CONFIG_ITEM]
# END BRY

# BEGIN PYH
CONFIG_FILE = ( "/home/csimon/q37/epeios/other/BPY/Apps/UCUq/" if isDev() else "../" ) + "ucuq.json"


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

DEFAULT_PROXY_HOST = "ucuq.q37.info"
DEFAULT_PROXY_PORT = "53843"
DEFAULT_PROXY_SSL = True

# Keys
K_DEVICE = "Device"
K_DEVICE_TOKEN = "Token"
K_DEVICE_ID = "Id"
K_PROXY = "Proxy"
K_PROXY_HOST = "Host"
K_PROXY_PORT = "Port"
K_PROXY_SSL = "SSL"

# Widgets
W_PROXY = "Proxy"
W_HOST = "Host"
W_PORT = "Port"
W_SSL = "SSL"
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

  proxyConfig = getConfigProxy()

  if K_PROXY_HOST in proxyConfig:
    values[W_HOST] = proxyConfig[K_PROXY_HOST]
  else:
    await setAsHidden(dom, W_HOST)

  if K_PROXY_PORT in proxyConfig:
    values[W_PORT] = proxyConfig[K_PROXY_PORT]
  else:
    await setAsHidden(dom, W_PORT)

  if K_PROXY_SSL in proxyConfig:
    values[W_SSL] = "true" if proxyConfig[K_PROXY_SSL] else "false"

  device = getConfigDevice()

  if K_DEVICE_TOKEN in device:
    await setAsHidden(dom, W_TOKEN)

  if K_DEVICE_ID in device:
    values[W_ID] = device[K_DEVICE_ID]

  if values:
    await dom.setValues(values)

  await dom.focus(W_TOKEN if not K_DEVICE_TOKEN in device else W_ID)


async def atk(dom):
  await dom.inner("", BODY.format(**dom.getL10n(proxy=1, save=2, delete=3, hint=4)))

# BEGIN PYH
  dom.disableElement(S_HIDE_PROXY)
# END PYH

  await updateUI(dom)


async def atkSave(dom):
  host, port, ssl, token, id = (value.strip() for value in (await dom.getValues([W_HOST, W_PORT, W_SSL, W_TOKEN, W_ID])).values())

  ssl = True if ssl == "true" else False

  device = getConfigDevice()

  if not token and K_DEVICE_TOKEN not in device:
    await dom.alert(dom.getL10n(5))
    await dom.focus(W_TOKEN)
    return

  if token:
    device[K_DEVICE_TOKEN] = token

  if id:
    device[K_DEVICE_ID] = id

  proxyConfig = getConfigProxy()

  if not host and not port:
    proxyConfig = None
  else:
    if host:
      if not port:
        await dom.alert(dom.getL10N(6))
        await dom.focus(W_PORT)
        return
    elif port:
      if not host:
        await dom.alert(dom.getL10n(7))
        await dom.focus(W_HOST)
        return

    proxyConfig[K_PROXY_HOST] = host
    proxyConfig[K_PROXY_PORT] = port
    proxyConfig[K_PROXY_SSL] = ssl
    
  config = getConfig()

  config[K_DEVICE] = device

  if proxyConfig:
    config[K_PROXY] = proxyConfig
  elif K_PROXY in config:
    del config[K_PROXY]

  save(config)

  await dom.setValue(W_OUTPUT, dom.getL10n(8))


async def atkDelete(dom):
  if isDev():
    await dom.alert(dom.getL10n(9))
  elif await dom.confirm(dom.getL10n(10)):
    delete()
    await dom.removeAttribute(W_TOKEN, "placeholder")
    await dom.setValues({W_TOKEN: "", "Id": ""})
    await dom.focus(W_TOKEN)
    await dom.setValue(W_OUTPUT, dom.getL10n(11))

