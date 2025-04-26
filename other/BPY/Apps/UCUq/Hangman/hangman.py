import os, sys, zlib, base64

os.chdir(os.path.dirname(os.path.realpath(__file__)))
sys.path.append("../../atlastk")

import atlastk, ucuq

from random import randint

L_FR = 0
L_EN = 1

LANGUAGE = None

L10N = (
  (
    "Vous êtes à court d'essais !",
    "You've run out of guesses!",
  ),
  (
    "Vous avez fait {errors} erreurs et trouvé {correct} bonnes lettres.",
    "You had {errors} errors and {correct} correct guesses."
  ),
  (
    "Le mot était '{}'.",
    "The world was '{}'."
  ),
  (
    "Bravo !",
    "Congratulations!"
  ),
  (
    "Vous avez gagné ! Félicitations !",
    "You've won! Congratulations!"
  ),
  # 5
  (
    "Recommencer",
    "Restart"
  )
)

getL10N = lambda m, *args, **kwargs: L10N[m][language].format(*args, **kwargs)

DICTIONARY_EN = (
  "apple", "banana", "grape", "orange", "mango", "peach", "pineapple", "strawberry",
  "blueberry", "blackberry", "kiwi", "melon", "pear", "plum", "cherry", "coconut",
  "watermelon", "papaya", "apricot", "lemon", "lime", "pomegranate", "fig", "date",
  "tomato", "cucumber", "carrot", "potato", "onion", "garlic", "pepper", "spinach",
  "lettuce", "broccoli", "cabbage", "celery", "zucchini", "eggplant", "beet", "radish",
  "turnip", "squash", "pumpkin", "asparagus", "artichoke", "parsley", "basil", "oregano",
  "cilantro", "thyme", "rosemary", "sage", "chili", "cinnamon", "ginger", "nutmeg",
  "vanilla", "peppermint", "cardamom", "anise", "clove", "fennel", "cumin", "coriander",
  "mustard", "sesame", "sunflower", "almond", "walnut", "pecan", "hazelnut", "cashew",
  "pistachio", "peanut", "grain", "barley", "oat", "wheat", "rice", "quinoa",
  "corn", "millet", "sorghum", "rye", "buckwheat", "spelt", "farro", "teff",
  "chickpea", "lentil", "kidney", "blackbean", "soybean", "pinto", "tofu", "tempeh",
  "seitan", "vegan", "vegetarian", "carnivore", "omnivore", "sustainable", "organic"
)

DICTIONARY_FR = (
  "abondant", "bateau", "chien", "dormir", "fleur", "gantier", "hiver",
  "jardin", "kiwi", "lune", "maison", "nuage", "oiseau", "plage",
  "quai", "rire", "soleil", "table", "usine", "verre", "wagon", "hippopotame",
  "arbre", "bonheur", "ciel", "danse", "feuille", "guitare", "herbe",
  "insecte", "jouet", "livre", "montagne", "neige", "glacier", "pluie",
  "question", "sable", "train", "univers", "vent", "whisky", "avion",
  "ballon", "chapeau", "drapeau", "foret", "glace", "horloge", "igloo",
  "kayak", "lampe", "musique", "nuit", "papillon", "radio", "stylo",
  "voiture", "amour", "biscuit", "cacao", "dent", "fromage", "graine",
  "hibou", "image", "jupe", "koala", "lait", "miel", "orange", "pomme",
  "quiche", "rose", "sucre", "tomate", "violon", "yaourt", "abeille",
  "banane", "carotte", "dauphin", "fraise", "gorille", "hamster",
  "igname", "jonquille", "kiosque", "lavande", "mouton", "narcisse",
  "poire", "renard", "serpent", "tulipe", "valise", "wasabi", "xylophone",
  "yoga", "zeste", "abricot", "bambou", "cactus", "dahlia", "framboise",
  "gantier", "hautbois", "jardinier", "kiosquier", "laurier", "magnolia",
  "mouvement", "nation", "nature", "nuageux", "paysage", "chasseur", "petit",
  "pouvoir", "rapport", "region", "ramification", "retour", "cauchemar", "rivage",
  "saison", "sang", "sauvetage", "secours", "sentier", "film", "service",
  "situation", "village", "spectacle", "sport", "station", "style", "appareil",
  "tendance", "terrain", "concert", "tourisme", "travail", "tribunal", "colifichet"
)

