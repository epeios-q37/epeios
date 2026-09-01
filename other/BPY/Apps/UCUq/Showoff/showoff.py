import os  # noqa: I001
import time

import atlastk
import ucuq

import bouncing
import colors
import indy
import partner
import pink
from show import getDevices as getDevices_, countdownIfRequested as countdownIfRequested_, connect as connect_, syncTest as syncTest_
import trios


DELAY_ = 0.5

DEVICES_ = ("Alfa", "India", "Lima", "Golf")
SHOW_DEVICES_ = (DEVICES_[0], DEVICES_[2], DEVICES_[1])
"""
DEVICES_ = ("Papa", "Romeo", "Mike")
SHOW_DEVICES_ = DEVICES_
"""
HTML_OPTION_ = "<option>{}</option>"


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


def isPartnerWholeAnimationRequired_(dom):
#  return True
  return dom.getValue("PartnerFormat") == "true"


def atk(dom):
  devices = "\n".join(HTML_OPTION_.format(device) for device in combinaisons_(DEVICES_))
  
  dom.inner("", BODY.format(devices, DEVICES_[0], *SHOW_DEVICES_))  # type: ignore # noqa: F821
  partner.set(dom)
  trios.set(dom)
  dom.executeVoid("handleClearable();toggleFieldsetByLegend('Showoff', false);")


def atkPartnerConnect(dom):
  partner.connect(dom.getValue("PartnerDevice"))
  dom.executeVoid("toggleFieldsetByLegend('Partner', true)")


def atkPartnerBuzzer(dom):
  partner.Buzzer(isPartnerWholeAnimationRequired_(dom))
  
  
def atkPartnerOLEDGeo(dom):
  partner.OLEDGeo(isPartnerWholeAnimationRequired_(dom))
  
  
def atkPartnerOLEDMov(dom):
  partner.Mov(isPartnerWholeAnimationRequired_(dom))
  
  
def atkPartnerRing(dom):
  partner.Ring(isPartnerWholeAnimationRequired_(dom))


def atkPartnerLCD(dom):
  partner.LCD()


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
  devices = getDevices_()
  timestamp = countdownIfRequested_(dom, time.time() + DELAY_, devices)
  indy.launch(timestamp, devices)


def atkShowPink(dom):
  devices = getDevices_()
  timestamp = countdownIfRequested_(dom, time.time() + DELAY_, devices)
  pink.launch(timestamp, devices)


SHOWS_ = {
  "Colors": lambda timestamp, devices: colors.launch(timestamp, devices),
  "Bouncing": lambda timestamp, devices: bouncing.launch(timestamp, devices)
}


def atkShowPlay(dom):
  devices = getDevices_()
  show = dom.getValue("Show")
  timestamp = countdownIfRequested_(dom, time.time() + DELAY_, devices)
  if show in SHOWS_:
    SHOWS_[show](timestamp, devices)
  else:
    trios.launch(int(show), timestamp, devices)


def _atkShowColors(dom):
  devices = getDevices_()
  timestamp = countdownIfRequested_(dom, time.time() + DELAY_, devices)
  colors.launch(timestamp, devices)


if os.environ.get("PREFIX", "").startswith("/data/data/com.termux"):
  atlastk.set_supplier(lambda url: os.system(f'am start -n com.android.chrome/com.google.android.apps.chrome.Main -d "{url}"')) 
