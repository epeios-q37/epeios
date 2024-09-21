import os, sys, time, io

os.chdir(os.path.dirname(os.path.realpath(__file__)))
sys.path.append("../atlastk")

import mcrcq, atlastk

MACRO_MARKER_ = '@'

macros = {
  "Test": {
    "Description": "Macro de test",
    "Content": "L5:R5"
  },
  "Forward": {
    "Description": "Going forward",
    "Content": "R35:L35 r3:l3 R0:L0 r0:l0 "
  },
  "Rewind": {
    "Description": "Step back",
    "Content": "R-35:L-35 r-3:l-3 R0:L0 r0:l0 "
  },
  "ForwardAndRewind": {
    "Description": "",
    "Content": "@Forward @Rewind"
  }
}

servos = {
  "l": "lf",
  "L": "ll",
  "r": "rf",
  "R": "rl"
}

BODY = """
<fieldset>
  <label xdh:mark="LF" style="display: flex; align-items: center;">
    <span>LF:&nbsp;</span>
    <input xdh:onevent="Slide" id="LFS" type="range" min="-45" max="45" step="1" value="0">
    <span>&nbsp;</span>
    <input xdh:onevent="Adjust" id="LFN" type="number" min="-45" max="45" value="0" step="5" size="3">
    <span>&nbsp;</span>
    <button xdh:onevent="Test">Test</button>
  </label>
  <label xdh:mark="LL" style="display: flex; align-items: center;">
    <span>LL:&nbsp;</span>
    <input xdh:onevent="Slide" id="LLS" type="range" min="-45" max="45" step="1" value="0">
    <span>&nbsp;</span>
    <input xdh:onevent="Adjust" id="LLN" type="number" min="-45" max="45" value="0" step="5" size="3">
    <span>&nbsp;</span>
    <button xdh:onevent="Test">Test</button>
  </label>
  <label xdh:mark="RL" style="display: flex; align-items: center;">
    <span>RL:&nbsp;</span>
    <input xdh:onevent="Slide" id="RLS" type="range" min="-45" max="45" step="1" value="0">
    <span>&nbsp;</span>
    <input xdh:onevent="Adjust" id="RLN" type="number" min="-45" max="45" value="0" step="5" size="3">
    <span>&nbsp;</span>
    <button xdh:onevent="Test">Test</button>
  </label>
  <label xdh:mark="RF" style="display: flex; align-items: center;">
    <span>RF:&nbsp;</span>
    <input xdh:onevent="Slide" id="RFS" type="range" min="-45" max="45" step="1" value="0">
    <span>&nbsp;</span>
    <input xdh:onevent="Adjust" id="RFN" type="number" min="-45" max="45" value="0" step="5" size="3">
    <span>&nbsp;</span>
    <button xdh:onevent="Test">Test</button>
  </label>
  <label xdh:mark="X1" style="display: flex; align-items: center;">
    <span>X1:&nbsp;</span>
    <input xdh:onevent="Slide" id="X1S" type="range" min="-45" max="45" step="1" value="0">
    <span>&nbsp;</span>
    <input xdh:onevent="Adjust" id="X1N" type="number" min="-45" max="45" value="0" step="5" size="3">
    <span>&nbsp;</span>
    <button xdh:onevent="Test">Test</button>
  </label>
  <label xdh:mark="X2" style="display: flex; align-items: center;">
    <span>X2:&nbsp;</span>
    <input xdh:onevent="Slide" id="X2S" type="range" min="-45" max="45" step="1" value="0">
    <span>&nbsp;</span>
    <input xdh:onevent="Adjust" id="X2N" type="number" min="-45" max="45" value="0" step="5" size="3">
    <span>&nbsp;</span>
    <button xdh:onevent="Test">Test</button>
  </label>
  <div style="height: 10px;"></div>
  <div style="display: flex;width: 100%; justify-content: center">
    <button xdh:onevent="Reset">Reset</button>
  </div>
  <fieldset>
    <div>
      <label style="width: 30%">
        <epan>Id:</epan>
        <input type="text"style="width: 10%">
      </label>
      <button>Save</button>
      <label>
        <span>Desc.:</span>
        <input type="text" style="width: 50%">
      </label>
      <button xdh:onevent="Submit">Execute</button>
    </div>
    <textarea id="Moves" xdh:onevent="Submit" style="width: 100%" name="" id=""></textarea>
  </fieldset>
  <fieldset id="Macros"/>
</fieldset>
"""

