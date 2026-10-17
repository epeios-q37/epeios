import os  # noqa: I001
import time

import atlastk
import ucuq

import bouncing
import colors
import indy
import json
import canon
import life
import partner
import pink
import qrcodes
from show import (
  getParts as getParts_,
  countdownIfRequested as countdownIfRequested_,
  connect as connect_,
  syncTest as syncTest_
)
import subprocess
import trios


DELAY_ = 0.5

DEVICES_ = ("Alfa", "Lima", "India", "Golf")
SHOW_DEVICES_ = (DEVICES_[0], DEVICES_[2], DEVICES_[1])
"""
DEVICES_ = ("Papa", "Romeo", "Mike")
SHOW_DEVICES_ = DEVICES_
"""
HTML_OPTION_ = "<option>{}</option>"

_devices = None


def combinaisons_(A):
  R = []
  n = len(A)
  for r in range(1, n + 1):
    def rec(start, prefix, targetLen):
      if len(prefix) == targetLen:
        R.append(" ".join(prefix))
        return
      for i in range(start, n):
        rec(i + 1, prefix + [A[i]], targetLen)

    rec(0, [], r)
  return R


def _getDevices():
  global _devices

  _devices = json.loads(subprocess.run(("ucuqm", "--fetch", "--json"), capture_output=True, check=True).stdout)["Ids"]

  return _devices


def _closeDevices():
  subprocess.run(("ucuqm", "--close"), check=False)


def partnerLength_(dom):
  return int(dom.getValue("PartnerLength"))


def atk(dom):
  devices = "\n".join(HTML_OPTION_.format(device) for device in combinaisons_(DEVICES_))
  
  dom.inner("", BODY.format(devices, _devices[0] if len(_getDevices()) else "", *SHOW_DEVICES_))  # type: ignore # noqa: F821
  partner.set(dom)
  trios.set(dom)
  qrcodes.set(dom)
  dom.executeVoid("handleClearable();toggleFieldsetByLegend('Showoff', false);toggleFieldsetByLegend('QR Codes', true);")


def _getPartnerDevicesDialog():
  return "document.getElementById('PartnerDevices')"


def _fillPartnerDevices(dom):
  html = "<div style='display: flex; flex-direction: column;'>"

  devices = dom.getValue("PartnerDevice").split()

  for index, device in enumerate(_getDevices()):
    html += f"<label style='display: flex; justify-content: space-between'><span>{device}: </span><input id='PartnerDevice{index}' type='checkbox' {"checked" if device in devices else ""}></input></label>"
  html += "</div>"

  dom.setValue("PartnerDevicesList", html)


def atkPartnerDevicesOK(dom):
  dom.executeVoid(f"{_getPartnerDevicesDialog()}.close()")

  ids = [f"PartnerDevice{index}" for index in range(len(_devices))]

  dom.setValue("PartnerDevice", " ".join([_devices[int(k[13:])] for k, v in dom.getValues(ids).items() if v == "true"]))


def atkPartnerDevicesCancel(dom):
  dom.executeVoid(f"{_getPartnerDevicesDialog()}.close()")


def atkPartnerDevicesRefresh(dom):
  dom.setValue("PartnerDevicesList", "")
  _fillPartnerDevices(dom)


def atkPartnerDevicesClose(dom):
  _closeDevices()
  dom.setValue("PartnerDevicesList", "")


def atkPartnerSelect(dom):
  with open("PartnerDevices.html") as dialog:
    dom.inner("PartnerDevices", dialog.read())
    dom.executeVoid(f"{_getPartnerDevicesDialog()}.showModal();")

  _fillPartnerDevices(dom)

def atkPartnerConnect(dom):
  partner.connect(dom.getValue("PartnerDevice"))
  dom.executeVoid("toggleFieldsetByLegend('Partner', true)")


def atkPartnerBuzzer(dom):
  partner.Buzzer(partnerLength_(dom))
  
  
def atkPartnerScreenGeo(dom):
  partner.screenGeo(partnerLength_(dom))
  
  
def atkPartnerScreenMov(dom):
  partner.screenMov(partnerLength_(dom))
  
  
def atkPartnerRing(dom):
  partner.Ring(partnerLength_(dom))


def atkPartnerPanel(dom):
  partner.Panel(partnerLength_(dom))


def atkPartnerServos(dom):
  partner.Servos()


def atkPartnerListen(dom):
  partner.Listen(dom)


# Called by JS script
def atkPartnerDisplaySpokenColor(dom):
  partner.DisplaySpokenColor(dom)
  
  
# Called by JS script
def atkPartnerDisplayOrientation(dom, id):
  partner.DisplayOrientation(dom, id)


