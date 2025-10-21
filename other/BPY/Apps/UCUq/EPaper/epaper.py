import atlastk, ucuq, datetime, json

epaper = None

W_QRC_TEXT = "QRCText"

W_TXT_TEXT = "TXTText"
W_TXT_WIDTH = "TXTWidth"
W_TXT_X = "TXTX"
W_TXT_Y = "TXTY"
W_TXT_FONT_SIZE = "TXTFontSize"
W_TXT_FONT = "TXTFont"
W_TXT_CENTER_X = "TXTCenterX"
W_TXT_CENTER_Y = "TXTCenterY"
W_TXT_CANVAS = "TXTCanvas"

async def txtUpdate(dom):
  text, x, y, width, font, fontSize, centerX, centerY = (await dom.getValues((W_TXT_TEXT, W_TXT_X, W_TXT_Y, W_TXT_WIDTH, W_TXT_FONT, W_TXT_FONT_SIZE, W_TXT_CENTER_X, W_TXT_CENTER_Y))).values()

  coords = json.loads(await dom.executeString(f"JSON.stringify(createTextCanvas('{W_TXT_CANVAS}','{text}', {x}, {y}, {width}, \"{font}\", {fontSize}, {centerX}, {centerY}));"))

  values = {W_TXT_X: coords['x'], W_TXT_Y: coords['y']}

  if centerX != "true":
    del values[W_TXT_X]
    
  if centerY != "true":
    del values[W_TXT_Y]

  if values:
    await dom.setValues(values)


async def atk(dom):
  global epaper

  await ucuq.ATKConnectAwait(dom, BODY)

  epaper = ucuq.SSD1680_SPI(7, 1, 2, 3, ucuq.SPI(1, baudrate=2000000, polarity=0, phase=0, sck=4, mosi=6))
  # epaper = ucuq.SSD1680_SPI( cs=45, dc=46, rst=47, busy=48, spi=ucuq.SPI(1, baudrate=2000000, polarity=0, phase=0, sck=12, mosi=11)  )
  epaper.fill(0).hText("E-paper ready !", 50).hText(datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"), 75).show()

  await dom.focus(W_QRC_TEXT)
  await txtUpdate(dom)


# Called from JS!
async def atkDisplay(dom, data):
  image = json.loads(data)
  
  epaper.fill(0).draw(image["pattern"], width = image['width'], ox = image['offsetX'], oy = image['offsetY'], mul = image['mul']).show()


async def atkQRCSubmit(dom):
  await dom.executeVoid(f"QRCodeLaunch('{await dom.getValue(W_QRC_TEXT)}')")
  await dom.focus(W_QRC_TEXT)


async def atkQRCClear(dom):
  await dom.setValue(W_QRC_TEXT, "")
  await dom.focus(W_QRC_TEXT)


async def atkTXTUpdate(dom):
  await txtUpdate(dom)


async def atkTXTSubmit(dom):
  text, x, y, width, font, fontSize, centerX, centerY = (await dom.getValues((W_TXT_TEXT, W_TXT_X, W_TXT_Y, W_TXT_WIDTH, W_TXT_FONT, W_TXT_FONT_SIZE, W_TXT_CENTER_X, W_TXT_CENTER_Y))).values()

  await dom.executeVoid(f"displayText('{W_TXT_CANVAS}','{text}', {x}, {y}, {width}, \"{font}\", {fontSize}, {centerX}, {centerY})")


async def atkTXTClear(dom):
  await dom.setValue(W_TXT_TEXT, "")


async def atkTXTCenterX(dom, id):
  if ( ( await dom.getValue(id) ) == "true"):
    await dom.disableElement(W_TXT_X)
    await txtUpdate(dom)
  else:
    await dom.enableElement(W_TXT_X)


async def atkTXTCenterY(dom, id):
  if ( ( await dom.getValue(id) ) == "true"):
    await dom.disableElement(W_TXT_Y)
    await txtUpdate(dom)
  else:
    await dom.enableElement(W_TXT_Y)


async def atkReset(dom, id):
  global epaper
  epaper = ucuq.SSD1680_SPI(7, 1, 2, 3, ucuq.SPI(1, baudrate=2000000, polarity=0, phase=0, sck=4, mosi=6)).fill(0).show()
#  ucuq.SSD1680_SPI(cs=45, dc=46, rst=47, busy=48,spi=ucuq.SPI(1,baudrate=2000000, polarity=0, phase=0, sck=12, mosi=11)).fill(0).show()
