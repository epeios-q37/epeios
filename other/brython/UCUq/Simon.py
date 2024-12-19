LISTEN = False

import atlastk, ucuq, json, math, random

ucuq.setDevice(id="Yellow")

RGB = ucuq.WS2812(3, 8)
OLED = ucuq.SSD1306_I2C(128, 64, ucuq.SoftI2C(0, 1))
BUZZER = ucuq.PWM(21)
BUZZER.setFreq(50).setNS(0)
ucuq.commit()

DIGITS = [
  0x3a33ae62e,
  0x11842108e, 
  0x3a213221f,
  0x7c223062e,
  0x8ca97c42,
  0x7e1e0862e,
  0x3a30f462e,
  0x7c2222108,
  0x3a317462e,
  0x3a317862e,
]

COEFF = 8

seq = ""
userSeq = ""

def digit(n,off):
  pattern = DIGITS[n]

  for x in range(5):
    for y in range(7):
      OLED.rect(off+x*COEFF,y*COEFF,COEFF,COEFF,1 if pattern & (1 << ((4 - x ) + (6 - y) * 5)) else 0)
  
  OLED.show()

def number(n):
  try:
    digit(n // 10, 12)
    digit(n % 10, 76)
  except:
    OLED.fill(0).show()

BUTTONS = {
  "R": [[30, 0, 0], 5, 9],
  "B": [[0, 0, 30], 7, 12],
  "Y": [[30, 30, 0], 1, 17],
  "G": [[0, 30, 0], 3, 5]
}

SPOKEN_COLORS = {
  "rouge": "R",
  "bleu": "B",
  "jaune": "Y",
  "vert": "G",
  "verre": "G",
  "verte": "G"
}

pitches = []

for i in range(24):
  pitches.append(int(220*math.pow(math.pow(2,1.0/12), i)))

LAUNCH_JINGLE = [
  3, 10,
  0, 8, 7, 5,
  3, 7, 10,
  8, 5, 3
]

SUCCESS_JINGLE = [
  7, 10, 19, 15, 17, 22
]

FAIL_JINGLE = [
  7, 10, 19, 15, 17, 22
]


def flash(button):
  RGB.fill([0,0,0])
  if button in BUTTONS:
    for i in range(3):
      RGB.setValue((BUTTONS[button][1] + i) % 8,BUTTONS[button][0])
  RGB.write()


def beep(note, delay = 0.29, sleep = 0.01):
  BUZZER.setFreq(pitches[note]).setU16(30000)
  ucuq.sleep(delay)
  BUZZER.setU16(0)
  if sleep:
    ucuq.sleep(sleep)


def playJingle(jingle):
  prevButton = ""
  prevPrevButton = ""
  number(None)
  ucuq.commit()
  for n in jingle:
    while True:
      button = random.choice(list(BUTTONS.keys())) 
      if ( button != prevButton ) and ( button != prevPrevButton ):
        break
    prevPrevButton = prevButton
    flash(prevButton := button)
    beep(n, 0.15, 0)
  flash("")
  ucuq.commit()


async def acConnect(dom):
  await dom.inner("", BODY)
  if not LISTEN:
    await dom.setAttribute("Listen","style", "display: none;")
  number(None)
  ucuq.commit()


async def acListen(dom):
  await dom.executeVoid("launch()")


def display(button):
  RGB.fill([0,0,0])
  if button in BUTTONS:
    for i in range(3):
      RGB.setValue((BUTTONS[button][1] + i) % 8,BUTTONS[button][0])
  RGB.write()
  BUZZER.setFreq(pitches[BUTTONS[button][2]]).setU16(30000)
  ucuq.sleep(0.29)
  BUZZER.setU16(0)
  RGB.fill([0,0,0]).write()
  ucuq.sleep(0.01)


def play(sequence):
  for s in sequence:
    display(s)
  ucuq.commit()

  
async def acDisplay(dom):
  colors = json.loads(await dom.getValue("Color"))

  for color in colors:
    color = color.lower()
    if color in SPOKEN_COLORS:
      ucuq.sleep(.25)
      display(SPOKEN_COLORS[color])
      ucuq.commit()

    


async def acNew():
  global seq

  playJingle(LAUNCH_JINGLE)

  seq = random.choice("RGBY")
  number(len(seq))
  play(seq)


async def acClick(dom, id):
  global seq, userSeq

  if not seq:
    return
  
  userSeq += id
  number(len(seq)-len(userSeq))
  display(id)

  if seq.startswith(userSeq):
    if len(seq) <= len(userSeq):
      playJingle(SUCCESS_JINGLE)
      userSeq = ""
      seq += random.choice("RGBY")
      number(len(seq))
      play(seq)
  else:
    number(len(seq)-1)
    BUZZER.setFreq(30).setU16(50000)
    ucuq.sleep(1)
    BUZZER.setU16(0)
    ucuq.commit()
    userSeq = ""
    seq = ""

  ucuq.commit()


CALLBACKS = {
  "": acConnect,
  "Listen": acListen,
  "Display": acDisplay,
  "New": acNew,
  "Click": acClick,
}

HEAD = """
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
<style>
#outer-circle {
  background: #385a94;
  border-radius: 50%;
  height: 500px;
  width: 500px;
  position: relative;
  border-style: solid;
  border-width: 10px;
  margin: auto;
  margin-top: 60px;
  box-shadow: 8px 8px 15px 5px #888888;
}

#G {
  position: absolute;
  height: 250px;
  width: 250px;
  border-radius: 250px 0 0 0;
  -moz-border-radius: 250px 0 0 0;
  -webkit-border-radius: 250px 0 0 0;
  background: darkgreen;
  top: 50%;
  left: 50%;
  margin: -250px 0px 0px -250px;
  border-style: solid;
  border-width: 5px;
  box-sizing: border-box;
  -moz-box-sizing: border-box;
  -webkit-box-sizing: border-box;
}

#R {
  position: absolute;
  height: 250px;
  width: 250px;
  border-radius: 0 250px 0 0;
  -moz-border-radius: 0 250px 0 0;
  -webkit-border-radius: 0 250px 0 0;
  background: darkred;
  top: 50%;
  left: 50%;
  margin: -250px 0px 0px 0px;
  border-style: solid;
  border-width: 5px;
  box-sizing: border-box;
  -moz-box-sizing: border-box;
  -webkit-box-sizing: border-box;
}

#Y {
  position: absolute;
  height: 250px;
  width: 250px;
  border-radius: 0 0 0 250px;
  -moz-border-radius: 0 0 0 250px;
  -webkit-border-radius: 0 0 0 250px;
  background: goldenrod;
  top: 50%;
  left: 50%;
  margin: 0px -250px 0px -250px;
  border-style: solid;
  border-width: 5px;
  box-sizing: border-box;
  -moz-box-sizing: border-box;
  -webkit-box-sizing: border-box;
}

#B {
  position: absolute;
  height: 250px;
  width: 250px;
  border-radius: 0 0 250px 0;
  -moz-border-radius: 0 0 250px 0;
  -webkit-border-radius: 0 0 250px 0;
  background: darkblue;
  top: 50%;
  left: 50%;
  margin: 0px 0px -250px 0px;
  border-style: solid;
  border-width: 5px;
  box-sizing: border-box;
  -moz-box-sizing: border-box;
  -webkit-box-sizing: border-box;
}

#inner-circle {
  position: absolute;
  background: grey;
  border-radius: 50%;
  height: 250px;
  width: 250px;
  border-style: solid;
  border-width: 10px;
  top: 50%;
  left: 50%;
  margin: -125px 0px 0px -125px;
  box-sizing: border-box;
  -moz-box-sizing: border-box;
  -webkit-box-sizing: border-box;
}

button {
  font-size: xx-large;
}
</style>
"""

BODY = """
<input id="Color" type="hidden">
<div id="outer-circle">
  <div id="G" xdh:onevent="Click"></div>
  <div id="R" xdh:onevent="Click"></div>
  <div id="Y" xdh:onevent="Click"></div>
  <div id="B" xdh:onevent="Click"></div>
  <div id="inner-circle" style="display: flex;justify-content: center;align-items: center; flex-direction: column;">
    <div>
      <button xdh:onevent="New">New</button>
    </div>
    <div>
      <button id="Listen" xdh:onevent="Listen">Listen</button>
    </div>
  </div>
</div>
"""

atlastk.launch(CALLBACKS, headContent = HEAD)