def atkPartnerIndy(dom):
  partner.indy()


def atkPartnerMatrix(dom):
  partner.matrixSimulation()


def _getShowDevicesDialog():
  return "document.getElementById('ShowDevices')"


def _fillShowDevices(dom):
  html = "<div style='display: flex; flex-direction: column;'>"

  for index, device in enumerate(_getDevices()):
    html += f"""
  <div style='display: flex; justify-content: space-between;>
    <label style='display: flex; justify-content: space-between'>{device}: </label>
    <span xdh:radio='ShowDevice{index}' id='ShowDevice{index}'>
      <input name="ShowDevice{index}" value='Left' type='radio'></input>
      <input name="ShowDevice{index}" value='Middle' type='radio'></input>
      <input name="ShowDevice{index}" value='Right' type='radio'></input>
      <button>x</button>
    </span>
  </div>
"""

  html += "</div>"

  dom.setValue("ShowDevicesList", html)


def atkShowDevicesOK(dom):
  dom.executeVoid(f"{_getShowDevicesDialog()}.close()")

  ids = dom.getValues([f"ShowDevice{index}" for index in range(len(_devices))])

  values = {
    "ShowLeftDevice": " ".join([_devices[int(key[10:])] for key, valeur in ids.items() if valeur == "Left"]),
    "ShowMiddleDevice": " ".join([_devices[int(key[10:])] for key, valeur in ids.items() if valeur == "Middle"]),
    "ShowRightDevice": " ".join([_devices[int(key[10:])] for key, valeur in ids.items() if valeur == "Right"]),
  }

  dom.setValues(values)


def atkShowDevicesCancel(dom):
  dom.executeVoid(f"{_getShowDevicesDialog()}.close()")


def atkShowDevicesRefresh(dom):
  dom.setValue("ShowDevicesList", "")
  _fillShowDevices(dom)


def atkShowDevicesClose(dom):
  _closeDevices()
  dom.setValue("ShowDevicesList", "")


def atkShowSelect(dom):
  with open("ShowDevices.html") as dialog:
    dom.inner("ShowDevices", dialog.read())
    dom.executeVoid(f"{_getShowDevicesDialog()}.showModal();")

  _fillShowDevices(dom)


def atkShowConnect(dom):
  cont = True

  while cont:
    cont = False
    try:
      offset = connect_(tuple(dom.getValues(("ShowLeftDevice", "ShowMiddleDevice", "ShowRightDevice")).values()))
    except RuntimeError as e:
      dom.alert(f"RuntimeError: {e!s}")
      cont = True

  dom.executeVoid("toggleFieldsetByLegend('Show', true)")
  
  if abs(offset) >= .9:
    dom.alert(f"Décalage horaire : {offset} s !")


def atkShowSync(dom):
  ucuq.ntpSync()
  syncTest_()


def atkShowTest():
  syncTest_()  


def atkShowIndy(dom):
  parts = getParts_()
  timestamp = countdownIfRequested_(dom, time.time() + DELAY_, parts)
  indy.launch(timestamp, parts)


def atkShowPink(dom):
  parts = getParts_()
  timestamp = countdownIfRequested_(dom, time.time() + DELAY_, parts)
  pink.launch(timestamp, parts)


SHOWS_ = {
  "Colors": lambda timestamp, parts: colors.launch(timestamp, parts),
  "Bouncing": lambda timestamp, parts: bouncing.launch(timestamp, parts),
  "Indy":  lambda timestamp, parts: indy.launch(timestamp, parts),
  "Pink":  lambda timestamp, parts: pink.launch(timestamp, parts),
  "Life":  lambda timestamp, parts: life.launch(timestamp, parts),
  "Canon":  lambda timestamp, parts: canon.launch(timestamp, parts),
}


def atkShowPlay(dom):
  parts = getParts_()
  show = dom.getValue("Show")
  timestamp = countdownIfRequested_(dom, time.time() + DELAY_, parts)
  if show in SHOWS_:
    SHOWS_[show](timestamp, parts)
  else:
    trios.launch(int(show), timestamp, parts)


def atkQRCodesSelect(dom, id):
  dom.setValue("QRCodesText", dom.getValue(id))


def atkQRCodesDisplay(dom):
  dom.executeVoid(f"window.open('http://api.qrserver.com/v1/create-qr-code/?data={dom.getValue('QRCodesText')}', '_blank')")


if os.environ.get("PREFIX", "").startswith("/data/data/com.termux"):
  atlastk.set_supplier(lambda url: os.system(f'am start -n com.android.chrome/com.google.android.apps.chrome.Main -d "{url}"')) 
