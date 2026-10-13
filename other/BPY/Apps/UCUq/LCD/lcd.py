import json

import atlastk
import ucuq

hw = None

class TrueLCD:
  def __init__(self, infos, device = None):
    self.nbRows = 2
    self.nbCols = 16
    self.device, self.lcd = ucuq.getBits(infos, "LCD", device = device)

  def put(self, lines):
    y = 0

    for y, line in enumerate(lines):
      self.lcd.moveTo(0, y)
      self.lcd.putString(line[:self.nbCols].ljust(self.nbCols))

    return self

  def backlightOn(self):
    self.lcd.backlightOn()

    return self


async def atk(dom):
  global hw

  if not hw:
    hw = ucuq.Multi(TrueLCD(await ucuq.ATKConnectAwait(dom, BODY))).backlightOn()
  else:
    await dom.inner("", BODY)

  await dom.executeVoid("init();")


async def atkUpdateAll(dom, id):
  lines = json.loads(id)
  hw.put(lines).backlightOn()
  lines = [line.replace('"','\\\"') for line in lines]
  await dom.executeVoid(f'renderLCD(["{lines[0]}","{lines[1]}"])')


async def atkUpdate(dom):
  atlastk.broadcastAction(atkUpdateAll, json.dumps(list((await dom.getValues(("Line1", "Line2"))).values())))
