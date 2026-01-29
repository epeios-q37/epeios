import ucuq, atlastk

async def atk(dom):
  await ucuq.ATKConnectAwait(dom, BODY)
  ucuq.GPIO(8).high()
  
async def atkSwitch(dom, id):
  ucuq.GPIO(8).high(await dom.getValue(id) != "true")
