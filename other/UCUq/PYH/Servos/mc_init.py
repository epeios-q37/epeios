import machine, time

class Servo:
  class Specs:
    def __init__(self, freq, u16_min, u16_max, range):
      self.freq = freq
      self.min = u16_min
      self.max = u16_max
      self.range = range
  
  class Home:
    def __init__(self, angle, u16_offset):
      self.angle = angle
      self.offset = u16_offset
  
  class Domain:
    def __init__(self, u16_min, u16_max):
      self.min = u16_min
      self.max = u16_max
  
  def __init__(self, pin, specs, home, domain = None):
    if domain == None:
      domain = Servo.Domain(specs.min, specs.max)

    self.pin = pin
    self.specs = specs
    self.home = home
    self.domain = domain

    self.init()

  def angleToDuty_(self, angle):
    u16 = self.specs.min + angle * ( self.specs.max - self.specs.min ) / self.specs.range + self.home.offset

    if u16 > self.domain.max:
      u16 = self.domain.max
    elif u16 < self.domain.min:
      u16 = self.domain.min

    return int(u16)


  def init(self):
    self.angle = self.home.angle
    self.pwm = machine.PWM(machine.Pin(self.pin, machine.Pin.OUT), freq = self.specs.freq, duty_u16 = self.angleToDuty_(self.angle)) 

  def move(self, angle):
    self.angle = angle
    self.pwm.duty_u16(self.angleToDuty_(angle))

  def current(self):
    return self.angle


def setServos():
  global servos

  servos = {
    "lf": lf,
    "ll": ll,
    "rf": rf,
    "rl": rl,
  #  "x1": x1,
  #  "x2": x2
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