DICTIONNARIES = (
  DICTIONARY_FR,
  DICTIONARY_EN
)

HANGED_MAN = "Head Body LeftArm RightArm LeftLeg RightLeg".split()

unpack = lambda data : zlib.decompress(base64.b64decode(data)).decode()

START_PATTERN = unpack("eJwzMDBPA4NUAyBAZpsZGMApOrENRtmjbNqw03AAACZsma8=")

HANGED_MAN_PATTERNS = (
  unpack("eJwzMDBPA4NUAyBAZpsZGMApKrPTEGzjtGQ429wgFc42A9MQdrKBMUlsZL3IZiLbhewGJAeOsocpOw0HAAAjmpxP"),
  unpack("eJwzMDBPA4NUAyBAZpsZGMApKrPTEGzjtGQ429wgFc42A9MQdrKBMUlsZL3IZiLbhewGmvhxsLENRjY7DQcAANVInME="),
  unpack("eJzl0EEKgDAMRNErjRSS3ic09z+CUiH+TUFBV84mb9FOQyXPmaEjtEk1XnZebhll1yjbnKdD7ZF5l518izvc2tnpjjPoNIMbvHV0Bmyf/jOtfzsX2QG1wJ1J"),
  unpack("eJzlkDEOwCAMA79khGTyH0T+/4SitApeGJDaqV58C+YUoHlkYEaZQNbL7Iur9+SGkczomzvqEetb3dS/1OHUubitTa5NUpyZPsVY7OE6q+dwiH54Z2X8m32TC+KXnfY="),
  unpack("eJzF0EEKwCAMBMAvbQhE/yPm/0+oWInbYg9CS3PJXIybAMl7VbRiGxDtZfu0egkn1LD1frpAt8xveSb/xRl2M4vnOdPmTDPKbJFHskke1tZKDO5BP7xzIkteG3QTutvVSo5dbo69xuOl8Zf9oQ5w1p6c"),
  unpack("eJy9kEEOwCAIBL+0hoTS9xj5/xNqbAN70INJIxfmoMsAcPmohl7MCkT7mT1ZvAZfaME6+ssVssX8lzN5FjvsOhe3zNTMVCVnDZ9iWuxj6a1G8BA9c+dy25QF5E93W9y/LxK7MMt4lsN1wiDB4+yLegALt59A"),
)

HAPPY_PATTERN = "03c00c30181820044c32524a80018001824181814812442223c410080c3003c0"


class Core:
  def reset(self):
    self.errors = 0
    self.correctGuesses = []
    self.secretWord = ""
    self.chosen = ""

  def __init__(self):
    self.reset()


def randword(dictionnary):
  return dictionnary[randint(0, len(dictionnary)-1)]


def normalize(string):
  if len(string) < 16:
    return string.ljust(16)
  else:
    return string[-16:]
  

def isWokwi():
  return ringCount == 16


COUNTER_LEDS = {
  True: ((7,9),(6,10),(5,11),(3,13),(2,14),(1,15)),
  False: ((5,),(6,),(7,),(1,),(2,),(3,))
}


FIXED_LEDS = {
  True: (0,4,8,12),
  False: (4,0)
}


def patchRingIndex(index):
  return ( index + ringOffset ) % ringCount