MACRO_HTML="""
<div xdh:mark="Macro{}">
  <div>
    <label>
      <span>Id.:</span>
      <input disabled="disabled" style="width: 20%" value="{}">
    </label>
    <button xdh:onevent="DeleteMacro">Delete</button>
    <label>
      <span>Desc.:</span>
      <input disabled="disabled" style="width: 50%" value="{}">
    </label>
  <button xdh:onevent="EditMacro">Edit</button>
  <button xdh:onevent="ExecuteMacro">Execute</button>
  </div>
  <textarea disabled="disabled" style="width: 100%">{}</textarea>
</div>
"""

C_INIT = """
from machine import Pin, PWM
import time

class Servo:
  __servo_pwm_freq = 50
  __min_u16_duty = 1640 - 2 # offset for correction
  __max_u16_duty = 7864 - 0  # offset for correction
  min_angle = 0
  max_angle = 180
  current_angle = 0.001


  def __init__(self, pin):
    self.__initialise(pin)


  def update_settings(self, servo_pwm_freq, min_u16_duty, max_u16_duty, min_angle, max_angle, pin):
    self.__servo_pwm_freq = servo_pwm_freq
    self.__min_u16_duty = min_u16_duty
    self.__max_u16_duty = max_u16_duty
    self.min_angle = min_angle
    self.max_angle = max_angle
    self.__initialise(pin)


  def move(self, angle):
    # round to 2 decimal places, so we have a chance of reducing unwanted servo adjustments
    angle = round(angle, 2)
    # do we need to move?
    if angle == self.current_angle:
        return
    self.current_angle = angle
    # calculate the new duty cycle and move the motor
    duty_u16 = self.__angle_to_u16_duty(angle)
    self.__motor.duty_u16(duty_u16)

  def current(self):
    return self.current_angle    

  def __angle_to_u16_duty(self, angle):
    return int((angle - self.min_angle) * self.__angle_conversion_factor) + self.__min_u16_duty


  def __initialise(self, pin):
    self.current_angle = 90.001
    self.__angle_conversion_factor = (self.__max_u16_duty - self.__min_u16_duty) / (self.max_angle - self.min_angle)
    self.__motor = PWM(Pin(pin))
    self.__motor.freq(self.__servo_pwm_freq)


def move(moves, step = 15):
  if not step or step == 0:
    servo.move(angle)
  else:
    current = servo.current()

    step = step + 1

    direction = 1 if angle > current else -1 

    while current < angle if direction == 1 else current > angle:
      servo.move(current)
      for _ in range(step):
        time.sleep(.0025)
      current += direction    


LL_PIN = 10
LF_PIN = 11
RL_PIN = 12
RF_PIN = 13
X1_PIN = 14
X2_PIN = 15

lf = Servo(LF_PIN)
ll = Servo(LL_PIN)
rl = Servo(RL_PIN)
rf = Servo(RF_PIN)
x1 = Servo(X1_PIN)
x2 = Servo(X2_PIN)

servos = {
  "lf": lf,
  "ll": ll,
  "rf": rf,
  "rl": rl,
  "x1": x1,
  "x2": x2
}

def moves_(moves, step):
  if not step:
    for move in moves:
      move[0].move(move[1])
  else:
    step += 1
    cont = True

    while cont:
      cont = False
      for move in moves:
        servo = move[0]
        current = int(servo.current())
        final = move[1]
        if current != final:
          cont = True
          current += 1 if current < final else -1

        servo.move(current)
      for _ in range(step):
        time.sleep(.0025)

def move(rawMoves, step=10):
  moves = []

  for move in rawMoves:
    moves.append((servos[move[0]], move[1]+90))

  moves_(moves, step)
"""

def resetStacks():
  global stacks

  stacks = {
    "l": [],
    "L": [],
    "R": [],
    "r": []
  }

stage = 0
moves = []

def move_(servo, angle, step = None):
  command = f"move([(\"{servo.lower()}\", {int(angle)})]"

  if step != None:
    command += f",{step}"

  command += ")"

  mcrcq.execute(command)
   

def reset_(dom):
  step = 5
  mcrcq.execute(f"""
move([
  ("lf", 0),
  ("ll", 0),
  ("rl", 0),
  ("rf", 0),
  ("x1", 0),
  ("x2", 0),
], {step})
""")
  dom.setValues({
    "LFN": 0,
    "LFS": 0,
    "LLN": 0,
    "LLS": 0,
    "RLN": 0,
    "RLS": 0,
    "RFN": 0,
    "RFS": 0,
    "X1N": 0,
    "X1S": 0,
    "X2N": 0,
    "X2S": 0,
  })


