import os, sys, time, io, json, datetime

os.chdir(os.path.dirname(os.path.realpath(__file__)))
sys.path.extend(("..","../../atlastk"))

import ucuq, atlastk

TARGET = "" # if "", retrieved from config file.

MACRO_MARKER_ = '$'

DEFAULT_STEP = 10

contentsHidden = True

macros = {}

# Hardware modes
M_STRAIGHT = "Straight"
M_PCA ="PCA"

# Config keys
HARDWARE_KEY = "Hardware"
HARDWARE_MODE_SUBKEY = "mode"
SPECS_KEY = "Specs"
TWEAK_KEY = "Tweak"

CONFIG_KEYS = {
  HARDWARE_KEY: {
    M_STRAIGHT: ["pin"],
    M_PCA: ["sda", "scl", "channel"]
  },
  SPECS_KEY: ["freq", "u16_min", "u16_max", "range"],
  TWEAK_KEY: ["angle", "offset", "invert"]
}

with open('Body.html', 'r') as file:
  BODY = file.read()

with open('Head.html', 'r') as file:
  HEAD = file.read()

with open('mc_init.py', 'r') as file:
  MC_INIT = file.read()

MACRO_HTML="""
<div class="macro" xdh:mark="Macro{}" style="margin-bottom: 3px;">
  <label>
    <span>Name:&nbsp;</span>
    <input disabled="disabled" value="{}">
  </label>
  <label>
    <span>Desc.:&nbsp;</span>
    <input disabled="disabled" value="{}">
  </label>
  <div>
    <button xdh:onevent="Execute">Execute</button>
  </div>
  <textarea class="description" disabled="disabled">{}</textarea>
  <div class="description">
    <button xdh:onevent="Edit">Edit</button>
    <button xdh:onevent="Delete">Delete</button>
  </div>
</div>
"""

stage = 0
moves = []

def move_(servo, angle, step = None):
  command = f"move([(\"{servo}\", {int(angle)})]"

  if step != None:
    command += f",{step}"

  command += ")"

  device.execute(command)
   

def reset_(dom):
  step = 5
  command = "move(["
  
  for servo in servos:
    command += f"('{servo}', 0),"
  
  command += f"], {step})"

  device.execute(command)


def displayMacros(dom):
  html = "<legend>Macros</legend><div>"

  if len(macros) >= 1:
    for macro in macros:
      if macro != '_':
        html += MACRO_HTML.format(macro, macro, macros[macro]["Description"], macros[macro]["Content"])
  else:
    html += "<em>No macros available</em>"

  html += "</div>"

  dom.inner("Macros", html)


def updateFileList(dom):
  html = ""
  for file in os.listdir("Macros"):
    html = f"<option value=\"{file}\">{file[:-5]}</option>\n" + html

  dom.inner("Files", html)


def acConnect(dom):
  dom.inner("", BODY)
  displayMacros(dom)
#  reset_(dom)
  updateFileList(dom)


def acTest():
  for servo in servos:
    move_(servo, 25, 3)
    move_(servo, -25, 3)
    move_(servo, 0, 3)


def acReset(dom):
  reset_(dom)


def getToken(stream):
  token = ""

  char = stream.read(1)

  while char and char == ' ':
    char = stream.read(1)

  pos = stream.tell()

  while char and char != ' ':
    token += char
    char = stream.read(1)

  if token:
    return (token, pos)
  else:
    return None
  

def getMacro(token):
  name = ""
  amount = 1

  with io.StringIO(token[0]) as stream:
    if not ( char := stream.read(1) ):
      raise Exception(f"Unexpected error ({token[1]})!")
    
    if char.isdigit():
      amount = int(char)

      while ( char := stream.read(1) ) and char .isdigit():
        amount = amount * 10 + int(char)

    if char != MACRO_MARKER_:
      raise Exception(f"Missing macro reference ({token[1]})!")
    
    if not (char := stream.read(1)):
      raise Exception(f"Empty macro name ({token[1]})!")
    
    if not char.isalpha(): 
      raise Exception(f"Macro name must beginning with a letter ({token[1]})!")
    
    while char and char.isalnum():
      name += char
      char = stream.read(1)

    if char:
      raise Exception(f"Unexpected character after macro call ({token[1]})!")

  if not name in macros:
    raise Exception(f"Unknown macro ({token[1]})!")

  return {"name": name, "amount" :amount} 