async def showHanged(dom, errors):
  if (errors):
    cOLED.draw(HANGED_MAN_PATTERNS[errors-1],48, ox=47).show()
    await dom.removeClass(HANGED_MAN[errors-1], "hidden")

  for e in range(errors+1):
    for l in COUNTER_LEDS[isWokwi()][e-1]:
      cRing.setValue(patchRingIndex(l), [ringLimiter, 0, 0])

  for e in range(errors+1, 7):
    for l in COUNTER_LEDS[isWokwi()][e-1]:
      cRing.setValue(patchRingIndex(l), [0, ringLimiter, 0])

  for l in FIXED_LEDS[isWokwi()]:
    cRing.setValue(patchRingIndex(l), [ringLimiter * errors // 6, 0, ringLimiter * ( 6 - errors ) // 6])

  cRing.write()


async def showWord(dom, secretWord, correctGuesses):
  output = ("_" * len(secretWord))
  
  for i in range(len(secretWord)):
    if secretWord[i] in correctGuesses:
      output = output[:i] + secretWord[i] + output[i + 1:]

  cLCD.moveTo(0,0).putString(output.center(16))

  html = atlastk.createHTML()
  html.putTagAndValue("h1", output)
  await dom.inner("output", html)


async def reset(core, dom):
  core.reset()
  await dom.inner("", BODY.format(restart=getL10N(5)))
  core.secretWord = randword(DICTIONNARIES[language])
  print(core.secretWord)
  cOLED.fill(0).draw(START_PATTERN, 48, ox=47).show()
  await showWord(dom, core.secretWord, core.correctGuesses)
  cLCD.moveTo(0,1).putString(normalize(""))
#  cRing.fill([0,0,0]).setValue(0,[0,ringLimiter,0]).write()
  await showHanged(dom, 0)


async def atk(core, dom):
  global cLCD, cOLED, cRing, cBuzzer, ringCount, ringOffset, ringLimiter, language

  language = LANGUAGE if LANGUAGE != None else L_FR if dom.language.startswith("fr") else L_EN

  infos = await ucuq.ATKConnectAwait(dom, "")
  hardware = ucuq.getKitHardware(infos)

  cLCD = ucuq.HD44780_I2C(ucuq.I2C(*ucuq.getHardware(hardware, "LCD", ["SDA", "SCL", "Soft"])), 2, 16)
  cOLED =  ucuq.SSD1306_I2C(128, 64, ucuq.I2C(*ucuq.getHardware(hardware, "OLED", ["SDA", "SCL", "Soft"])))
  cBuzzer = ucuq.PWM(*ucuq.getHardware(hardware, "Buzzer", ["Pin"]), freq=50, u16 = 0).setNS(0)
  pin, ringCount, ringOffset, ringLimiter = ucuq.getHardware(hardware, "Ring", ["Pin", "Count", "Offset", "Limiter"])
  cRing = ucuq.WS2812(pin, ringCount)

  await reset(core,dom)


async def atkSubmit(core, dom, id):
  await dom.addClass(id, "chosen")

  guess = id.lower()
  core.chosen += guess

  if guess in core.secretWord:
    core.correctGuesses.append(guess)

    correct = 0

    for i in range(len(core.secretWord)):
      if core.secretWord[i] in core.correctGuesses:
        correct += 1

    await showWord(dom, core.secretWord, core.correctGuesses)

    if correct == len(core.secretWord):
      cLCD.moveTo(0,1).putString(getL10N(3))
      cOLED.draw(HAPPY_PATTERN, 16, mul=4, ox=32).show()
      for _ in range(3):
        for l in range(ringCount):
          cRing.setValue(patchRingIndex(l),[randint(0,ringLimiter // 3),randint(0,ringLimiter // 3),randint(0,ringLimiter // 3)]).write()
          ucuq.sleep(0.075)
      await dom.alert(getL10N(4))
      await reset(core, dom)
      return
  else:
    core.errors += 1
    await showHanged(dom, core.errors)
    cLCD.moveTo(0,1).putString(normalize(''.join([char for char in core.chosen if char not in core.correctGuesses])))
    cBuzzer.setFreq(30).setU16(50000)
    ucuq.sleep(0.5)
    cBuzzer.setU16(0)

  
  if core.errors >= len(HANGED_MAN):
    await dom.removeClass("Face", "hidden")
    await showWord(dom, core.secretWord, core.secretWord)
    await dom.alert(f"{getL10N(0)}\n{getL10N(1, errors=core.errors, correct=len(core.correctGuesses))}\n\n{getL10N(2,core.secretWord)}")
    await reset(core, dom)


async def atkRestart(core, dom):
  if (core.secretWord != "" ):
    await dom.alert(f"{getL10N(1, errors=core.errors, correct=len(core.correctGuesses))}\n\n{getL10N(2,core.secretWord)}")

  await reset(core, dom)

ATK_USER = Core
