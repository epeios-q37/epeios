import atlastk, ucuq, random, json

RB_DELAY = .05

ws2812 = None
ws2812Limiter = 0
onDuty = False
oledDIY = None

# Presets
P_USER = "User"
P_BIPEDAL = "Bipedal"
P_DOG = "Dog"
P_DIY = "DIY"
P_WOKWI = "Wokwi"

SPOKEN_COLORS =  {
  "rouge": [255, 0, 0],
  "vert": [0, 255, 0],
  "verre": [0, 255, 0],
  "verte": [0, 255, 0],
  "bleu": [0, 0, 255],
  "jaune": [255, 255, 0],
  "cyan": [0, 255, 255],
  "magenta": [255, 0, 255],
  "orange": [255, 127, 0],
  "violet": [127, 0, 255],
  "rose": [255, 127, 127],
  "gris": [127, 127, 127],
  "noir": [0, 0, 0],
  "blanc": [255, 255, 255],
  "marron": [127, 59, 0],
  "turquoise": [0, 127, 127],
  "beige": [255, 212, 170]
}


def rainbow():
  v =  random.randint(0, 5)
  i = 0
  while i < 7 * ws2812Limiter:
    ws2812.fill(ucuq.rbShadeFade(v, int(i), ws2812Limiter)).write()
    ucuq.sleep(RB_DELAY)
    i += ws2812Limiter / 20
  ws2812.fill([0]*3).write()
  ucuq.commit() 


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


def update_(r, g, b):
  if ws2812:
    ws2812.fill([int(r), int(g), int(b)]).write()
    if oledDIY:
      oledDIY.fill(0).text(f"R: {r}", 0, 5).text(f"G: {g}", 0, 20).text(f"B: {b}", 0, 35).show()
    ucuq.commit()


async def launchAwait(dom, pin, count):
  global ws2812, onDuty

  try:
    ws2812 = ucuq.WS2812(pin, count)
    ucuq.commit()
  except Exception as err:
    await dom.alert(err)
    onDuty = False
  else:
    onDuty = True


async def resetAwait(dom):
  await dom.executeVoid(f"colorWheel.rgb = [0, 0, 0]")
  await dom.setValues(getAllValues_(0, 0, 0))
  update_(0, 0, 0)    


async def updateUIAwait(dom, onDuty):
  ids = ["SlidersBox", "PickerBox"]

  if onDuty:
    await dom.enableElements(ids)
    await dom.disableElements(["HardwareBox", "Preset"])
    await dom.setValue("Switch", "true")
  else:
    await dom.disableElements(ids)
    await dom.enableElements(["HardwareBox", "Preset"])
    await dom.setValue("Switch", "false")

    preset = await dom.getValue("Preset")

    if preset == P_BIPEDAL:
      await dom.setValues({
        "Pin": ucuq.H_BIPEDAL["RGB"]["Pin"],
        "Count": ucuq.H_BIPEDAL["RGB"]["Count"],
        "Offset": ucuq.H_["RGB"]["Offset"],
        "Limiter": ucuq.H_["RGB"]["Limiter"],
      })
    elif preset == P_DOG:
      await dom.setValues({
        "Pin": ucuq.H_DOG["RGB"]["Pin"],
        "Count": ucuq.H_DOG["RGB"]["Count"],
        "Offset": ucuq.H_DOG["RGB"]["Offset"],
        "Limiter": ucuq.H_DOG["RGB"]["Limiter"],
      })
    elif preset == P_DIY:
      await dom.setValues({
        "Pin": ucuq.H_DIY_DISPLAYS["Ring"]["Pin"],
        "Count": ucuq.H_DIY_DISPLAYS["Ring"]["Count"],
        "Offset": ucuq.H_DIY_DISPLAYS["Ring"]["Offset"],
        "Limiter": ucuq.H_DIY_DISPLAYS["Ring"]["Limiter"],
      })
    elif preset == P_WOKWI:
      await dom.setValues({
        "Pin": ucuq.H_WOKWI_DISPLAYS["Ring"]["Pin"],
        "Count": ucuq.H_WOKWI_DISPLAYS["Ring"]["Count"],
        "Offset": ucuq.H_WOKWI_DISPLAYS["Ring"]["Offset"],
        "Limiter": ucuq.H_WOKWI_DISPLAYS["Ring"]["Limiter"],
      })
    elif preset != P_USER:
      raise Exception("Unknown preset!")


