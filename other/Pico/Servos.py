import os, sys, time

os.chdir(os.path.dirname(os.path.realpath(__file__)))
sys.path.append("../atlastk")

import mcrcq, atlastk
from io import StringIO


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
    <textarea rows="10" id="Moves" xdh:onevent="Submit" type="text" style="width: 100%">r20 r-20 l-20 l20</textarea>
    <div style="display: flex">
      <span style="align-content: center;">
        <button xdh:onevent="Submit" >Submit</button>
      </span>
      <fieldset>
        <button xdh:onevent="First">|&lt;</button>
        <button xdh:onevent="Prev">&lt;</button>
        <button xdh:onevent="Next">&gt;</button>
        <output id="Move"></output>
      </fieldset>
    </div>
  </fieldset>
</fieldset>
"""

C_INIT = """
from machine import Pin,PWM
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


def move(servo, angle, step = 15):
  if not step or step == 0:
    servo.move(angle)
  else:
    current = servo.current()

    step = step + 1

    direction = 1 if angle > current else -1 

    while current < angle if direction == 1 else current > angle:
      print(current)
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

def test(servo):
  move(servo, 90)  # tourne le servo à 0°
  move(servo, 45)  # tourne le servo à 0°
  time.sleep(0.5)
  move(servo, 135)  # tourne le servo à 45°
  time.sleep(0.5)
  move(servo, 90)  # tourne le servo à 0°

  
print("Yo")
move(lf, 90)
move(ll, 90)
move(rl, 90)
move(rf, 90)
move(x1, 90)
move(x2, 90)
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
  command = f"move({servo.lower()}, {int(angle)+90}"

  if step != None:
    command += f",{step}"

  command += ")"

  mcrcq.execute(command)
   

def acConnect(dom):
  dom.inner("", BODY)
  mcrcq.execute(C_INIT)


def acTest(dom, id):
  mark = dom.getMark(id);
  dom.setValues({
    f"{mark}S": "0",
    f"{mark}N": "0",
  })
  mcrcq.execute(f"test({mark.lower()})")


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


def reset_():
  step = 5
  move_("lf",0, step)
  move_("ll",0, step)
  move_("rl",0, step)
  move_("rf",0, step)
  move_("x1",0, step)
  move_("x2",0, step)


def acReset(dom):
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
  reset_()

def next(stream):
  char = stream.read(1)

  while char and char == ' ':
    char = stream.read(1)

  return char


def split(movesString):
  movesStream = StringIO(movesString)

  moves = []
  angle = ""

  char = next(movesStream)

  while char:
    target = char

    char = next(movesStream)

    if not char:
      break

    if char == '-':
      angle += char
      char = next(movesStream)

    while char and char.isdigit():
      angle += char
      char = next(movesStream)

    moves.append((target, int(angle)))

    target = ""
    angle = ""

  return moves


def buildCommand(move):
  print(move)
  match move[0]:
    case "L":
      member = "ll"
    case "l":
      member = "lf"
    case "R":
      member = "rl"
    case "r":
      member = "rf"
    case _:
      return ""  

  return f"move({member},{move[1]+90})"


def buildCommands(moves):
  moveCommands = ""

  for move in (moves):
    moveCommands += buildCommand(move) + "\ntime.sleep(0.1)\n"

  return moveCommands


def acSubmit(dom):
  global moves, stage

  stage = 0

  reset_()
  moves = split(dom.getValue("Moves"))
  mcrcq.execute(buildCommands(moves))
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
  reset_()
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
    reset_()
    resetStacks()
    moves = split(dom.getValue("Moves"))


  if stage < len(moves):
    stacks[moves[stage][0]].append(moves[stage][1])
    print(stacks)
    mcrcq.execute(buildCommand(moves[stage]))
    stage += 1
    displayMove(dom)
  

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
}

mcrcq.connect()

atlastk.launch(CALLBACKS)