import os, sys, json, ucuq

from PIL import Image
import base64
import io

import atlastk

class HW:
  def __init__(self, infos, device=None):
    self.device, self.tft = ucuq.getBits(infos, ucuq.B_TFT, device=device)

    if self.tft:
      pin, = ucuq.getHardware(infos, ucuq.B_TFT, ["Backlight"])
      ucuq.GPIO(pin, device=device).high()

  def __getattr__(self, methodName):
    def wrapper(*args, **kwargs):
      getattr(self.tft, methodName)(*args, **kwargs)
      return self
    return wrapper
  
  def sleep(self, delay = 0.75):
    self.device.sleep(delay)

  def draw(self, dataurl):
    self.tft.clear()
    header, base64_data = dataurl.split(',', 1)
    
    image_data = base64.b64decode(base64_data)
    
    image = Image.open(io.BytesIO(image_data))
    
    width, height = image.size
    
    rgb_image = image.convert('RGB')
    
    rgb565_bytes = bytearray()
    
    for y in range(height):
      for x in range(width):
        r, g, b = rgb_image.getpixel((x, y))
        r5 = (r >> 3) & 0x1F
        g6 = (g >> 2) & 0x3F
        b5 = (b >> 3) & 0x1F
        rgb565 = (r5 << 11) | (g6 << 5) | b5
        rgb565_bytes.append((rgb565 >> 8) & 0xFF)
        rgb565_bytes.append(rgb565 & 0xFF)
    
    self.tft.draw(io.BytesIO(bytes(rgb565_bytes)), width, height)


hw = None

async def atk(dom):
  global hw

  if not hw:
    hw = ucuq.Multi(HW(await ucuq.ATKConnectAwait(dom, BODY)))
  else:
    await dom.inner("", BODY)


async def atkSmile(dom, id):
  await dom.executeVoid("Go();allowCamera();")
  await dom.disableElements((id, "HidePhoto"))


async def atkShoot(dom):
  await dom.executeVoid("takePicture();")
  photo = await dom.getAttribute("photo", "src")
  hw.draw(photo)


async def atkTest(dom):
  test()


def dataurl_to_rgb565(dataurl):
  header, base64_data = dataurl.split(',', 1)
  
  image_data = base64.b64decode(base64_data)
  
  image = Image.open(io.BytesIO(image_data))
  
  width, height = image.size
  
  rgb_image = image.convert('RGB')
  
  rgb565_bytes = bytearray()
  
  for y in range(height):
    for x in range(width):
      r, g, b = rgb_image.getpixel((x, y))
      r5 = (r >> 3) & 0x1F
      g6 = (g >> 2) & 0x3F
      b5 = (b >> 3) & 0x1F
      rgb565 = (r5 << 11) | (g6 << 5) | b5
      rgb565_bytes.append((rgb565 >> 8) & 0xFF)
      rgb565_bytes.append(rgb565 & 0xFF)
  
  hw.draw(io.BytesIO(bytes(rgb565_bytes)), width, height)

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

  hw.poly(7, 120, 286, 30, (0, 64, 255), rotate=15, fill=False)
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
