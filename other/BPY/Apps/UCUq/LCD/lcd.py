import ucuq, atlastk, json

hw = None

class TrueLCD():
  def __init__(self, infos, device = None):
    self.nbRows = 2
    self.nbCols = 16
    self.device, self.lcd = ucuq.getBits(infos, "LCD", device = device)

  def put(self, lines):
    y = 0

    for line in lines.splitlines()[:self.nbRows]:
      self.lcd.moveTo(0, y)
      self.lcd.putString(line[:self.nbCols].ljust(self.nbCols))
      y += 1

  def backlightOn(self):
    self.lcd.backlightOn()


class SimulatedLCD():
  def __init__(self, dom):
    self.dom = dom

    dom.executeVoid("init()")

  def put(self, lines):
    command = f"displayLCD(`{json.dumps(lines).replace('\\','\\\\').replace('`','\`')}`);"
    print(command)
    self.dom.executeVoid(command)

  def backlightOn(self):
    pass


async def displayLCD(dom, lines):
  command = f"displayLCD(`{json.dumps(lines).replace('\\','\\\\').replace('`','\`')}`);"
  print(command)
  await dom.executeVoid(command)
  

async def atk(dom):
  global hw

  if not hw:
    hw = ucuq.Multi(TrueLCD(await ucuq.ATKConnectAwait(dom, BODY)))
  else:
    await dom.inner("", BODY)

  await dom.executeVoid("init();")


async def atkSubmit(dom):
  lines =  dom.getValue("lcdtext")
  hw.put(await lines)
  hw.backlightOn()

  await displayLCD(dom, lines)



