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

HTML_OPTION_ = "<option>{}</option>"

def atk(dom):
  devices = "\n".join(HTML_OPTION_.format(device) for device in DEVICES_)
    
  dom.inner("", BODY.format(devices, DEVICES_[0], *DEVICES_[:3]))  # type: ignore # noqa: F821
  colors.fill(dom)
  colors.update(dom)
  dom.executeVoid("handleClearable();toggleFieldsetByLegend('Showoff', false);")
  
  
def atkPartnerConnect(dom):
  partner.connect(dom.getValue("PartnerDevice"))
  dom.executeVoid("toggleFieldsetByLegend('Partner', true)")
  
  
def atkPartnerBuzzer(dom):
  partner.Buzzer()


def atkPartnerOLED(dom):
  partner.OLED()

  
def atkPartnerRing(dom):
  partner.Ring()

  
def atkPartnerLCD(dom):
  partner.LCD()


def atkPartnerListen(dom):
  partner.Listen(dom)
  

# Called by JS 'partnerListen' script (itself launched by above 'atkPartnerListen' callback)
def atkPartnerDisplaySpokenColor(dom):
  partner.DisplaySpokenColor(dom)


def atkPartnerIndy(dom):
  partner.indy()

  
def atkShowConnect(dom):
  show.connect(tuple(dom.getValues(("ShowLeftDevice", "ShowMiddleDevice", "ShowRightDevice")).values()))
  dom.executeVoid("toggleFieldsetByLegend('Show', true)")
  
  
def syncTest():
  timestamp = time.time() + 1.5
  
  show.sleepUntil(timestamp)
  
  show.devices.rings.flash()
  
  show.sleepUntil(timestamp + 1)
  
  show.devices.rings.flash()
  
  
def atkShowSync(dom):
  ucuq.ntpSetTime()
  syncTest()
  
def atkShowTest():
  syncTest()  
  
def atkShowIndy(dom):
  timestamp = show.countdownIfSelected(dom, time.time() + DELAY)
  indy.launch(timestamp)
  

def atkShowPink(dom):
  timestamp = show.countdownIfSelected(dom, time.time() + DELAY)
  pink.launch(timestamp)
  
  
def atkShowFugue(dom):
  timestamp = show.countdownIfSelected(dom, time.time() + DELAY)
  trio.launch(timestamp)


def atkShowColorUpdate(dom):
  colors.update(dom)


def atkShowColorOnce(dom):
  scheme, delay = dom.getValues((colors.W_SCHEMES, colors.W_DELAY)).values()
  timestamp = show.countdownIfSelected(dom, time.time() + DELAY)
  colors.launch(int(scheme), timestamp, float(delay), 1)
  
  
def atkShowColorRepeat(dom):
  scheme, delay, repeat = dom.getValues((colors.W_SCHEMES, colors.W_DELAY, colors.W_REPEAT)).values()
  timestamp = show.countdownIfSelected(dom, time.time() + DELAY)
  colors.launch(int(scheme), timestamp, float(delay), int(repeat))
  
if os.environ.get("PREFIX", "").startswith("/data/data/com.termux"):
  atlastk.set_supplier(lambda url: os.system(f'am start -n com.android.chrome/com.google.android.apps.chrome.Main -d "{url}"'))  