def displayMacros(dom):
  html = "<div>"

  for macro in macros:
    html += MACRO_HTML.format(macro, macro, macros[macro]["Description"], macros[macro]["Content"])

  html += "</div>"

  dom.inner("Macros", html)

def acConnect(dom):
  dom.inner("", BODY)
  displayMacros(dom)
  mcrcq.execute(C_INIT)
  reset_(dom)


def acTest(dom, id):
  mark = dom.getMark(id);
  dom.setValues({
    f"{mark}S": "0",
    f"{mark}N": "0",
  })
  move_(mark, 30, 5)
  move_(mark, -30, 5)
  move_(mark, 0, 5)


def acSlide(dom, id):
  mark = dom.getMark(id)
  angle = dom.getValue(f"{mark}S")
  dom.setValue(f"{mark}N", angle )
  move_(mark, angle)


def acAdjust(dom, id):
  mark = dom.getMark(id)
  angle = dom.getValue(f"{mark}N")
  dom.setValue(f"{mark}S", angle )
  move_(mark, angle)


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
  step = 0

  with io.StringIO(token[0]) as stream:
    while char := stream.read(1):
      if not char.isalpha():
        raise Exception(f"Servo id expected ({token[1]})!")
      
      servo = char
      angle = 0
      sign = 1

      if char := stream.read(1):
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

      if char not in "%$":
        if char != ':':
          raise Exception(f"Servo move can only be followed by '$' of y '%' ({token[1]})!")
      else:
        while (char := stream.read(1)) and char.isdigit():
          step = step * 10 + int(char)

        if char:
          raise Exception("Unexpected char at end of servo moves ({token[1]})!")
        
    return { "moves": moves, "step": None if not step else step }


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
    else:
      ast.append(("action",getMoves(token)))

  return ast


def getCommand(moves, step):
  command = "move([\n"

  for move in moves:
    command += f"(\"{servos[move[0]]}\",{move[1]}),"

  command += "]" + (f",{step}" if step else "") + ")" 

  return command



def getCommands(dom, string):
  commands = ""

  try:
    ast = getAST(tokenize(string))

    for item in ast:
      if item[0] == 'action':
        commands += getCommand(item[1]["moves"], item[1]["step"]) + '\n'
      elif item[0] == 'macro':
        for _ in range(item[1]["amount"]):
          commands += getCommands(dom, macros[item[1]["name"]]["Content"])
  except Exception as err:
    dom.alert(err)
    commands = ""
  
  return commands

def acSubmit(dom):
  global moves, stage

  stage = 0

  reset_(dom)
  command=getCommands(dom, dom.getValue("Moves"))
  mcrcq.execute(command)
  dom.focus("Moves")


def displayMove(dom):
  if stage < len(moves):
    dom.setValue("Move", f"{moves[stage][0]}{moves[stage][1]}")
  else:
    dom.setValue("Move", "")

def acFirst(dom):
  global stage, moves
  stage = 0
  resetStacks()
  moves = split(dom.getValue("Moves"))
  reset_(dom)
  displayMove(dom)


def acPrev(dom):
  global stage, moves, stacks

  if stage >= 0 and len(moves) > 0:
    if stage >= len(moves):
      stage = len(moves) - 1

    stacks[moves[stage][0]].pop()
    print(stacks)
    mcrcq.execute(buildCommand((moves[stage][0], 0 if len(stacks[moves[stage][0]]) == 0 else stacks[moves[stage][0]][-1])))
    displayMove(dom)
    stage -= 1


def acNext(dom):
  global stage, stacks, moves

  if stage == 0:
    reset_(dom)
    resetStacks()
    moves = split(dom.getValue("Moves"))


  if stage < len(moves):
    stacks[moves[stage][0]].append(moves[stage][1])
    print(stacks)
    mcrcq.execute(buildCommand(moves[stage]))
    stage += 1
    displayMove(dom)


def acExecuteMacro(dom, id):
  mcrcq.execute(getCommands(dom, macros[dom.getMark(id)[5:]]["Content"],))


CALLBACKS = {
   "": acConnect,
   "Test": acTest,
   "Slide": acSlide,
   "Adjust": acAdjust,
   "Reset": acReset,
   "Submit": acSubmit,
   "First": acFirst,
   "Prev": acPrev,
   "Next": acNext,
   "ExecuteMacro": acExecuteMacro,
}

mcrcq.connect()

atlastk.launch(CALLBACKS)