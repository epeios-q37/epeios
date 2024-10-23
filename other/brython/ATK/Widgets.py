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
  await dom.inner("", BODY)
  last = await dom.nextSibling(await dom.nextSibling(await dom.firstChild("")))
  current = await dom.lastChild(await dom.parent(last))

  while True:
    widget = await dom.getAttribute(current, "id")
    await dom.setValue("RetrievedWidget", widget)
    await displayCode(dom,current)
    await dom.removeClass(widget, "hidden")
    if current == last:
      break
    current = await dom.previousSibling(current)

  await dom.executeVoid("document.querySelectorAll('pre').forEach((block) => {hljs.highlightBlock(block);});")

  await dom.addClass("Retrieving", "hidden")

  await dom.setAttribute("ckInput", "xdh:widget", await dom.getAttribute("ckInput", "xdh:widget_"))
  await dom.after("ckInput", "")


def dlShape(flavors):
  html = atlastk.createHTML()

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


async def acBtSubmit(dom):
  await dom.alert("Click on button detected!")


async def acPwSubmit(dom, id):
  await dom.setValue("pwOutput", await dom.getValue(id))


async def acCbSelect(dom, id):
  await dom.setValue("cbOutput", "{} ({})".format(id, await dom.getValue(id)))


async def acCbSubmit(dom):
  await dom.alert(str(await dom.getValues(["cbBicycle", "cbCar", "cbPirogue"])))


async def acRdCheck(dom,id):
  await dom.setValue("rdSelect", await dom.getValue(id))


async def acRdSelect(dom, id):
  await dom.setValue("rdRadios", await dom.getValue(id))


async def acRdReset(dom):
  await dom.setValues({"rdSelect": "None", "rdRadios": ""})


async def acDtSelect(dom, id):
  await dom.setValue("dtOutput", await dom.getValue(id))


async def acClSelect(dom, id):
  await dom.setValue("clOutput", await dom.getValue(id))


async def acSlSelect(dom, id):
  await dom.setValue("slOutput", await dom.getValue(id))


async def acSlToggle(dom, id):
  await dom.disableElement("slOthers") if (await dom.getValue(id)) == 'true' else await dom.enableElement("slOthers")


async def acSlRadio(dom):
  await dom.scrollTo("radio")


async def acCkSubmit(dom, id):
  await dom.setValue("ckOutput", await dom.getValue("ckInput"))


CALLBACKS = {
  "": acConnect,

  "btSubmit": acBtSubmit,

  "pwSubmit": acPwSubmit,

  "cbSelect": acCbSelect,
  "cbSubmit": acCbSubmit,

  "rdCheck": acRdCheck,
  "rdSelect": acRdSelect,
  "rdReset": acRdReset,

  "dlSubmit": acDlSubmit,

  "dtSelect": acDtSelect,

  "clSelect": acClSelect,

  "rgSubmit": acRgSubmit,

  "slSelect": acSlSelect,
  "slAdd": acSlAdd,
  "slToggle": acSlToggle,
  "slRadio": acSlRadio,

  "ckSubmit": acCkSubmit,
}

HEAD = """
<title>Widgets | Zelbinium</title>

<!-- HTML Syntax highlighting -->
<link rel="stylesheet" href="//cdnjs.cloudflare.com/ajax/libs/highlight.js/10.1.2/styles/default.min.css">
<script src="//cdnjs.cloudflare.com/ajax/libs/highlight.js/10.1.2/highlight.min.js"></script>

<!-- CKEditor -->
<script src="https://code.jquery.com/jquery-3.2.1.slim.min.js"
  integrity="sha256-k2WSCIexGzOj3Euiig+TlR8gA0EmPjuc79OEeY5L45g=" crossorigin="anonymous"></script>
<script src="https://cdn.ckeditor.com/4.22.1/standard/ckeditor.js"></script>
<script src="https://cdn.ckeditor.com/4.22.1/standard/adapters/jquery.js"></script>

<style>
  output, .widget {
    font-family: monospace;
    font-size: large;
    background-color: cornsilk ;
  }

  details {
    cursor: pointer;
  }

  .hidden {
    display: none;
  }

  output > span {
    all: initial;
    background-color: lightgrey;
    font-style: oblique;
  }

  output > span::before {
    content: '('
  }

  output > span::after {
    content: ')'
  }

  .hljs {
    margin: 0px;
  }
</style>
"""

