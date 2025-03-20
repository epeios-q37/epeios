import os, sys, zlib, base64

os.chdir(os.path.dirname(os.path.realpath(__file__)))
sys.path.append("../../atlastk")

import atlastk, ucuq

ucuq.setDevice("Golf")

lcd = ucuq.HD44780_I2C(ucuq.SoftI2C(6, 7), 2, 16)
oled = ucuq.SSD1306_I2C(128, 64, ucuq.I2C(8, 9))
ring = ucuq.WS2812(20, 8)
buzzer = ucuq.PWM(5, freq=50, u16 = 0).setNS(0)


from random import randint

DICTIONARY_EN = [
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
]

DICTIONARY_FR = [
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
]


DICTIONARY = DICTIONARY_EN

HANGED_MAN = "Head Body LeftArm RightArm LeftLeg RightLeg".split()

unpak = lambda data : zlib.decompress(base64.b64decode(data)).decode()

START_PATTERN = unpak("eJwzMDBPA4NUAyBAZpsZGMApOrENRtmjbNqw03AAACZsma8=")

HANGED_MAN_PATTERNS = (
  unpak("eJwzMDBPA4NUAyBAZpsZGMApKrPTEGzjtGQ429wgFc42A9MQdrKBMUlsZL3IZiLbhewGJAeOsocpOw0HAAAjmpxP"),
  unpak("eJwzMDBPA4NUAyBAZpsZGMApKrPTEGzjtGQ429wgFc42A9MQdrKBMUlsZL3IZiLbhewGmvhxsLENRjY7DQcAANVInME="),
  unpak("eJzl0EEKgDAMRNErjRSS3ic09z+CUiH+TUFBV84mb9FOQyXPmaEjtEk1XnZebhll1yjbnKdD7ZF5l518izvc2tnpjjPoNIMbvHV0Bmyf/jOtfzsX2QG1wJ1J"),
  unpak("eJzlkDEOwCAMA79khGTyH0T+/4SitApeGJDaqV58C+YUoHlkYEaZQNbL7Iur9+SGkczomzvqEetb3dS/1OHUubitTa5NUpyZPsVY7OE6q+dwiH54Z2X8m32TC+KXnfY="),
  unpak("eJzF0EEKwCAMBMAvbQhE/yPm/0+oWInbYg9CS3PJXIybAMl7VbRiGxDtZfu0egkn1LD1frpAt8xveSb/xRl2M4vnOdPmTDPKbJFHskke1tZKDO5BP7xzIkteG3QTutvVSo5dbo69xuOl8Zf9oQ5w1p6c"),
  unpak("eJy9kEEOwCAIBL+0hoTS9xj5/xNqbAN70INJIxfmoMsAcPmohl7MCkT7mT1ZvAZfaME6+ssVssX8lzN5FjvsOhe3zNTMVCVnDZ9iWuxj6a1G8BA9c+dy25QF5E93W9y/LxK7MMt4lsN1wiDB4+yLegALt59A"),
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


def randword():
  return DICTIONARY[randint(0, len(DICTIONARY)-1)]


def normalize(string):
  if len(string) < 16:
    return string.ljust(16)
  else:
    return string[-16:]


async def showHanged(dom, errors):
  if (errors):
    oled.draw(HANGED_MAN_PATTERNS[errors-1],48, ox=47).show()
    await dom.removeClass(HANGED_MAN[errors-1], "hidden")

  for l in range(errors):
    ring.setValue(l + int(l > 2), [30, 0, 0])

  for l in range(errors, 7):
    ring.setValue(l + int(l > 2), [0, 30, 0])

  ring.setValue(7, [5 *  errors, 0, 5 * ( 6 - errors )]).setValue(3, [5 *  errors, 0, 5 * ( 6 - errors )]).write()


async def showWord(dom, secretWord, correctGuesses):
  output = ("_" * len(secretWord))
  
  for i in range(len(secretWord)):
    if secretWord[i] in correctGuesses:
      output = output[:i] + secretWord[i] + output[i + 1:]

  lcd.moveTo(0,0).putString(output.center(16))

  html = atlastk.createHTML()
  html.putTagAndValue("h1", output)
  await dom.inner("output", html)


async def reset(core, dom):
  core.reset()
  await dom.inner("", BODY)
  core.secretWord = randword()
  print(core.secretWord)
  oled.fill(0).draw(START_PATTERN, 48, ox=47).show()
  await showWord(dom, core.secretWord, core.correctGuesses)
  lcd.moveTo(0,1).putString(normalize(""))
  ring.fill([0,0,0]).setValue(0,[0,30,0]).write()
  await showHanged(dom, 0)


async def atk(core, dom):
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
      lcd.moveTo(0,1).putString("Congratulations!")
      oled.draw(HAPPY_PATTERN, 16, mul=4, ox=32).show()
      for _ in range(3):
        for l in range(8):
          ring.setValue(l,[randint(0,10),randint(0,10),randint(0,10)]).write()
          ucuq.sleep(0.075)
      await dom.alert("You've won! Congratulations!")
      await reset(core, dom)
      return
  else:
    core.errors += 1
    await showHanged(dom, core.errors)
    lcd.moveTo(0,1).putString(normalize(''.join([char for char in core.chosen if char not in core.correctGuesses])))
    buzzer.setFreq(30).setU16(50000)
    ucuq.sleep(0.5)
    buzzer.setU16(0)

  
  if core.errors >= len(HANGED_MAN):
    await dom.removeClass("Face", "hidden")
    await dom.alert("\nYou've run out of guesses. \nYou had " + str(core.errors) +
      " errors and " + str(len(core.correctGuesses)) + " correct guesses. " +
      "\n\nThe word was '" + core.secretWord + "'.")
    await reset(core, dom)


async def atkRestart(core, dom):
  if (core.secretWord != "" ):
    await dom.alert("You had " + str(core.errors) +
      " errors and " + str(len(core.correctGuesses)) + " correct guesses. " +
      "\nThe word was '" + core.secretWord + "'.")

  await reset(core, dom)

ATK_USER = Core
