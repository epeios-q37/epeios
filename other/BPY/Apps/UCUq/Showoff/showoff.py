import atlastk  # noqa: F401
import ucuq # pyright: ignore[reportMissingImports]
import time
import pink
import indy
import trio
import colors

import partner
import show

DEVICES_ = ("Alpha", "India", "Lima", "Golf")

HTML_OPTION_ = "<option>{}</option>"

def atk(dom):
  devices = "\n".join(HTML_OPTION_.format(device) for device in DEVICES_)
    
  dom.inner("", BODY.format(devices, DEVICES_[0], *DEVICES_[:3]))  # type: ignore # noqa: F821
  colors.fill(dom)
  colors.update(dom)
  
  
def atkPartnerConnect(dom):
  partner.connect(dom.getValue("Device"))
  
  
def atkPartnerLaunch(dom):
  if not partner.isConnected():
    partner.connect(dom.getValue("Device"))
    
  partner.launch(dom.getValue("PartnerSound") == "true")
  
  
def atkShowConnect(dom):
  show.connect(tuple(dom.getValues(("Device1", "Device2", "Device3")).values()))
  
  
def atkShowSync(dom):
  ucuq.ntpSetTime()
  
  
def atkShowTest():
  timestamp = time.time() + 1
  
  show.sleep(timestamp)
  
  show.devices.rgbs.flash()
  
  show.sleep(timestamp + 1)
  
  show.devices.rgbs.flash()
  
  
def atkShowIndy(dom):
  timestamp = show.countdownIfSelected(dom, time.time() + 1)
  indy.launch(timestamp)
  

def atkShowPink(dom):
  timestamp = show.countdownIfSelected(dom, time.time() + 1)
  pink.launch(timestamp)
  
  
def atkShowFugue(dom):
  timestamp = show.countdownIfSelected(dom, time.time() + 1)
  trio.launch(timestamp)


def atkShowColorUpdate(dom):
  colors.update(dom)


def atkShowColorOnce(dom):
  scheme, delay = dom.getValues((colors.W_SCHEMES, colors.W_DELAY)).values()
  timestamp = show.countdownIfSelected(dom, time.time() + 1)
  colors.launch(int(scheme), timestamp, float(delay), 1)
  
  
def atkShowColorRepeat(dom):
  scheme, delay, repeat = dom.getValues((colors.W_SCHEMES, colors.W_DELAY, colors.W_REPEAT)).values()
  timestamp = show.countdownIfSelected(dom, time.time() + 1)
  colors.launch(int(scheme), timestamp, float(delay), int(repeat))
