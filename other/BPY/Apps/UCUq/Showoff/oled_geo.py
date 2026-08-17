import math
import random

import ucuq

WIDTH_ = ucuq.ravel.OLED_WIDTH
HEIGHT_ = ucuq.ravel.OLED_HEIGHT


def runTimedLoop(duration, frameDelay):
  iterations = int(duration / frameDelay)
  for _ in range(iterations):
    ucuq.sleepStart()
    yield
    ucuq.sleepWait(frameDelay)


def animStarfield(oled, duration=2.0):
  width = WIDTH_
  height = HEIGHT_
  frameDelay = 0.03

  stars = []
  for _ in range(60):
    stars.append([
      (random.random()*2 - 1),
      (random.random()*2 - 1),
      (random.random()*2 + 0.2),
      (random.random()*0.04 - 0.02),
      (random.random()*0.04 - 0.02) 
    ])

  angle = 0.0

  for _ in runTimedLoop(duration, frameDelay):
    oled.fill(0)

    angle += 0.01

    cosA = math.cos(angle)
    sinA = math.sin(angle)

    for s in stars:
      x, y, z, vx, vy = s

      x += vx
      y += vy

      rx = x*cosA - y*sinA
      ry = x*sinA + y*cosA

      z -= 0.04

      if z <= 0.1 or abs(rx) > 2 or abs(ry) > 2:
        s[0] = random.random()*2 - 1
        s[1] = random.random()*2 - 1
        s[2] = random.random()*2 + 0.2
        s[3] = random.random()*0.04 - 0.02
        s[4] = random.random()*0.04 - 0.02
        continue

      sx = int(width/2  + (rx/z) * 45)
      sy = int(height/2 + (ry/z) * 30)

      if 0 <= sx < width and 0 <= sy < height:
        oled.pixel(sx, sy, 1)

      s[0], s[1], s[2] = x, y, z

    oled.show()


def animTunnel(oled, duration=2.0):
  width = WIDTH_
  height = HEIGHT_
  frameDelay = 0.03
  t = 0.0

  for _ in runTimedLoop(duration, frameDelay):
    oled.fill(0)
    for y in range(height):
      for x in range(width):
        dx = x - width/2
        dy = y - height/2
        dist = math.sqrt(dx*dx + dy*dy)
        angle = math.atan2(dy, dx)
        v = math.sin(dist*0.15 - t + angle*3)
        oled.pixel(x, y, 1 if v > 0 else 0)
    oled.show()
    t += 0.15


def animFire(oled, duration=2.0):
  width = WIDTH_
  height = HEIGHT_
  frameDelay = 0.03

  buf = [[0]*width for _ in range(height)]

  for _ in runTimedLoop(duration, frameDelay):
    for x in range(width):
      buf[height-1][x] = 1 if random.random() > 0.5 else 0
    for y in range(height-1):
      for x in range(width):
        s = buf[y+1][x]
        if x > 0: s += buf[y+1][x-1]
        if x < width-1: s += buf[y+1][x+1]
        buf[y][x] = 1 if s >= 2 else 0
    oled.fill(0)
    for y in range(height):
      for x in range(width):
        if buf[y][x]:
          oled.pixel(x, y, 1)
    oled.show()


def animMetaballs(oled, duration=2.0):
  width = WIDTH_
  height = HEIGHT_
  frameDelay = 0.03

  balls = [
    [width/3, height/2, 1.2, 0.8],
    [2*width/3, height/2, -1.0, -0.6],
    [width/2, height/3, 0.7, -1.1]
  ]

  for _ in runTimedLoop(duration, frameDelay):
    oled.fill(0)
    for b in balls:
      b[0] += b[2]
      b[1] += b[3]
      if b[0] < 0 or b[0] >= width: b[2] = -b[2]
      if b[1] < 0 or b[1] >= height: b[3] = -b[3]
    for y in range(height):
      for x in range(width):
        v = 0
        for bx, by, _, _ in balls:
          dx = x - bx
          dy = y - by
          v += 1.0 / (dx*dx + dy*dy + 1)
        oled.pixel(x, y, 1 if v > 0.03 else 0)
    oled.show()


def animMatrixRain(oled, duration=2.0):
  width = WIDTH_
  height = HEIGHT_
  frameDelay = 0.05

  cols = [0] * width

  for _ in runTimedLoop(duration, frameDelay):
    oled.fill(0)
    for x in range(width):
      y = cols[x]
      oled.pixel(x, y, 1)
      cols[x] += 1
      if cols[x] >= height or random.random() > 0.95:
        cols[x] = 0
    oled.show()


def animLightning(oled, duration=2.0):
  width = WIDTH_
  height = HEIGHT_
  frameDelay = 0.05

  for _ in runTimedLoop(duration, frameDelay):
    oled.fill(0)
    x = int(random.random() * width)
    for y in range(height):
      oled.pixel(x, y, 1)
      x += int(random.random()*3 - 1)
      x = max(x, 0)
      if x >= width: x = width-1
    oled.show()


def animWaves(oled, duration=2.0):
  width = WIDTH_
  height = HEIGHT_
  frameDelay = 0.03
  t = 0.0

  for _ in runTimedLoop(duration, frameDelay):
    oled.fill(0)
    for x in range(width):
      y = int(height/2 + math.sin(x*0.15 + t) * 20)
      oled.pixel(x, y, 1)
    oled.show()
    t += 0.2


