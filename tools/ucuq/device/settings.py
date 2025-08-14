import network, binascii, json

_SETTINGS_FILE = "ucuq.json"

_settingsOK = None

try:
  with open(_SETTINGS_FILE, "r") as settings:
    _SETTINGS = json.load(settings)
except:
  _settingsOK = False

_K_IDENTIFICATION = "Identification"
_K_WLAN = "WLAN"
_K_ONBOARD_LED = "OnBoardLed"
_K_PROXY = "Proxy"
_K_WIFI_POWER = "WifiPower"

_DEFAULT_ONBOARD_LED = (None, True)
_DEFAULT_PROXY = ("ucuq.q37.info", 53800, False)
_DEFAULT_WIFI_POWER = (8,)

getSettings = lambda key: _SETTINGS[key] if key in _SETTINGS else None

if _settingsOK != False:
  try:
    _IDENTIFICATION = _SETTINGS[_K_IDENTIFICATION]
    _ONBOARD_LED = getSettings(_K_ONBOARD_LED)
    _PROXY = getSettings(_K_PROXY)
    _WIFI_POWER = getSettings(_K_WIFI_POWER)
    _settingsOK = True
  except:
    _settingsOK = False


def _getMAC():
  wifi = network.WLAN(network.STA_IF)
  wifi.active(True)

  return binascii.hexlify(wifi.config('mac')).decode()


def getIdentificationToken():
  return _IDENTIFICATION[0]    
# NOTA: also used in remote script for 'getInfos()'… 


def getDeviceId():
  if isinstance(_IDENTIFICATION[1], str):
    return _IDENTIFICATION[1]
  else:
    if ( mac := _getMAC() ) in _IDENTIFICATION[1]:
      return _IDENTIFICATION[1][mac]
    else:
      return None
    

def _completeSettings(params, default):
  if params is None:
    return default  
  elif isinstance(params, (int, str, float)):
    return [params] + list(default[1:])  
  elif isinstance(params, (list, tuple)):
    return params + list(default[len(params):])
  else:
    return default


def _getSettings(settings, deviceId, default):
  if not isinstance(settings, (list, tuple)) or not all(isinstance(item, (list, tuple)) for item in settings):
    return _completeSettings(settings, default)
  else:
    for deviceId in (deviceId, "_default"):
      for devices in settings:
        if deviceId in devices[1]:
          return _completeSettings(devices[0], default)
    return default    
  

def available():
  return _settingsOK


def getWLANS():
  return _SETTINGS[_K_WLAN]


def getOnboardLed(deviceId):
  return _getSettings(_ONBOARD_LED, deviceId, _DEFAULT_ONBOARD_LED)


def getProxy(deviceId):
  return _getSettings(_PROXY, deviceId, _DEFAULT_PROXY) 


def getWifiPower(deviceId):
  return _getSettings(_WIFI_POWER, deviceId, _DEFAULT_WIFI_POWER)[0]