def getMoves(token):
  moves = []
  step = None

  with io.StringIO(token[0]) as stream:
    while char := stream.read(1):
      if not char.isalnum():
        raise Exception(f"Servo id expected ({token[1]})!")
      
      servo = char

      char = stream.read(1)

      while char and ( char.isalnum() or char == '_' ):
        servo += char
        char = stream.read(1)

      if not servo in servos:
        raise Exception(f"No servo of id '{servo}'  ({token[1]})")
        
      angle = 0
      sign = 1

      if char:
        if char in "+-":
          if char == '-':
            sign = -1
          char = stream.read(1)


      while char and char.isdigit():
        angle = angle * 10 + int(char)
        char = stream.read(1)

      moves.append((servo, angle * sign))

      if not char:
        break

      if char != "%":
        if char != ':':
          raise Exception(f"Servo move can only be followed by '%' ({token[1]})!")
      else:
        step = 0

        while (char := stream.read(1)) and char.isdigit():
          step = step * 10 + int(char)

        if char:
          raise Exception("Unexpected char at end of servo moves ({token[1]})!")
        
    return { "moves": moves, "step": str(step) if step else None if step == None else ""}
  

def getStep(token):
  step = 0

  with io.StringIO(token[0]) as stream:
    if stream.read(1) != '%':
      raise Exception(f"Unexpected error ({token[1]})!")
    
    while (char := stream.read(1)) and char.isdigit():
      step = step * 10 + int(char)

  return { "value": step if step else DEFAULT_STEP }


def tokenize(string):
  tokens = []

  with io.StringIO(string) as stream:
    while token := getToken(stream):
      tokens.append(token)

  return tokens


def getAST(tokens):
  ast = []
  for token in tokens:
    if token[0][0].isdigit() or token[0][0] == MACRO_MARKER_:
      ast.append(("macro", getMacro(token)))
    elif token[0][0] == '%':
      ast.append(("step", getStep(token)))
    else:
      ast.append(("action",getMoves(token)))

  return ast


def getCommand(moves, step, currentStep):
  command = "move(["

  for move in moves:
    command += f"('{move[0]}',{move[1]}),"

  command += "]," + ( step if step else str(currentStep) if step == None else str(DEFAULT_STEP) ) + ")"

  return command


def getCommands(dom, string, step = DEFAULT_STEP):
  commands = ""

  try:
    ast = getAST(tokenize(string))

    for item in ast:
      match item[0]:
        case "action":
          commands += getCommand(item[1]["moves"], item[1]["step"], step) + '\n'
        case "macro":
          for _ in range(item[1]["amount"]):
            commands += getCommands(dom, macros[item[1]["name"]]["Content"], step)
        case "step":
          step = item[1]["value"]
  except Exception as err:
    dom.alert(err)
    commands = ""

  return commands


def acExecute(dom, id):
  mark = dom.getMark(id)

  if mark == "Buffer":
    moves = dom.getValue("Content")
    dom.focus("Content")
  else:
    moves = macros[mark[5:]]["Content"]

  if dom.getValue("Reset") == "true":
    reset_(dom)

  device.execute(getCommands(dom, moves))


def acSave(dom):
  name = dom.getValue("Name").strip()

  if not ( content := dom.getValue("Content") ):
    dom.alert("There is no content to save!")
  else:
    macros["_"] = {"Description": "Internal use", "Content": content}

    if name == "":
        dom.alert("Please give a name for the macro!")
    elif not name.isidentifier() or name == '_':
      dom.alert(f"'{name}' is not a valid macro name!")
    elif not name in macros or dom.getValue("Ask") == "true" or dom.confirm(f"Overwrite existing macro of name '{name}'?"):
      macros[name] = {"Description": dom.getValue("Description"), "Content": content}

      with open(f"Macros/Latest.json", "w") as file: 
        file.write(json.dumps(macros, indent=2)) # type: ignore

    displayMacros(dom)


