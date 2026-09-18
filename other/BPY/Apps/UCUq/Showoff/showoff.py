import os  # noqa: I001
import time

import atlastk
import ucuq

import bouncing
import colors
import indy
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


def partnerLength_(dom):
  return int(dom.getValue("PartnerLength"))


def atk(dom):
  devices = "\n".join(HTML_OPTION_.format(device) for device in combinaisons_(DEVICES_))
  
  dom.inner("", BODY.format(devices, DEVICES_[0], *SHOW_DEVICES_))  # type: ignore # noqa: F821
  partner.set(dom)
  trios.set(dom)
  qrcodes.set(dom)
  dom.executeVoid("handleClearable();toggleFieldsetByLegend('Showoff', false);toggleFieldsetByLegend('QR Codes', true);")


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
