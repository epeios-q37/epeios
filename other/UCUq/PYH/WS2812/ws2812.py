import atlastk, ucuq, random

RB_LIMIT = 30
RB_DELAY = .05
RB_TOTAL = RB_LIMIT * 7

ws2812 = None
nbLed = 0

rbTiming = None

def r2y(i):
  return [RB_LIMIT, i, 0]
  
def y2g(i):
  return [RB_LIMIT - i, RB_LIMIT, 0]
  
def g2c(i):
  return [0, RB_LIMIT, i]
  
def c2b(i):
  return [0, RB_LIMIT - i, RB_LIMIT]
  
def b2m(i):
  return [i, 0, RB_LIMIT]
  
def m2r(i):
  return [RB_LIMIT, 0, RB_LIMIT - i]
  
def rbShade(v, i):
  match int(v) % 6:
    case 0:
      return r2y(i)
    case 1:
      return y2g(i)
    case 2:
      return g2c(i)
    case 3:
      return c2b(i)
    case 4:
      return b2m(i)
    case 5:
      return m2r(i)
      
def rbFade(v, i, inOut):
  if not inOut:
    i = RB_LIMIT - i
  match int(v) % 6:
    case 0:
      return [i,0,0]
    case 1:
      return [i,i,0]
    case 2:
      return [0,i,0]
    case 3:
      return [0,i,i]
    case 4:
      return [0,0,i]
    case 5:
      return [i,0,i]
      

def rbLoopOne(d, i):
  if i < RB_LIMIT:
    return rbFade(d, i, True)
  elif i > RB_LIMIT * 6:
    return rbFade((d + 5 )% 6, i % RB_LIMIT, False)
  else:
    return rbShade(d + (i - RB_LIMIT) / RB_LIMIT, i % RB_LIMIT)
    

def rbLoop():
  v =  random.randint(0, 5)
  for i in range(RB_TOTAL):
    ws2812.fill(rbLoopOne(v, i)).write()
    ucuq.sleep(RB_DELAY)
  ws2812.fill([0]*3).write()
  ucuq.commit()      


def rainbow():
  rbLoop()

def convert_(hex):
  return int(int(hex,16) * 100 / 256)

def getValues_(target, R, G, B):
  return {
    target + "R": R,
    target + "G": G,
    target + "B": B
  }

def getNValues_(R, G, B):
  return getValues_("N", R, G, B)

def getSValues_(R, G, B):
  return getValues_("S", R, G, B)

def getAllValues_(R, G, B):
  return getNValues_(R, G, B) | getSValues_(R, G, B)

def update_(R, G, B):
  if ws2812:
    ws2812.fill([int(R), int(G), int(B)])
    ws2812.write()
    ucuq.commit()

def launch(dom, pin, count):
  global ws2812, nbLed

  try:
    ws2812 = ucuq.WS2812(pin, count)
    ucuq.commit()
  except Exception as err:
    dom.alert(err)
    nbLed = 0
  else:
    nbLed = count


def updateUI(dom, onDuty):
  ids = ["SlidersBox", "PickerBox"]

  if onDuty:
    dom.enableElements(ids)
    dom.disableElement("HardwareBox")
    dom.setValue("Switch", "true")
  else:
    dom.disableElements(ids)
    dom.enableElement("HardwareBox")
    dom.setValue("Switch", "false")

    match dom.getValue("Preset"):
      case "User":
        dom.enableElements(["Pin", "Count"])
      case "Bipedal":
        dom.setValues({
          "Pin": 16,
          "Count": 4
        })
        dom.disableElements(["Pin", "Count"])
      case "Dog":
        dom.setValues({
          "Pin": 0,
          "Count": 4
        })
        dom.disableElements(["Pin", "Count"])
      case _:
        raise Exception("Unknown preset!")

def acConnect(dom):
  label = ucuq.handleATK(dom)['kit']['label']
  ucuq.addCommand("pin=machine.Pin(16)")
  ucuq.commit()
  ucuq.addCommand("test=neopixel.NeoPixel(pin, 4)")
  ucuq.commit()

  dom.inner("", BODY)
  dom.executeVoid("setColorWheel()")
  dom.executeVoid(f"colorWheel.rgb = [0, 0, 0]")

  if not nbLed:
    match label:
      case "Freenove.Robot.Bipedal.RPIPicoW":
        dom.setValue("Preset", "Bipedal")
      case "Freenove.Robot.Dog.ESP32":
        dom.setValue("Preset", "Dog")

  updateUI(dom, False)

