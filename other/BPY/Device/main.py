import atlastk, ucuq, json

async def atkConnect(dom):
  infos = await ucuq.ATKConnectAwait(dom, BODY)
  await dom.setValue("Infos", json.dumps(infos, indent=2))