BODY = """
<div>
  <div id="Retrieving">
    <span>Importing </span>
    <output id="RetrievedWidget">(please wait…)</output>
    <span> widget. </span>
  </div>
  <br />
</div>
<fieldset class="hidden" id="button">
  <legend class="widget">button</legend>
  <fieldset>
    <button xdh:onevent="btSubmit">A button</button>
  </fieldset>
  <hr />
  <details>
    <summary>Source code</summary>
    <fieldset>
      <legend>HTML</legend>
      <pre class="lang-html"></pre>
    </fieldset>
    <fieldset>
      <legend>Python</legend>
      <pre class="lang-python">
CALLBACKS = {
  "btSubmit": lambda dom: dom.alert("Click on button detected!"),
}      </pre>
    </fieldset>
  </details>
</fieldset>
<fieldset class="hidden" id="password">
  <legend class="widget">password</legend>
  <fieldset>
    <input type="password" xdh:onevent="pwSubmit" placeholder="Password" />
    <span>Submitted password: </span>
    <output id="pwOutput">
      <span>Type a password and hit the <span style="font-weight: bold;">Enter</span> key</span>
    </output>
  </fieldset>
  <hr />
  <details>
    <summary>Source code</summary>
    <fieldset>
      <legend>HTML</legend>
      <pre class="lang-html"></pre>
    </fieldset>
    <fieldset>
      <legend>Python</legend>
      <pre class="lang-python">
CALLBACKS = {
  "pwSubmit": lambda dom, id: dom.setValue("pwOutput", dom.getValue(id)),
}      </pre>
    </fieldset>
  </details>
</fieldset>
<fieldset class="hidden" id="checkbox">
  <legend class="widget">checkbox</legend>
  <fieldset>
    <div>
      <p>Specify the type of vehicle you own:</p>
      <label>
        <input type="checkbox" id="cbBicycle" xdh:onevent="cbSelect" />
        <span>Bicycle</span>
      </label>
      <br />
      <label>
        <input type="checkbox" id="cbCar" xdh:onevent="cbSelect" />
        <span>Car</span>
      </label>
      <br />
      <label>
        <input type="checkbox" id="cbPirogue" xdh:onevent="cbSelect" />
        <span>Pirogue</span>
      </label>
    </div>
    <p></p>
    <div>
      <span>Last selected vehicle: </span>
      <output id="cbOutput">
        <span>Click on a checkbox or its label</span>
      </output>
    </div>
    <p></p>
    <div>
      <button xdh:onevent="cbSubmit">Submit</button>
    </div>
  </fieldset>
  <hr />
  <details>
    <summary>Source code</summary>
    <fieldset>
      <legend>HTML</legend>
      <pre class="lang-html"></pre>
    </fieldset>
    <fieldset>
      <legend>Python</legend>
      <pre class="lang-python">
CALLBACKS = {
  "cbSelect": lambda dom, id: dom.setValue("cbOutput", "{} ({})".format(id, dom.getValue(id))),
  "cbSubmit": lambda dom: dom.alert(str(dom.getValues(["cbBicycle", "cbCar","cbPirogue"]))),
}      </pre>
    </fieldset>
  </details>
</fieldset>
<fieldset class="hidden" id="radio">
  <legend class="widget">radio</legend>
  <fieldset>
    <div>How to contact you:</p>
      <span id="rdRadios" xdh:radio="rdContact" xdh:onevent="rdCheck">
        <label>
          <input type="radio" name="rdContact" value="Email" />
          <span>Email</span>
        </label>
        <label>
          <input type="radio" name="rdContact" value="Phone" />
          <span>Phone</span>
        </label>
        <label>
          <input type="radio" name="rdContact" value="Mail" />
          <span>Mail (post)</span>
        </label>
      </span>
      <span>&nbsp;</span>
      <span>
        <button xdh:onevent="rdReset">Reset</button>
      </span>
    </div>
    <p></p>
    <div>
      <span>Selected contact method: </span>
      <select id="rdSelect" xdh:onevent="rdSelect">
        <option selected="" disabled="" value="None">Check above or select below</option>
        <option value="Email">Email</option>
        <option value="Phone">Phone</option>
        <option value="Mail">Mail (post)</option>
      </select>
    </div>
  </fieldset>
  <hr />
  <details>
    <summary>Source code</summary>
    <fieldset>
      <legend>HTML</legend>
      <pre class="lang-html"></pre>
    </fieldset>
    <fieldset>
      <legend>Python</legend>
      <pre class="lang-python">
CALLBACKS = {
  "rdCheck": lambda dom, id: dom.setValue("rdSelect", dom.getValue(id)),
  "rdSelect": lambda dom, id: dom.setValue("rdRadios", dom.getValue(id)),
  "rdReset": lambda dom: dom.setValues({"rdSelect": "None", "rdRadios": ""}),
}      </pre>
    </fieldset>
  </details>
</fieldset>
<fieldset class="hidden" id="datalist">
  <legend class="widget">datalist</legend>
  <fieldset>
    <span>
      <input list="dlFlavors" xdh:onevent="dlSubmit" placeholder="Select a flavor" />
      <datalist id="dlFlavors">
        <option value="Caramel"></option>
        <option value="Chocolate"></option>
        <option value="Vanilla"></option>
        <option value="Mint"></option>
      </datalist>
    </span>
    <span>Selected flavor: </span>
    <output id="dlOutput">
      <span>Select flavor, or type (a new) one and validate</span>
    </output>
  </fieldset>
  <hr />
  <details>
    <summary>Source code</summary>
    <fieldset>
      <legend>HTML</legend>
      <pre class="lang-html"></pre>
    </fieldset>
    <fieldset>
      <legend>Python</legend>
      <pre class="lang-python">
dlFlavors = ["Vanilla", "Chocolate", "Caramel", "Mint"]  


def acDlSubmit(dom, id):
  global dlFlavors

  flavor = dom.getValue(id)
  dom.setValue(id, "")
  if not flavor in dlFlavors:
    dlFlavors.append(flavor)
    dlFlavors.sort()
    dom.inner("dlFlavors", dlShape(dlFlavors))
  dom.setValue("dlOutput", flavor)


CALLBACKS = {
  "dlSubmit": acDlSubmit,
}      </pre>
    </fieldset>
  </details>
</fieldset>
<fieldset class="hidden" id="date">
  <legend class="widget">date</legend>
  <fieldset>
    <input type="date" xdh:onevent="dtSelect" />
    <span>Selected date: </span>
    <output id="dtOutput">
      <span>Click on the date selector</span>
    </output>
  </fieldset>
  <hr />
  <details>
    <summary>Source code</summary>
    <fieldset>
      <legend>HTML</legend>
      <pre class="lang-html"></pre>
    </fieldset>
    <fieldset>
      <legend>Python</legend>
      <pre class="lang-python">
CALLBACKS = {
  "dtSelect": lambda dom, id: dom.setValue("dtOutput", dom.getValue(id)),
}      </pre>
    </fieldset>
  </fieldset>
</fieldset>
<fieldset class="hidden" id="color">
  <legend class="widget">color</legend>
  <fieldset>
    <input type="color" id="clColor" xdh:onevent="clSelect" />
    <span>Selected color: </span>
    <output id="clOutput">
      <span>Click on the color selector</span>
    </output>
  </fieldset>
  <hr />
  <details>
    <summary>Source code</summary>
    <fieldset>
      <legend>HTML</legend>
      <pre class="lang-html"></pre>
    </fieldset>
    <fieldset>
      <legend>Python</legend>
      <pre class="lang-python">
CALLBACKS = {
  "clSelect": lambda dom, id: dom.setValue("clOutput", dom.getValue(id)),
}      </pre>
    </fieldset>
  </details>
</fieldset>
<fieldset class="hidden" id="range/meter">
  <legend class="widget">range/meter</legend>
  <fieldset style="display: flex; flex-direction: row; align-items: center; gap: 5px;">
    <label style="display: flex; align-items: center;">
      <span>Volume: </span>
      <input type="range" id="rgRange" xdh:onevent="rgSubmit" min="0" max="15" value="5" />
    </label>
    <input type="number" id="rgNumber" xdh:onevent="rgSubmit" min="0" max="15" value="5" size="3" />
    <meter id="rgMeter" min="0" max="15" low="5" high="10" optimum="3" value="5"></meter>
  </fieldset>
  <hr />
  <details>
    <summary>Source code</summary>
    <fieldset>
      <legend>HTML</legend>
      <pre class="lang-html"></pre>
    </fieldset>
    <fieldset>
      <legend>Python</legend>
      <pre class="lang-python">
def acRgSubmit(dom, id):
  value = dom.getValue(id)

  dom.setValues({
    "rgRange": value,
    "rgNumber": value,
    "rgMeter": value
  })        


CALLBACKS = {
  "rgSubmit": acRgSubmit,
}      </pre>
    </fieldset>
  </details>
</fieldset>
<fieldset class="hidden" id="select">
  <legend class="widget">select</legend>
  <fieldset>
    <select xdh:onevent="slSelect">
      <option selected disabled>-- Select a dinausor --</option>
      <optgroup label="Theropods">
        <option value="tyrannosaurus">Tyrannosaurus</option>
        <option value="velociraptor">Velociraptor</option>
        <option value="deinonychus">Deinonychus</option>
      </optgroup>
      <optgroup label="Sauropods">
        <option value="diplodocus">Diplodocus</option>
        <option value="saltasaurus">Saltasaurus</option>
        <option value="apatosaurus">Apatosaurus</option>
      </optgroup>
      <optgroup id="slOthers" label="Others" />
    </select>
    <span>
      <label for="slOutput">Selected dinausor: </label>
      <output id="slOutput">
        <span>Click on a dinosaur</span>
      </output>
    </span>
    <p></p>
    <div>
      <input id="slInput" xdh:onevent="slAdd" placeholder="Other dinausor to add" />
      <label>
        <input type="checkbox" xdh:onevent="slToggle" />
        <strong>Deactivate</strong>
      </label>
    </div>
    <p></p>
    <div>See the above <a href="#" target="_self" xdh:onevent="slRadio">radio widget</a> to see how to
      programmatically select an item from a list box.</div>
  </fieldset>
  <hr />
  <details>
    <summary>Source code</summary>
    <fieldset>
      <legend>HTML</legend>
      <pre class="lang-html"></pre>
    </fieldset>
    <fieldset>
      <legend>Python</legend>
      <pre class="lang-python">
def slEmbed(other):
  html = atlastk.createHTML()
  html.pushTag("option")
  html.putAttribute("selected", "selected")
  html.putValue(other)
  return html


def acSlAdd(dom):
  dom.begin("slOthers", slEmbed(dom.getValue("slInput")))
  dom.setValue("slInput", "")
  dom.focus("slInput")  
  

CALLBACKS = {
  "slSelect": lambda dom, id: dom.setValue("slOutput", dom.getValue(id)),
  "slAdd": acSlAdd,
  "slToggle": lambda dom, id: dom.disableElement("slOthers") if dom.getValue(id) == 'true' else dom.enableElement("slOthers"),
}      </pre>
    </fieldset>
  </details>
</fieldset>
<fieldset class="hidden" id="CKEditor">
  <legend class="widget">CKEditor</legend>
  <fieldset>
    <textarea id="ckInput"
      xdh:widget_="ckeditor|{entities: false, enterMode : CKEDITOR.ENTER_BR, linkShowTargetTab: false, versionCheck: false}|val\(\)|"></textarea>
    <button xdh:onevent="ckSubmit">Submit</button>
    <fieldset>
      <output id="ckOutput" style="all: initial;">
        <span>Type content in the editor and hit the <span style="font-weight: bold;">Submit</span> button</span>
      </output>
    </fieldset>
  </fieldset>
  <hr />
  <details>
    <summary>Source code</summary>
    <fieldset>
      <legend>HTML</legend>
      <pre class="lang-html"></pre>
    </fieldset>
    <fieldset>
      <legend>Python</legend>
      <pre class="lang-python">
CALLBACKS = {
  "ckSubmit": lambda dom, id: dom.setValue("ckOutput", dom.getValue("ckInput")),
}      </pre>
    </fieldset>
  </details>
</fieldset>
"""


atlastk.launch(CALLBACKS, headContent=HEAD)
