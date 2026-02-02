import ucuq, base64, io, atlastk, json

class HW:
  def __init__(self, infos, device=None):
    self.device, self.tft = ucuq.getBits(infos, ucuq.B_TFT, device=device)

    if self.tft:
      pin, = ucuq.getHardware(infos, ucuq.B_TFT, ["Backlight"])
      ucuq.GPIO(pin, device=device).high()

  def __getattr__(self, methodName):
    def wrapper(*args, **kwargs):
      if methodName == "sleep":
        return self.sleep(*args, **kwargs)
      if methodName == "draw":
        return self.draw(*args, **kwargs)
      getattr(self.tft, methodName)(*args, **kwargs)
      return self
    return wrapper
  
  def sleep(self, delay = 0.75):
    self.device.sleep(delay)

  def draw(self, picture, width, height):
    self.tft.clear()
    
    with io.BytesIO(base64.b64decode(picture)) as stream:
      self.tft.draw(stream, width, height)


hw = None

async def atk(dom):
  global hw

  if not hw:
    hw = ucuq.Multi(HW(await ucuq.ATKConnectAwait(dom, BODY)))
  else:
    await dom.inner("", BODY)

  await dom.executeVoid("Go();")


async def atkSmile(dom, id):
  await dom.disableElement(id)
  await dom.executeVoid("allowCamera();")


async def atkCamera(dom, id):
  cameras = json.loads(base64.b64decode(id).decode('utf-8'))

  html = ""

  for camera in cameras:
    html += f'<option value="{camera["deviceId"]}">{camera["label"]}</option>'

  await dom.inner("cameras", html)
  await dom.executeVoid("document.getElementById('camera').showModal();")


async def atkCameraOk(dom):
  deviceId = await dom.getValue("cameras")
  if deviceId:
    await dom.executeVoid(f"launchCamera('{deviceId}');")
    await dom.disableElement("HidePhoto")
  else:
    await dom.enableElement("Smile")

  await dom.executeVoid("document.getElementById('camera').close();document.getElementById('camera').remove();")


async def atkCameraCancel(dom):
  await dom.executeVoid("document.getElementById('camera').close()")
  await dom.enableElement("Smile")


async def atkShoot(dom):
  # 'dom.executeStrings(…)' does not work with Google Chrome.
  # width, height, picture = await dom.executeStrings("takePicture();")

  # result = await dom.executeString("takePicture();")

  await dom.executeVoid("takePicture();")


async def atkDisplay(dom):
  result = ""

  while True:
    partial = await dom.executeString("getNextChunk(25000);")

    if not partial:
      break

    result += partial

  width, height, picture = result.split(',')
  hw.draw(picture, int(width), int(height))


async def atkTest(dom):
  test()

def test():
  hw.clear((0,0,255))
  hw.sleep()

  hw.clear()

  hw.hline(10, 309, 229, (255, 0, 255))
  hw.sleep()

  hw.vline(10, 0, 309, (0, 255, 255))
  hw.sleep()

  hw.rect(23, 50, 30, 75, (255, 255, 0))
  hw.sleep()

  hw.rect(23, 50, 75, 30, (0, 255, 255), fill=False)
  hw.sleep()

  hw.line(127, 0, 64, 127, (255, 0, 0))
  hw.sleep()

  coords = [[200, 163], [78, 80], [122, 92], [50, 50], [78, 15], [200, 163]]
  hw.lines(coords, (0, 255, 0))
  hw.sleep()

  hw.clear()

  hw.poly(5, 120, 286, 30, (0, 64, 255), rotate=15, fill=False)
  hw.sleep()

  hw.poly(9, 180, 186, 40, (255, 64, 0), rotate=15)
  hw.sleep()

  hw.clear()
  hw.circle(132, 132, 70, (0, 255, 0))
  hw.sleep()

  hw.circle(132, 96, 70, (0, 0, 255), fill=False)
  hw.sleep()

  hw.ellipse(96, 96, 30, 16, (255, 0, 0))
  hw.sleep()

  hw.ellipse(96, 256, 16, 30, (255, 255, 0), fill=False)
  hw.sleep()

  hw.text(100, 100, "Hello World!", (255, 255, 255), (0, 0, 0), rotate=90)

async def UCUqXDevice(dom, device):
  hw.add(HW(await ucuq.getInfosAwait(device), device))
