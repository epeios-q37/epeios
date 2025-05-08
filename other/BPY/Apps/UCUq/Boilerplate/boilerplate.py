import ucuq, atlastk

async def atk(dom):
  global pin, level
  
  pin, level = ucuq.getKitHardware(await ucuq.ATKConnectAwait(dom, BODY))["OnBoardLed"]

  ucuq.GPIO(pin).high(not(level))
  
async def atkSwitch(dom, id):
  ucuq.GPIO(pin).high( (await dom.getValue(id) == "true") == level)
