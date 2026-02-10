import ucuq, atlastk

microbit = ucuq.Microbit()


async def atk(dom):
  dom.inner("", BODY)  # type: ignore # noqa: F821
  
  
async def clear(dom):
  microbit.clear()
  dom.executeVoid('clearMatrix()')
  

async def atkSelect(dom, id):
  pos = int(await dom.executeString(f'getPosition("{id}")'))
  
  x = pos // 5
  y = pos % 5
  
  microbit.setPixel(x, y, level :=  (0 if microbit.getPixel(x, y) else 9))
  
  await dom.setAttribute(id, "style", f"opacity: {0 if level == 0 else 1}")


async def atkSubmit(dom):
  await clear(dom)
  microbit.showText(await dom.getValue("Text"))
  
  

async def atkTest(dom):
  await clear(dom)
  dom.executeVoid('clearMatrix()')
  microbit.flash()
  