def animSpiral(oled, duration=2.0):
  width = WIDTH_
  height = HEIGHT_
  frameDelay = 0.03
  t = 0.0

  for _ in runTimedLoop(duration, frameDelay):
    oled.fill(0)
    for i in range(200):
      a = i * 0.1 + t
      r = 2 * i
      x = int(width/2  + math.cos(a) * r * 0.05)
      y = int(height/2 + math.sin(a) * r * 0.05)
      if 0 <= x < width and 0 <= y < height:
        oled.pixel(x, y, 1)
    oled.show()
    t += 0.1


def animGravityParticles(oled, duration=2.0):
  width = WIDTH_
  height = HEIGHT_
  frameDelay = 0.03

  particles = []
  for _ in range(20):
    particles.append([
      random.random()*width,
      random.random()*height,
      random.random()*2 - 1,
      random.random()*2 - 1
    ])

  cx = width/2
  cy = height/2

  for _ in runTimedLoop(duration, frameDelay):
    oled.fill(0)
    for p in particles:
      px, py, vx, vy = p
      dx = cx - px
      dy = cy - py
      dist = math.sqrt(dx*dx + dy*dy) + 1
      ax = dx / dist * 0.2
      ay = dy / dist * 0.2
      vx += ax
      vy += ay
      px += vx
      py += vy
      p[0], p[1], p[2], p[3] = px, py, vx, vy
      if 0 <= int(px) < width and 0 <= int(py) < height:
        oled.pixel(int(px), int(py), 1)
    oled.show()


def animPlasmaFractal(oled, duration=2.0):
  width = WIDTH_
  height = HEIGHT_
  frameDelay = 0.03
  t = 0.0

  for _ in runTimedLoop(duration, frameDelay):
    oled.fill(0)
    for y in range(height):
      for x in range(width):
        v = (math.sin(x*0.1 + t) +
          math.sin(y*0.13 - t*1.2) +
          math.sin((x+y)*0.07 + t*0.7))
        oled.pixel(x, y, 1 if v > 0 else 0)
    oled.show()
    t += 0.15


def animConcentricWaves(oled, duration=2.0):
  width = WIDTH_
  height = HEIGHT_
  frameDelay = 0.03
  t = 0.0

  cx = width/2
  cy = height/2

  for _ in runTimedLoop(duration, frameDelay):
    oled.fill(0)
    for y in range(height):
      for x in range(width):
        dx = x - cx
        dy = y - cy
        dist = math.sqrt(dx*dx + dy*dy)
        v = math.sin(dist*0.2 - t)
        oled.pixel(x, y, 1 if v > 0 else 0)
    oled.show()
    t += 0.15

def animNeuronal(oled, duration=2.0):
  width = WIDTH_
  height = HEIGHT_
  frameDelay = 0.03

  nodes = []
  for _ in range(12):
    nodes.append([
      random.random()*width,
      random.random()*height,
      random.random()*2 - 1,
      random.random()*2 - 1
    ])

  for _ in runTimedLoop(duration, frameDelay):
    oled.fill(0)
    for n in nodes:
      x, y, vx, vy = n
      x += vx
      y += vy
      if x < 0 or x >= width: vx = -vx
      if y < 0 or y >= height: vy = -vy
      n[0], n[1], n[2], n[3] = x, y, vx, vy
      oled.pixel(int(x), int(y), 1)
    for i in range(len(nodes)):
      for j in range(i+1, len(nodes)):
        x1, y1, _, _ = nodes[i]
        x2, y2, _, _ = nodes[j]
        dx = x2 - x1
        dy = y2 - y1
        dist2 = dx*dx + dy*dy
        if dist2 < 400:
          oled.line(int(x1), int(y1), int(x2), int(y2), 1)
    oled.show()


def animOpticalDistortion(oled, duration=2.0):
  width = WIDTH_
  height = HEIGHT_
  frameDelay = 0.03
  t = 0.0

  cx = width/2
  cy = height/2

  for _ in runTimedLoop(duration, frameDelay):
    oled.fill(0)
    for y in range(height):
      for x in range(width):
        dx = x - cx
        dy = y - cy
        dist = math.sqrt(dx*dx + dy*dy) + 1
        angle = math.atan2(dy, dx)
        v = math.sin(dist*0.15 + t + angle*4) / dist
        oled.pixel(x, y, 1 if v > 0.02 else 0)
    oled.show()
    t += 0.12


def animVectorField(oled, duration=2.0):
  width = WIDTH_
  height = HEIGHT_
  frameDelay = 0.05
  t = 0.0

  for _ in runTimedLoop(duration, frameDelay):
    oled.fill(0)
    step = 8
    for y in range(0, height, step):
      for x in range(0, width, step):
        vx = math.sin(x*0.1 + t) * 3
        vy = math.cos(y*0.1 - t) * 3
        x2 = int(x + vx)
        y2 = int(y + vy)
        oled.pixel(x, y, 1)
        if 0 <= x2 < width and 0 <= y2 < height:
          oled.line(x, y, x2, y2, 1)
    oled.show()
    t += 0.15


WHOLE_ = (
  animStarfield,
  animTunnel,
  animFire,
  animMetaballs,
  animMatrixRain,
  animLightning,
  animWaves,
  animSpiral,
  animGravityParticles,
  animPlasmaFractal,
  animConcentricWaves,
  animNeuronal,
  animOpticalDistortion,
  animVectorField
)

SHORT_ = (
  animTunnel,
  animLightning,
  animSpiral,
  animPlasmaFractal,
  animNeuronal,
  animVectorField
)

def launch(whole):
  if whole:
    list = WHOLE_
  else:
    list = SHORT_  

  oled = ucuq.ravel.OLED()

  for anim in list:
    anim(oled)

  oled.fill(0).show()
