import random

import ucuq

NUM_LEDS = ucuq.ravel.RING_SIZE
MAX_LEVEL = ucuq.ravel.RING_MAX
TARGET_DURATION = 2.0


def hueToColor(hue):
  segment = int(hue) % 6
  fraction = hue - int(hue)
  highLevel = int(MAX_LEVEL * fraction)
  lowLevel = MAX_LEVEL - highLevel

  if segment == 0:
    return (MAX_LEVEL, highLevel, 0)
  elif segment == 1:
    return (lowLevel, MAX_LEVEL, 0)
  elif segment == 2:
    return (0, MAX_LEVEL, highLevel)
  elif segment == 3:
    return (0, lowLevel, MAX_LEVEL)
  elif segment == 4:
    return (highLevel, 0, MAX_LEVEL)
  else:
    return (MAX_LEVEL, 0, lowLevel)


def wheelAnimation_(ring, duration=TARGET_DURATION):
  palette = [
    (MAX_LEVEL, 0, 0),
    (MAX_LEVEL, MAX_LEVEL // 2, 0),
    (MAX_LEVEL, MAX_LEVEL, 0),
    (0, MAX_LEVEL, 0),
    (0, MAX_LEVEL, MAX_LEVEL),
    (0, 0, MAX_LEVEL),
    (MAX_LEVEL // 2, 0, MAX_LEVEL),
    (MAX_LEVEL, 0, MAX_LEVEL),
  ]

  for x in range(NUM_LEDS):
    ring.setValue(x, palette[x]).write()
    ucuq.sleep(duration  /NUM_LEDS)

  ring.fill((0, 0, 0)).write()


def blinkAnimation_(ring, repetitions=5, duration=TARGET_DURATION):
  ledColors = [hueToColor(x / NUM_LEDS * 6) for x in range(NUM_LEDS)]
  steps = repetitions * 2
  pause = duration / steps

  for rep in range(repetitions):
    for x in range(NUM_LEDS):
      ring.setValue(x, ledColors[x] if x % 2 == 0 else (0, 0, 0))

    ring.write()
    ucuq.sleep(pause)

    for x in range(NUM_LEDS):
      ring.setValue(x, ledColors[x] if x % 2 == 1 else (0, 0, 0))

    ring.write()
    ucuq.sleep(pause)

  ring.fill((0, 0, 0)).write()


def fillAnimation_(ring, holdFraction=0.15, duration=TARGET_DURATION):
  palette = [
    (MAX_LEVEL, 0, 0),
    (MAX_LEVEL, MAX_LEVEL // 2, 0),
    (MAX_LEVEL, MAX_LEVEL, 0),
    (0, MAX_LEVEL, 0),
    (0, MAX_LEVEL, MAX_LEVEL),
    (0, 0, MAX_LEVEL),
    (MAX_LEVEL // 2, 0, MAX_LEVEL),
    (MAX_LEVEL, 0, MAX_LEVEL),
  ]
  hold = duration * holdFraction
  steps = 2 * NUM_LEDS
  pause = (duration - hold) / steps

  ring.fill((0, 0, 0)).write()

  for x in range(NUM_LEDS):
    ring.setValue(x, palette[x]).write()
    ucuq.sleep(pause)

  ucuq.sleep(hold)

  for x in range(NUM_LEDS - 1, -1, -1):
    ring.setValue(x, (0, 0, 0)).write()
    ucuq.sleep(pause)


def breathingAnimation_(ring, cycles=2, duration=TARGET_DURATION):
  ledColors = [hueToColor(x / NUM_LEDS * 6) for x in range(NUM_LEDS)]
  stepsPerCycle = 2 * (MAX_LEVEL + 1)
  pause = duration / (cycles * stepsPerCycle)

  for cycle in range(cycles):
    for level in range(0, MAX_LEVEL + 1):
      factor = level / MAX_LEVEL
      for x in range(NUM_LEDS):
        r, g, b = ledColors[x]
        ring.setValue(x, (int(r * factor), int(g * factor), int(b * factor)))
      ring.write()
      ucuq.sleep(pause)

    for level in range(MAX_LEVEL, -1, -1):
      factor = level / MAX_LEVEL
      for x in range(NUM_LEDS):
        r, g, b = ledColors[x]
        ring.setValue(x, (int(r * factor), int(g * factor), int(b * factor)))
      ring.write()
      ucuq.sleep(pause)


def chaseAnimation_(ring, laps=2, bandWidth=3, duration=TARGET_DURATION):
  steps = laps * NUM_LEDS
  pause = duration / steps

  ring.fill((0, 0, 0)).write()

  for lap in range(laps):
    for x in range(NUM_LEDS):
      ring.fill((0, 0, 0))
      for offset in range(bandWidth):
        index = (x + offset) % NUM_LEDS
        hue = index / NUM_LEDS * 6
        ring.setValue(index, hueToColor(hue))
      ring.write()
      ucuq.sleep(pause)

  ring.fill((0, 0, 0)).write()


def cometAnimation_(ring, laps=2, tailLength=5, duration=TARGET_DURATION):
  steps = laps * NUM_LEDS
  pause = duration / steps

  for lap in range(laps):
    for x in range(NUM_LEDS):
      for i in range(NUM_LEDS):
        ring.setValue(i, (0, 0, 0))
      for d in range(tailLength):
        index = (x - d) % NUM_LEDS
        hue = index / NUM_LEDS * 6
        r, g, b = hueToColor(hue)
        factor = (tailLength - d) / tailLength
        ring.setValue(index, (int(r * factor), int(g * factor), int(b * factor)))
      ring.write()
      ucuq.sleep(pause)

  ring.fill((0, 0, 0)).write()


def rainbowAnimation_(ring, laps=1, duration=TARGET_DURATION):
  steps = laps * NUM_LEDS
  pause = duration / steps

  for lap in range(laps):
    for shift in range(NUM_LEDS):
      for x in range(NUM_LEDS):
        hue = ((x + shift) % NUM_LEDS) / NUM_LEDS * 6
        ring.setValue(x, hueToColor(hue))
      ring.write()
      ucuq.sleep(pause)

  ring.fill((0, 0, 0)).write()


def twinkleAnimation_(ring, sparks=25, duration=TARGET_DURATION):
  pause = duration / sparks

  for i in range(sparks):
    ring.fill((0, 0, 0))
    litCount = random.randint(1, 3)
    for _ in range(litCount):
      index = random.randrange(NUM_LEDS)
      hue = random.random() * 6
      ring.setValue(index, hueToColor(hue))
    ring.write()
    ucuq.sleep(pause)

  ring.fill((0, 0, 0)).write()


def fireAnimation_(ring, frames=30, duration=TARGET_DURATION):
  pause = duration / frames

  for frame in range(frames):
    for x in range(NUM_LEDS):
      flicker = random.uniform(0.5, 1.0)
      red = int(MAX_LEVEL * flicker)
      green = int(MAX_LEVEL * 0.4 * flicker)
      ring.setValue(x, (red, green, 0))
    ring.write()
    ucuq.sleep(pause)

  ring.fill((0, 0, 0)).write()


def sonarPulseAnimation_(ring, pulses=3, duration=TARGET_DURATION):
  maxDistance = NUM_LEDS // 2
  steps = pulses * (maxDistance + 1)
  pause = duration / steps

  for p in range(pulses):
    origin = random.randrange(NUM_LEDS)
    color = hueToColor(random.random() * 6)
    r, g, b = color
    for distance in range(maxDistance + 1):
      ring.fill((0, 0, 0))
      factor = 1 - distance / maxDistance
      for offset in (-distance, distance):
        index = (origin + offset) % NUM_LEDS
        ring.setValue(index, (int(r * factor), int(g * factor), int(b * factor)))
      ring.write()
      ucuq.sleep(pause)

  ring.fill((0, 0, 0)).write()


def meteorRainAnimation_(ring, meteors=3, laps=1, tailLength=4, duration=TARGET_DURATION):
  steps = laps * NUM_LEDS
  pause = duration / steps
  spacing = NUM_LEDS // meteors

  for lap in range(laps):
    for x in range(NUM_LEDS):
      ring.fill((0, 0, 0))
      for m in range(meteors):
        headIndex = (x + m * spacing) % NUM_LEDS
        hue = (headIndex / NUM_LEDS * 6 + m * 2) % 6
        r, g, b = hueToColor(hue)
        for d in range(tailLength):
          index = (headIndex - d) % NUM_LEDS
          factor = (tailLength - d) / tailLength
          ring.setValue(index, (int(r * factor), int(g * factor), int(b * factor)))
      ring.write()
      ucuq.sleep(pause)

  ring.fill((0, 0, 0)).write()


def discoAnimation_(ring, frames=20, duration=TARGET_DURATION):
  pause = duration / frames

  for frame in range(frames):
    for x in range(NUM_LEDS):
      hue = random.random() * 6
      ring.setValue(x, hueToColor(hue))
    ring.write()
    ucuq.sleep(pause)

  ring.fill((0, 0, 0)).write()


def launch():
  ring = ucuq.ravel.Ring()
  wheelAnimation_(ring)
  blinkAnimation_(ring)
  twinkleAnimation_(ring)
  fillAnimation_(ring)
  breathingAnimation_(ring)
  sonarPulseAnimation_(ring)
  chaseAnimation_(ring)
  fireAnimation_(ring)
  cometAnimation_(ring)
  meteorRainAnimation_(ring)
  rainbowAnimation_(ring)
  discoAnimation_(ring)
  ring.fill((0, 0, 0))
  ring.write()