def acPreset(dom):
  match dom.getValue("Preset"):
    case "User":
      dom.setValues({
        "Pin": "",
        "Count": ""
      })
    case "Bipedal" | "Dog":
      pass
    case _:
      raise Exception("Unknown preset!")
    
  updateUI(dom, bool(nbLed))


def acSwitch(dom, id):
  global nbLed

  state = dom.getValue(id) == "true"

  if state:
    updateUI(dom, state)

    try:
      pin, count = (int(value.strip()) for value in (dom.getValues(["Pin", "Count"])).values())
    except:
      dom.alert("No or bad value for Pin/Count!")
      updateUI(dom, False)
    else:
      launch(dom, pin, count)
  else:
    nbLed = 0

  updateUI(dom, bool(nbLed))


def acSelect(dom):
  if nbLed:
    R, G, B = (dom.getValues(["rgb-r", "rgb-g", "rgb-b"])).values()
    dom.setValues(getAllValues_(R, G, B))
    update_(R, G, B)
  else:
    dom.executeVoid(f"colorWheel.rgb = [0,0,0]")  

def acSlide(dom):
  (R,G,B) = (dom.getValues(["SR", "SG", "SB"])).values()
  dom.setValues(getNValues_(R, G, B))
  dom.executeVoid(f"colorWheel.rgb = [{R},{G},{B}]")
  update_(R, G, B)

def acAdjust(dom):
  (R,G,B) = (dom.getValues(["NR", "NG", "NB"])).values()
  dom.setValues(getSValues_(R, G, B))
  dom.executeVoid(f"colorWheel.rgb = [{R},{G},{B}]")
  update_(R, G, B)

def acRainbow():
  rainbow()

def acReset(dom):
  dom.executeVoid(f"colorWheel.rgb = [0, 0, 0]")
  dom.setValues(getAllValues_(0, 0, 0))
  update_(0, 0, 0)

def connect_(id):
  device = ucuq.UCUq()

  if not device.connect(id):
    print(f"Device '{id}' not available.")

  return device


CALLBACKS = {
  "": acConnect,
  "Preset": acPreset,
  "Switch": acSwitch,
  "Select": acSelect,
  "Slide": acSlide,
  "Adjust": acAdjust,
  "Rainbow": acRainbow,
  "Reset": acReset
}

HEAD = """
<script type="text/javascript">
  function setColorWheel() {
    var hsvInputs = [document.getElementById('hsv-h'), document.getElementById('hsv-s'), document.getElementById('hsv-v')];
    var hslInputs = [document.getElementById('hsl-h'), document.getElementById('hsl-s'), document.getElementById('hsl-l')];
    var rgbInputs = [document.getElementById('rgb-r'), document.getElementById('rgb-g'), document.getElementById('rgb-b')];
    var hexInput = document.getElementById('hex');
    function set(input, value) {
      if (input !== document.activeElement) {
        input.value = value;
      }
    }
    window.colorWheel = new ReinventedColorWheel({
      appendTo: document.getElementById('color-wheel-container'),
      wheelDiameter: 300,
      wheelThickness: 30,
      handleDiameter: 24,
      wheelReflectsSaturation: true,
      onChange: function (color) {
        set(hsvInputs[0], color.hsv[0].toFixed(1));
        set(hsvInputs[1], color.hsv[1].toFixed(1));
        set(hsvInputs[2], color.hsv[2].toFixed(1));
        set(hslInputs[0], color.hsl[0].toFixed(1));
        set(hslInputs[1], color.hsl[1].toFixed(1));
        set(hslInputs[2], color.hsl[2].toFixed(1));
        set(rgbInputs[0], color.rgb[0]);
        set(rgbInputs[1], color.rgb[1]);
        set(rgbInputs[2], color.rgb[2]);
      },
    });

    colorWheel.onChange(colorWheel);

    function padStart(s, len) {
      s = String(s);
      while (s.length < len)
        s = ' ' + s;
      return s;
    }
  }
</script>
<link rel="stylesheet"
  href="https://cdn.jsdelivr.net/npm/reinvented-color-wheel@0.4.0/css/reinvented-color-wheel.min.css">
<script src="https://cdn.jsdelivr.net/npm/reinvented-color-wheel@0.4.0"></script>
<style>
  .switch-container {
    margin: auto;
    display: flex;
  }

  .switch {
    position: relative;
    display: inline-block;
    width: 30px;
    height: 17px;
    margin: auto;
  }

  .switch input {
    opacity: 0;
    width: 0;
    height: 0;
  }

  .slider {
    position: absolute;
    cursor: pointer;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: #ccc;
    -webkit-transition: .4s;
    transition: .4s cubic-bezier(0, 1, 0.5, 1);
    border-radius: 4px;
  }

  .slider:before {
    position: absolute;
    content: "";
    height: 13px;
    width: 13px;
    left: 3px;
    bottom: 2px;
    background-color: white;
    -webkit-transition: .4s;
    transition: .4s cubic-bezier(0, 1, 0.5, 1);
    border-radius: 3px;
  }

  input:checked+.slider {
    background-color: #52c944;
  }

  input:focus+.slider {
    box-shadow: 0 0 4px #7efa70;
  }

  input:checked+.slider:before {
    -webkit-transform: translateX(10px);
    -ms-transform: translateX(10px);
    transform: translateX(10px);
  }

  /* Rounded sliders */
  .slider.round {
    border-radius: 17px;
  }

  .slider.round:before {
    border-radius: 50%;
  }
</style>
"""

