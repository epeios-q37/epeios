import os  # noqa: I001
import time

import atlastk
import ucuq

import bouncing
import colors
import devices
from devices import *
import indy
import canon
import life
import partner
import pink
import qrcodes
import show
import threading
import trios

from show import (
  getParts as getParts_,
  countdownIfRequested as countdownIfRequested_,
  connect as connect_,
  syncTest as syncTest_
)

DELAY_ = 0.5

W_SHOW_SUSPEND_RESTART_BUTTON = "ShowSuspendRestart"
W_SHOW_CONTROL_GROUP = "ShowControl"

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


def _enableShowControl(dom, state):
  dom.executeVoid(f"toggleFieldsetByLegend('Control', {'true' if state else 'false'})")


def atk(dom):
  availableDevices = devices.getDevices()
  
  dom.inner("", BODY.format(availableDevices[0] if len(availableDevices) else "", *(availableDevices[:3] if len(availableDevices) >= 3 else [""] * 3))) # type: ignore
  partner.set(dom)
  trios.set(dom)
  qrcodes.set(dom)
  dom.executeVoid("handleClearable();toggleFieldsetByLegend('Showoff', false);toggleFieldsetByLegend('QR Codes', true);")
  _enableShowControl(dom, False)


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
      offset = connect_(tuple(dom.getValues(show.SHOW_SITES_INPUT).values()))
    except RuntimeError as e:
      dom.alert(f"RuntimeError: {e!s}")
      cont = True

  dom.executeVoid("toggleFieldsetByLegend('Show', true)")
  _enableShowControl(dom, False)
  
  if abs(offset) >= .9:
    dom.alert(f"Décalage horaire : {offset} s !")


def atkShowSyncAdjust(dom):
  ucuq.ntpSync()
  syncTest_()


def atkShowSyncTest():
  syncTest_()  


def atkShowIndy(dom):
  parts = getParts_()
  timestamp = countdownIfRequested_(dom, show.getNtpTime() + DELAY_, parts)
  indy.launch(timestamp, parts)


def atkShowPink(dom):
  parts = getParts_()
  timestamp = countdownIfRequested_(dom, show.getNtpTime() + DELAY_, parts)
  pink.launch(timestamp, parts)


SHOWS_ = {
  "Colors": lambda timestamp, parts: colors.launch(timestamp, parts),
  "Bouncing": lambda timestamp, parts: bouncing.launch(timestamp, parts),
  "Indy":  lambda timestamp, parts: indy.launch(timestamp, parts),
  "Pink":  lambda timestamp, parts: pink.launch(timestamp, parts),
  "Life":  lambda timestamp, parts: life.launch(timestamp, parts),
  "Canon":  lambda timestamp, parts: canon.launch(timestamp, parts),
}


def atkbDisableShowControl(dom):
  _enableShowControl(dom, False)


def _launchTrio( showId, timestamp, parts):
  trios.launch(showId, timestamp, parts)
  atlastk.broadcastAction(atkbDisableShowControl)


def atkShowPlay(dom):
  parts = getParts_()
  showId = dom.getValue("Show")
  show.setState(show.State.STOP)
  timestamp = countdownIfRequested_(dom, show.getNtpTime() + DELAY_, parts)
  if showId in SHOWS_:
    threading.Thread(target=SHOWS_[showId], args=(timestamp, parts)).start()
  else:
    threading.Thread(target=_launchTrio, args=(showId, timestamp, parts)).start()
    _enableShowControl(dom, True)


def atkShowDisableControl(dom):
  show.setState(show.State.DISABLE)
  _enableShowControl(dom, False)


def atkShowStop(dom):
  show.setState(show.State.STOP)


def atkShowSuspendRestart(dom, id):
  show.toggleSuspendRestart(lambda: (show.getParts().buzzers.off(), ucuq.commit()))


def atkQRCodesSelect(dom, id):
  dom.setValue("QRCodesText", dom.getValue(id))


def atkQRCodesDisplay(dom):
  dom.executeVoid(f"window.open('http://api.qrserver.com/v1/create-qr-code/?data={dom.getValue('QRCodesText')}', '_blank')")


if os.environ.get("PREFIX", "").startswith("/data/data/com.termux"):
  atlastk.set_supplier(lambda url: os.system(f'am start -n com.android.chrome/com.google.android.apps.chrome.Main -d "{url}"'))