def expand(moves):
  content = ""
  
  for item in getAST(tokenize(moves)):
    match item[0]:
      case 'action':
        for move in item[1]["moves"]:
          content += move[0] + move[1] + ":"
        content = content[:-1]
        if item[2]:
          content += f"%{item[2]}"
        content += " "
      case 'macro':
        if not ( name := item[1]["name"] ) in macros:
          raise Exception(f"No macro named '{item[1]}!")
        else:
          for _ in range(item[1]["amount"]):
            content += macros[item[1]["name"]]["Content"] + " "

  return content


def acExpand(dom):
  try:
    dom.setValue("Content", expand(dom.getContent("Content")))
  except Exception as err:
    dom.alert(err)


def acDelete(dom, id):
  name = dom.getMark(id)[5:]

  if dom.confirm(f"Delete macro '{name}'?"):
    del macros[name]
    displayMacros(dom)


def acEdit(dom, id):
  name = dom.getMark(id)[5:]

  dom.setValues({
    "Name": name,
    "Description": macros[name]["Description"],
    "Content": macros[name]["Content"],
    "Ask": "false"
  })


def acHideContents(dom):
  global contentsHidden

  contentsHidden = not contentsHidden

  if contentsHidden:
    dom.enableElement("HideContents")
  else:
    dom.disableElement("HideContents")

  
def acSaveToFile(dom):
  with open(f"Macros/{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.json", "w") as file: 
    file.write(json.dumps(macros, indent=2)) # type: ignore
  
  updateFileList(dom)


def acLoadFromFile(dom):
  global macros

  with open(f"Macros/{dom.getValue('Files')}", "r") as file:
    macros = json.load(file)

  if "_" in macros:
    dom.setValue("Content", macros["_"]["Content"])

  displayMacros(dom)


CALLBACKS = {
   "": acConnect,
   "Test": acTest,
   "Reset": acReset,
   "Save": acSave,
   "Execute": acExecute,
   "Expand": acExpand,
   "Delete": acDelete,
   "Edit": acEdit,
   "HideContents": acHideContents,
   "SaveToFile": acSaveToFile,
   "LoadFromFile": acLoadFromFile,
}

device = ucuq.UCUq(TARGET, dryRun=False)

device.execute(MC_INIT)

command = ""

def getServoConfig(key, subkey, preset, motor):
  if ( key in motor ) and ( subkey in motor[key] ):
    return motor [key][subkey]
  else:
    return preset[key][subkey]


def getServosConfig(target):
  servos = {}

  with open("servos.json", "r") as file:
    config = json.load(file)[target]

  preset = config["Preset"]
  motors = config["Motors"]

  for label in motors:
    servos[label] = {}

    motor = motors[label]

    for key in CONFIG_KEYS:
      servos[label][key] = {}

      if key == HARDWARE_KEY:
        mode = getServoConfig(key, HARDWARE_MODE_SUBKEY, motor, preset)

        servos[label][key][HARDWARE_MODE_SUBKEY] = mode

        for subkey in CONFIG_KEYS[key][mode]:
          servos[label][key][subkey] = getServoConfig(key, subkey, preset, motor)
      else:
        for subkey in CONFIG_KEYS[key]:
          servos[label][key][subkey] = getServoConfig(key, subkey, preset, motor)
      

  return servos

servos = getServosConfig(target := device.getDeviceId())

print(f"Target: '{target}'")

for key in servos:
  servo = servos[key]
  hardware = servo[HARDWARE_KEY]
  specs = servo[SPECS_KEY]
  tweak = servo[TWEAK_KEY]
  if hardware[HARDWARE_MODE_SUBKEY] == M_STRAIGHT:
    pwm = f"{M_STRAIGHT}({hardware["pin"]}, {specs["freq"]})"
  elif hardware["mode"] == "PCA":
    pwm = f"{M_PCA}({hardware["sda"]}, {hardware["scl"]}, {hardware["channel"]}, {specs["freq"]})"
  else:
    raise Exception("Unknown hardware mode!")
  command += f"servos['{key}'] = Servo({pwm}, Servo.{SPECS_KEY}({specs["freq"]},{specs["u16_min"]},{specs["u16_max"]},{specs["range"]}),Servo.{TWEAK_KEY}({tweak["angle"]},{tweak["offset"]},{tweak["invert"]}))\n"

device.execute(command)

atlastk.launch(CALLBACKS, headContent = HEAD)