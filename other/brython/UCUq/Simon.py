import atlastk, ucuq, json, math, random

ucuq.setDevice(id="Yellow")

RGB = ucuq.WS2812(3, 8)
BUZZER = ucuq.PWM(21)
OLED = ucuq.SSD1306_I2C(128, 64, ucuq.SoftI2C(0, 1))

DIGITS = [
  0x75557,
  0x11111,
  0x71747,
  0x71317,
  0x55711,
  0x74717,
  0x74757,
  0x71111,
  0x75757,
  0x75717
]

COEFF = 12

def digit(n,off):
  pattern = DIGITS[n]

  for x in range(4):
    for y in range(5):
      OLED.rect(off+x*COEFF,y*COEFF,COEFF,COEFF,1 if pattern & (1 << ((3 - x ) + (4 - y) * 4)) else 0)
  
  OLED.show()

def number(n):
  if n > 9:
    digit(n // 10,0)
  digit(n % 10,60)

BUTTONS = {
  "R": [[30, 0, 0], 5, 5],
  "B": [[0, 0, 30], 7, 9],
  "Y": [[30, 30, 0], 1, 12],
  "G": [[0, 30, 0], 3, 17]
}

SPOKEN_COLORS = {
  "rouge": "R",
  "bleu": "B",
  "jaune": "Y",
  "vert": "G",
  "verre": "G",
  "verte": "G"
}


NOTES = []

jingle = [
    3, 10,  # C, G (Introduction)  
    0, 8, 7, 5,  # A, F, E, D (Thème principal)  
    3, 7, 10,  # C, E, G  
    8, 5, 3   # F, C (Conclusion)  
]


for i in range(24):
  NOTES.append(int(220*math.pow(math.pow(2,1.0/12), i)))


def lightUp(button):
  RGB.fill([0,0,0])
  if button in BUTTONS:
    for i in range(3):
      RGB.setValue((BUTTONS[button][1] + i) % 8,BUTTONS[button][0])
  RGB.write()


def play(note, delay = 0.29, sleep = 0.01):
  BUZZER.setFreq(NOTES[note]).setU16(30000)
  ucuq.sleep(delay)
  BUZZER.setU16(0)
  if sleep:
    ucuq.sleep(sleep)


async def acConnect(dom):
  prevButton = ""
  prevPrevButton = ""
  await dom.inner("", BODY)
  for n in jingle:
    while True:
      button = random.choice(list(BUTTONS.keys())) 

      if ( button != prevButton ) and ( button != prevPrevButton ):
        break;
    prevPrevButton = prevButton
    lightUp(prevButton := button)
    play(n, 0.2, 0)
  lightUp("")
  ucuq.commit()
  for n in range(0, 100, 3):
    number(n)
    ucuq.sleep(0.3)
    ucuq.commit()


async def acListen(dom):
  await dom.executeVoid("launch()")


def display(button):
  lightUp(button)
  play(BUTTONS[button][2])
  lightUp("")
  ucuq.commit()

  
async def acDisplay(dom):
  colors = json.loads(await dom.getValue("Color"))

  for color in colors:
    color = color.lower()
    if color in SPOKEN_COLORS:
      display(SPOKEN_COLORS[color])


async def acClick(dom, id):
  display(id)


CALLBACKS = {
  "": acConnect,
  "Listen": acListen,
  "Display": acDisplay,
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

  </style>
"""

BODY = """
<button xdh:onevent="Listen">Listen</button>
<input id="Color" type="hidden">
<div id="outer-circle">
  <div id="G" xdh:onevent="Click"></div>
  <div id="R" xdh:onevent="Click"></div>
  <div id="Y" xdh:onevent="Click"></div>
  <div id="B" xdh:onevent="Click"></div>
  <div id="inner-circle">
  </div>
</div>
"""

atlastk.launch(CALLBACKS, headContent = HEAD)
