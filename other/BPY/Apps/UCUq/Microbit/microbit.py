import ucuq, atlastk

microbit = ucuq.Microbit()


async def atk(dom):
  dom.inner("", BODY)  # type: ignore # noqa: F821
  

async def atkSelect(dom, id):
  pos = int(dom.executeString(f'[...document.getElementById("LEDsOn").children].indexOf(document.getElementById("{id}"))'))
  
  x = pos // 5
  y = pos % 5
  
  microbit.setPixel(x, y, level :=  (0 if microbit.getPixel(x, y) else 9))
  
  await dom.setAttribute(id, "style", f"opacity: {0 if level == 0 else 1}")
  
  microbit.showText("Hello!")