async def acConnect(dom):
  global oledDIY
  id = ucuq.getKitId(await ucuq.ATKConnectAwait(dom, BODY))

  await dom.executeVoid("setColorWheel()")
  await dom.executeVoid(f"colorWheel.rgb = [0, 0, 0]")

  if not onDuty:
    if id == ucuq.K_BIPEDAL:
      await dom.setValue("Preset", P_BIPEDAL)
    elif id == ucuq.K_DOG:
      await dom.setValue("Preset", P_DOG)
    elif id == ucuq.K_DIY_DISPLAYS:
      oledDIY = ucuq.SSD1306_I2C(128, 64, ucuq.I2C(ucuq.H_DIY_DISPLAYS["OLED"]["SDA"], ucuq.H_DIY_DISPLAYS["OLED"]["SCL"], soft = ucuq.H_DIY_DISPLAYS["OLED"]["Soft"]))
      await dom.setValue("Preset", P_DIY)
    elif id == ucuq.K_WOKWI_DISPLAYS:
      oledDIY = ucuq.SSD1306_I2C(128, 64, ucuq.I2C(ucuq.H_WOKWI_DISPLAYS["OLED"]["SDA"], ucuq.H_WOKWI_DISPLAYS["OLED"]["SCL"], soft = ucuq.H_WOKWI_DISPLAYS["OLED"]["Soft"]))
      await dom.setValue("Preset", P_WOKWI)

  await updateUIAwait(dom, False)


async def acPreset(dom):
  await updateUIAwait(dom, onDuty)


async def acSwitch(dom, id):
  global onDuty, ws2812Limiter

  state = (await dom.getValue(id)) == "true"

  if state:
    await updateUIAwait(dom, state)

    try:
      pin, count, ws2812Limiter = (int(value.strip()) for value in (await dom.getValues(["Pin", "Count", "Limiter"])).values())
    except:
      await dom.alert("No or bad value for Pin/Count!")
      await updateUIAwait(dom, False)
    else:
      await launchAwait(dom, pin, count)
  else:
    onDuty = False

  await updateUIAwait(dom, onDuty)


async def acSelect(dom):
  if onDuty:
    R, G, B = (await dom.getValues(["rgb-r", "rgb-g", "rgb-b"])).values()
    await dom.setValues(getAllValues_(R, G, B))
    update_(R, G, B)
  else:
    await dom.executeVoid(f"colorWheel.rgb = [0,0,0]")  


async def acSlide(dom):
  (R,G,B) = (await dom.getValues(["SR", "SG", "SB"])).values()
  await dom.setValues(getNValues_(R, G, B))
  await dom.executeVoid(f"colorWheel.rgb = [{R},{G},{B}]")
  update_(R, G, B)


async def acAdjust(dom):
  (R,G,B) = (await dom.getValues(["NR", "NG", "NB"])).values()
  await dom.setValues(getSValues_(R, G, B))
  await dom.executeVoid(f"colorWheel.rgb = [{R},{G},{B}]")
  update_(R, G, B)


async def acListen(dom):
  await dom.executeVoid("launch()")

  
