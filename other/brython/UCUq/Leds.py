import os, sys

import atlastk, ucuq

leds = None

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

def update_(dom, R, G, B):
  leds.fill([int(R), int(G), int(B)])
  leds.write()

async def acConnect(dom):
  await dom.inner("", BODY)
  await dom.executeVoid("setColorWheel()")
  await dom.executeVoid(f"colorWheel.rgb = [0, 0, 0]")
  update_(dom, 0, 0, 0)

async def acSelect(dom):
  R, G, B = (await dom.getValues(["rgb-r", "rgb-g", "rgb-b"])).values()
  await dom.setValues(getAllValues_(R, G, B))
  update_(dom, R, G, B)

async def acSlide(dom):
  (R,G,B) = (await dom.getValues(["SR", "SG", "SB"])).values()
  await dom.setValues(getNValues_(R, G, B))
  await dom.executeVoid(f"colorWheel.rgb = [{R},{G},{B}]")
  update_(dom, R, G, B)

async def acAdjust(dom):
  (R,G,B) = (await dom.getValues(["NR", "NG", "NB"])).values()
  await dom.setValues(getSValues_(R, G, B))
  await dom.executeVoid(f"colorWheel.rgb = [{R},{G},{B}]")
  update_(dom, R, G, B)

async def acReset(dom):
  await dom.executeVoid(f"colorWheel.rgb = [0, 0, 0]")
  await dom.setValues(getAllValues_(0, 0, 0))
  update_(dom, 0, 0, 0)

def connect_(id):
  device = ucuq.UCUq()

  if not device.connect(id):
    print(f"Device '{id}' not available.")

  return device


CALLBACKS = {
  "": acConnect,
  "Select": acSelect,
  "Slide": acSlide,
  "Adjust": acAdjust,
  "Reset": acReset
}

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
  <fieldset style="display: flex; flex-direction: column; align-content: space-between">
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
      <div style="display: flex; justify-content: center;">
        <button xdh:onevent="Reset">Reset</button>
      </div>
    </div>
  </fieldset>
  </span>
  <fieldset style="display: flex; justify-content: center; flex-direction: column">
    <div id="color-wheel-container" xdh:onevent="Select"></div>
    <label class="label-checkbox" style="display: flex; justify-content: center;">
      <input type="checkbox" checked onchange="colorWheel.wheelReflectsSaturation = this.checked; colorWheel.redraw()">
      <span>wheel reflects saturation</span>
    </label>
  </fieldset>
</fieldset>
"""

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
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reinvented-color-wheel@0.4.0/css/reinvented-color-wheel.min.css">
<script src="https://cdn.jsdelivr.net/npm/reinvented-color-wheel@0.4.0"></script>
"""

ucuq.launch()

leds = ucuq.WS2812(16, 4)

atlastk.launch(CALLBACKS, headContent=HEAD)
