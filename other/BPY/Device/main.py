import atlastk, ucuq, json

async def acConnect(dom):
  infos = await ucuq.ATKConnectAwait(dom, BODY)
  await dom.setValue("Infos", json.dumps(infos, indent=2))

CALLBACKS = {
  "": acConnect
}
