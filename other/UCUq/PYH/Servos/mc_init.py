import machine, time, ustruct

servos = {}

class PCA9685:
  def __init__(self, i2c, address=0x40):
    self.i2c = i2c
    self.address = address
    self.reset()

  def _write(self, address, value):
    self.i2c.writeto_mem(self.address, address, bytearray([value]))

  def _read(self, address):
    return self.i2c.readfrom_mem(self.address, address, 1)[0]

  def reset(self):
    self._write(0x00, 0x00) # Mode1

  def freq(self, freq=None):
    if freq is None:
      return int(25000000.0 / 4096 / (self._read(0xfe) - 1))
    prescale = int(25000000.0 / 4096.0 / freq + 1)
    old_mode = self._read(0x00) # Mode 1
    self._write(0x00, (old_mode & 0x7F) | 0x10) # Mode 1, sleep
    self._write(0xfe, prescale) # Prescale
    self._write(0x00, old_mode) # Mode 1
    time.sleep_us(5)
    self._write(0x00, old_mode | 0xa1) # Mode 1, autoincrement on

  def pwm(self, index, on=None, off=None):
    if on is None or off is None:
      data = self.i2c.readfrom_mem(self.address, 0x06 + 4 * index, 4)
      return ustruct.unpack('<HH', data)
    data = ustruct.pack('<HH', on, off)
    self.i2c.writeto_mem(self.address, 0x06 + 4 * index,  data)

  def duty(self, index, value=None, invert=False):
    if value is None:
      pwm = self.pwm(index)
      if pwm == (0, 4096):
        value = 0
      elif pwm == (4096, 0):
        value = 4095
      value = pwm[1]
      if invert:
        value = 4095 - value
      return value
    if not 0 <= value <= 4095:
      raise ValueError("Out of range")
    if invert:
      value = 4095 - value
    if value == 0:
      self.pwm(index, 0, 4096)
    elif value == 4095:
      self.pwm(index, 4096, 0)
    else:
      self.pwm(index, 0, value)

class Straight:
  def __init__(self, pin, freq, *, duty_ns = None, duty_u16 = None):
    self.pwm = machine.PWM(machine.Pin(pin), freq=freq)

    if duty_ns != None:
      if duty_u16 != None:
        raise Exception ("duty_ns and duty_u16 can not be specified together!")
      self.pwm.duty_ns(duty_ns)
    elif duty_u16 != None:
      self.pwm.duty_u16(duty_u16)


  def deinit(self):
    self.pwm.deinit()

  def freq(self, value = None):
    if value == None:
      return self.pwm.freq()
    else:
      return self.pwm.freq(value)
  
  def duty_u16(self, value = None):
    if value == None:
      return self.pwm.duty_u16()
    else:
      return self.pwm.duty_u16(value)
  
  def duty_ns(self, value = None):
    if value == None:
      return self.pwm.duty_ns()
    else:
      return self.pwm.duty_ns(value)


class PCA:
  def __init__(self, sda, scl, driver, freq, *, duty_ns = None, duty_u16 = None):
    self.driver = driver
    self.pca = PCA9685(machine.I2C(sda = sda, scl = scl))
    self.pca.freq(freq)
    if duty_ns != None:
      if duty_u16 != None:
        raise Exception ("duty_ns and duty_u16 can not be specified together!")
      self.pca.duty(driver, self.nsToU12_(duty_ns))
    elif duty_u16 != None:
      self.pca.duty(driver, duty_u16 >> 4)
    
  def deinit(self):
    self.pca.reset()

  def nsToU12_(self, duty_ns):
    return int(self.freq() * duty_ns * 0.000004095)
  
  def u12ToNS_(self, value):
    return int(200000000 * value / (self.freq() * 819))
  
  def freq(self, value = None):
    return self.pca.freq(value)
  
  def duty_ns(self, value = None):
    if value == None:
      return self.u12ToNS_(self.pca.duty(self.driver))
    self.pca.duty(self.driver, self.nsToU12_(value))

  def duty_u16(self, value = None):
    if value == None:
      return self.pca.duty(self.driver) << 4
    self.pca.duty(self.driver, value >> 4)


class Servo:
  class Specs:
    def __init__(self, freq, u16_min, u16_max, range):
      self.freq = freq
      self.min = u16_min
      self.max = u16_max
      self.range = range
  
  class Tweak:
    def __init__(self, angle, u16_offset, invert):
      self.angle = angle
      self.offset = u16_offset
      self.invert = invert
  
  class Domain:
    def __init__(self, u16_min, u16_max):
      self.min = u16_min
      self.max = u16_max
  
  def __init__(self, pwm, specs, tweak, domain = None):
    if domain == None:
      domain = Servo.Domain(specs.min, specs.max)

    self.pwm = pwm
    self.specs = specs
    self.tweak = tweak
    self.domain = domain

    self.init()

  def angleToDuty_(self, angle):
    u16 = self.specs.min + angle * ( self.specs.max - self.specs.min ) / self.specs.range + self.tweak.offset

    if u16 > self.domain.max:
      u16 = self.domain.max
    elif u16 < self.domain.min:
      u16 = self.domain.min

    return int(u16)


  def init(self):
    self.move(0)

  def move(self, angle):
    self.angle = angle
    self.pwm.duty_u16(self.angleToDuty_(( -angle if self.tweak.invert else angle ) + self.tweak.angle))

  def current(self):
    return self.angle


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
    moves.append((servos[move[0]], move[1]))

  moves_(moves, step)

