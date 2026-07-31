import time

import atlastk  # noqa: F401
import ucuq

import colors
import indy
import os
import partner
import pink
import show
import trio

DELAY = 0.5

DEVICES_ = ("Alfa", "India", "Lima", "Golf")
SHOW_DEVICES_ = (DEVICES_[0], DEVICES_[2], DEVICES_[1])

HTML_OPTION_ = "<option>{}</option>"


def combinaisons_(A):
  R = []
  n = len(A)
  for r in range(1, n + 1):
    def rec(start, prefix):
      if len(prefix) == r:
        R.append(" ".join(prefix))
        return
      for i in range(start, n):
        rec(i + 1, prefix + [A[i]])

    rec(0, [])
  return R


def isPartnerWholeAnimationRequired_(dom):
#  return True
  return dom.getValue("PartnerFormat") == "true"


def atk(dom):
  devices = "\n".join(HTML_OPTION_.format(device) for device in combinaisons_(DEVICES_))
  
  dom.inner("", BODY.format(devices, DEVICES_[0], *SHOW_DEVICES_))  # type: ignore # noqa: F821
  partner.set(dom)
  dom.executeVoid("handleClearable();toggleFieldsetByLegend('Showoff', false);")


def atkPartnerConnect(dom):
  partner.connect(dom.getValue("PartnerDevice"))
  dom.executeVoid("toggleFieldsetByLegend('Partner', true)")


def atkPartnerBuzzer(dom):
  partner.Buzzer(isPartnerWholeAnimationRequired_(dom))
  
  
def atkPartnerOLED(dom):
  partner.OLED(isPartnerWholeAnimationRequired_(dom))
  
  
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
  offset = show.connect(tuple(dom.getValues(("ShowLeftDevice", "ShowMiddleDevice", "ShowRightDevice")).values()))
  dom.executeVoid("toggleFieldsetByLegend('Show', true)")
  
  if abs(offset) >= .9:
    dom.alert(f"Décalage horaire : {offset} s !")


def atkShowSync(dom):
  ucuq.ntpSetTime()
  show.syncTest()


def atkShowTest():
  show.syncTest()  

def atkShowIndy(dom):
  devices = show.getDevices()
  timestamp = show.countdown(time.time() + DELAY, devices)
  indy.launch(timestamp, devices)


def atkShowPink(dom):
  devices = show.getDevices()
  timestamp = show.countdown(time.time() + DELAY, devices)
  pink.launch(timestamp, devices)


def atkShowFugue(dom):
  devices = show.getDevices()
  timestamp = show.countdown(time.time() + DELAY, devices)
  trio.launch(timestamp, devices)


def atkShowColors(dom):
  devices = show.getDevices()
  timestamp = show.countdown(time.time() + DELAY, devices)
  colors.launch(timestamp, devices)

if os.environ.get("PREFIX", "").startswith("/data/data/com.termux"):
  atlastk.set_supplier(lambda url: os.system(f'am start -n com.android.chrome/com.google.android.apps.chrome.Main -d "{url}"')) 