BODY = """
<div class="color-tables" style="display: none">
  <input id="hsv-h" type="number">
  <input id="hsv-s" type="number">
  <input id="hsv-v" type="number">
  <input id="hsl-h" type="number">
  <input id="hsl-s" type="number">
  <input id="hsl-l" type="number">
  <input id="rgb-r" type="number">
  <input id="rgb-g" type="number">
  <input id="rgb-b" type="number">
</div>
<fieldset>
  <legend>WS2012</legend>
  <fieldset style="display: flex;">
    <fieldset id="HardwareBox" style="display: flex; flex-direction: column; justify-content: center;">
      <div style="display: flex; justify-content: center;">
      <select id="Preset" xdh:onevent="Preset">
        <option value="User">User defined</option>
        <optgroup label="Freenove">
          <option value="Bipedal">Bipedal</option>
          <option value="Dog">Dog (ESP32)</option>
        </optgroup>
      </select>
        </div>
      <div style="margin: 10px">
      <label>
        <span>Pin:</span>
        <input id="Pin" size="2" type="number">
      </label>
      <label>
        <span>Count:</span>
        <input id="Count" size="3" type="number">
      </label>
        </div>
    </fieldset>
    <span class="switch-container">
      <label class="switch">
        <input id="Switch" type="checkbox" xdh:onevent="Switch">
        <span class="slider round"></span>
      </label>
    </span>
  </fieldset>
  <fieldset id="SlidersBox" style="display: flex; flex-direction: column; align-content: space-between">
    <div>
      <label style="display: flex; align-items: center;">
        <span>R:&nbsp;</span>
        <input id="SR" style="width: 100%" type="range" min="0" max="255" step="1" xdh:onevent="Slide" value="0">
        <span>&nbsp;</span>
        <input id="NR" xdh:onevent="Adjust" type="number" min="0" max="255" step="5" value="0" size="3">
      </label>
      <label style="display: flex; align-items: center;">
        <span>V:&nbsp;</span>
        <input id="SG" style="width: 100%" type="range" min="0" max="255" step="1" xdh:onevent="Slide" value="0">
        <span>&nbsp;</span>
        <input id="NG" xdh:onevent="Adjust" type="number" min="0" max="255" step="5" value="0" size="3">
      </label>
      <label style="display: flex; align-items: center;">
        <span>B:&nbsp;</span>
        <input id="SB" style="width: 100%" type="range" min="0" max="255" step="1" xdh:onevent="Slide" value="0">
        <span>&nbsp;</span>
        <input id="NB" xdh:onevent="Adjust" type="number" min="0" max="255" step="5" value="0" size="3">
      </label>
      <div style="display: flex; justify-content: space-evenly;">
        <button xdh:onevent="Rainbow">Rainbow</button>
        <button xdh:onevent="Reset">Reset</button>
      </div>
    </div>
  </fieldset>
  </span>
  <fieldset id="PickerBox" style="display: flex; justify-content: center; flex-direction: column">
    <div id="color-wheel-container" xdh:onevent="Select"></div>
    <label class="label-checkbox" style="display: flex; justify-content: center;">
      <input type="checkbox" checked onchange="colorWheel.wheelReflectsSaturation = this.checked; colorWheel.redraw()">
      <span>wheel reflects saturation</span>
    </label>
  </fieldset>
</fieldset>
"""

atlastk.launch(CALLBACKS, headContent=HEAD)