async def acDisplay(dom):
  colors = json.loads(await dom.getValue("Color"))

  for color in colors:
    color = color.lower()
    if color in SPOKEN_COLORS:
      r, g, b = [ws2812Limiter * c // 255 for c in SPOKEN_COLORS[color]]
      await dom.setValues(getAllValues_(r, g, b))
      await dom.executeVoid(f"colorWheel.rgb = [{r},{g},{b}]")
      update_(r, g, b)
      if oledDIY:
        oledDIY.text(color, 0, 50).show()
        ucuq.commit()
      break;


async def acRainbow(dom):
  await resetAwait(dom)
  rainbow()


async def acReset(dom):
  await resetAwait(dom)


CALLBACKS = {
  "": acConnect,
  "Preset": acPreset,
  "Switch": acSwitch,
  "Select": acSelect,
  "Slide": acSlide,
  "Adjust": acAdjust,
  "Listen": acListen,
  "Display": acDisplay,
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
<script src="https://cdn.jsdelivr.net/npm/reinvented-color-wheel@0.4.0">
</script>
<style>
  .switch-container {
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
<script>
  var SpeechRecognition = SpeechRecognition || webkitSpeechRecognition;
  var SpeechRecognitionEvent = SpeechRecognitionEvent || webkitSpeechRecognitionEvent;
  
  var recognition = new SpeechRecognition();
  
  recognition.continuous = false;
  recognition.lang = 'fr-FR';
  recognition.interimResults = false;
  recognition.maxAlternatives = 5;
  
  function launch() {
    recognition.start();
    console.log('Ready to receive a color command.');
  };
  
  recognition.onresult = function(event) {
    var color = event.results[0][0].transcript;
    console.log('Confidence: ' + event.results[0][0].confidence);
    results = event.results[0];
    array = [];
    for (const cle in results) {
      if (results.hasOwnProperty(cle)) {
          console.log(`${cle}: ${results[cle].transcript}`);
          array.push(results[cle].transcript);
      }
      console.log(array)
    }
    console.log(color);
    document.getElementById("Color").value = JSON.stringify(array);
    launchEvent("test|BUTTON|click||(Display)");
  };
  
  recognition.onspeechend = function() {
    recognition.start();
  };
  
  recognition.onnomatch = function(event) {
    console.warn("I didn't recognise that color.");
  };
  
  recognition.onerror = function(event) {
    console.err('Error occurred in recognition: ' + event.error);
  };
  </script>
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
  <fieldset>
    <fieldset style="display: flex; flex-direction: column;">
      <div style="display: flex; justify-content: space-evenly; margin-bottom: 5px;">
        <select id="Preset" xdh:onevent="Preset">
          <option value="User">User</option>
          <optgroup label="Freenove">
            <option value="Bipedal">Bipedal</option>
            <option value="Dog">Dog (ESP32)</option>
          </optgroup>
          <option value="DIY">DIY</option>
          <option value="Wokwi">Wokwi</option>
        </select>
        <span class="switch-container">
          <label class="switch">
            <input id="Switch" type="checkbox" xdh:onevent="Switch">
            <span class="slider round"></span>
          </label>
        </span>
      </div>
      <fieldset id="HardwareBox" style="display: flex; flex-direction: row; justify-content: space-around">
        <div style="display: flex; flex-direction: column; justify-content: space-between">
          <label style="display: flex; justify-content: space-between">
            <span>Pin:&nbsp;</span>
            <input id="Pin" min="0" max="99" type="number">
          </label>
          <label style="display: flex; justify-content: space-between">
            <span>Count:&nbsp;</span>
            <input id="Count" min="0" max="999" type="number">
          </label>
        </div>
        <div style="display: flex; flex-direction: column; justify-content: space-between">
          <label style="display: flex; justify-content: space-between">
            <span>Offset:&nbsp;</span>
            <input id="Offset" min="-999" max="999" type="number">
          </label>
          <label style="display: flex; justify-content: space-between">
            <span>Limiter:&nbsp;</span>
            <input id="Limiter" min="0" max="255" type="number">
          </label>
        </div>
      </fieldset>
    </fieldset>
    <fieldset id="SlidersBox" style="display: flex; flex-direction: column; align-content: space-between">
      <div>
        <label style="display: flex; align-items: center;">
          <span>R:&nbsp;</span>
          <input id="SR" style="width: 100%" type="range" min="0" max="255" step="1" xdh:onevent="Slide" value="0">
          <span>&nbsp;</span>
          <input id="NR" xdh:onevent="Adjust" type="number" min="0" max="255" step="5" value="0" style="width: 5ch">
        </label>
        <label style="display: flex; align-items: center;">
          <span>V:&nbsp;</span>
          <input id="SG" style="width: 100%" type="range" min="0" max="255" step="1" xdh:onevent="Slide" value="0">
          <span>&nbsp;</span>
          <input id="NG" xdh:onevent="Adjust" type="number" min="0" max="255" step="5" value="0" style="width: 5ch">
        </label>
        <label style="display: flex; align-items: center;">
          <span>B:&nbsp;</span>
          <input id="SB" style="width: 100%" type="range" min="0" max="255" step="1" xdh:onevent="Slide" value="0">
          <span>&nbsp;</span>
          <input id="NB" xdh:onevent="Adjust" type="number" min="0" max="255" step="5" value="0" style="width: 5ch">
        </label>
        <div style="display: flex; justify-content: space-evenly;">
          <button xdh:onevent="Listen">Listen</button>
          <button xdh:onevent="Rainbow">Rainbow</button>
          <button xdh:onevent="Reset">Reset</button>
        </div>
      </div>
    </fieldset>
    </span>
    <fieldset id="PickerBox" style="display: flex; justify-content: center; flex-direction: column">
      <div id="color-wheel-container" xdh:onevent="Select"></div>
      <label class="label-checkbox" style="display: flex; justify-content: center;">
        <input type="checkbox" checked
          onchange="colorWheel.wheelReflectsSaturation = this.checked; colorWheel.redraw()">
        <span>wheel reflects saturation</span>
      </label>
    </fieldset>
  </fieldset>
  <input id="Color" type="hidden">
  """

atlastk.launch(CALLBACKS, headContent=HEAD)
