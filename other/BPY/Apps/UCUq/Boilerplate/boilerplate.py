import ucuq, atlastk

async def atk(dom):
  await ucuq.ATKConnectAwait(dom, BODY)
  ucuq.GPIO(2).low()
  
async def atkSwitch(dom, id):
  ucuq.GPIO(2).high(await dom.getValue(id) == "true")
