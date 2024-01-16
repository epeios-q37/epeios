import atlastk, html, re

"""
From here and up to and including the 'acConnect' function,
to simplify the writing of the program, there are a lot of quirks
which should not be used in regular applications.
"""

def clean(s):
  return re.sub(' id="_CGN.*?"', '', s).strip(" \n").replace ("    <", "<").replace("xdh:widget_", "xdh:widget")


async def displayCode(dom, element):
  source = await dom.executeString(f"getOrGenerateId(getElement('{element}').firstElementChild.nextElementSibling);")
  code = clean(await dom.getValue(source))
  target = await dom.executeString(f"getOrGenerateId(getElement('{source}').nextElementSibling.nextElementSibling.firstElementChild.nextElementSibling.firstElementChild.nextElementSibling);")
  await dom.setValue(target, html.escape(code))


async def acConnect(dom):
  await dom.inner("", open("Main.html").read())
  last = await dom.nextSibling(await dom.nextSibling(await dom.firstChild("")))
  current = await dom.lastChild(await dom.parent(last))

  while True:
    widget = await dom.getAttribute(current, "id")
    await dom.setValue("RetrievedWidget", widget)
    displayCode(dom,current)
    await dom.removeClass(widget, "hidden")
    if current == last:
      break
    current = await dom.previousSibling(current)

  await dom.executeVoid("document.querySelectorAll('pre').forEach((block) => {hljs.highlightBlock(block);});")

  await dom.addClass("Retrieving", "hidden")

  await dom.setAttribute("ckInput", "xdh:widget", await dom.getAttribute("ckInput", "xdh:widget_"))
  await dom.after("ckInput", "")


def dlShape(flavors):
  html = atlastk.create_HTML()

  for flavor in flavors:
    html.pushTag("option")
    html.putAttribute("value", flavor)
    html.popTag()

  return html

dlFlavors = ["Vanilla", "Chocolate", "Caramel", "Mint"]  


async def acDlSubmit(dom, id):
  global dlFlavors

  flavor = await dom.getValue(id)
  await dom.setValue(id, "")
  if flavor not in dlFlavors:
    dlFlavors.append(flavor)
    dlFlavors.sort()
    await dom.inner("dlFlavors", dlShape(dlFlavors))
  await dom.setValue("dlOutput", flavor)


async def acRgSubmit(dom, id):
  value = await dom.getValue(id)

  await dom.setValues({
    "rgRange": value,
    "rgNumber": value,
    "rgMeter": value
  })


def slEmbed(other):
  html = atlastk.createHTML()

  html.pushTag("option")
  html.putAttribute("selected", "selected")
  html.putValue(other)

  return html


async def acSlAdd(dom):
  await dom.begin("slOthers", slEmbed(await dom.getValue("slInput")))
  await dom.setValue("slInput", "")
  await dom.focus("slInput")  


CALLBACKS = {
  "": acConnect,

  "btSubmit": lambda dom: dom.alert("Click on button detected!"),

  "pwSubmit": lambda dom, id: dom.setValue("pwOutput", dom.getValue(id)),

  "cbSelect": lambda dom, id: dom.setValue("cbOutput", "{} ({})".format(id, dom.getValue(id))),
  "cbSubmit": lambda dom: dom.alert(str(dom.getValues(["cbBicycle", "cbCar", "cbPirogue"]))),

  "rdCheck": lambda dom, id: dom.setValue("rdSelect", dom.getValue(id)),
  "rdSelect": lambda dom, id: dom.setValue("rdRadios", dom.getValue(id)),
  "rdReset": lambda dom: dom.setValues({"rdSelect": "None", "rdRadios": ""}),

  "dlSubmit": acDlSubmit,

  "dtSelect": lambda dom, id: dom.setValue("dtOutput", dom.getValue(id)),

  "clSelect": lambda dom, id: dom.setValue("clOutput", dom.getValue(id)),

  "rgSubmit": acRgSubmit,

  "slSelect": lambda dom, id: dom.setValue("slOutput", dom.getValue(id)),
  "slAdd": acSlAdd,
  "slToggle": lambda dom, id: dom.disableElement("slOthers") if dom.getValue(id) == 'true' else dom.enableElement("slOthers"),
  "slRadio": lambda dom: dom.scrollTo("radio"),

  "ckSubmit": lambda dom, id: dom.setValue("ckOutput", dom.getValue("ckInput")),
}


atlastk.launch(CALLBACKS, None, open("Head.html").read())
