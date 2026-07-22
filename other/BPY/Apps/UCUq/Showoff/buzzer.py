import random

import ucuq

STANDARD_RATIO = 0.5
TARGET_DURATION = 2.5  # seconds, harmonized length for every effect below


def singleToneEffect_(buzzer, frequency=440, duration=TARGET_DURATION):
  buzzer.on(frequency)
  ucuq.sleep(duration)


def volumeFadeEffect_(buzzer, frequency=440, steps=40, duration=TARGET_DURATION):
  buzzer.on(frequency)
  ratioBackup = buzzer.ratio()

  sets = tuple(tuple(range(*set)) for set in ((50, 96), (95, 4, -1), (5, 51)))

  for set in sets:
    for ratio in set:
      buzzer.ratio(ratio / 100)
      ucuq.sleep(.02)

  buzzer.ratio(ratioBackup)


def morseEffect_(buzzer, frequency=1000, duration=TARGET_DURATION):
  # Suite d'impulsions courtes et longues, rythme generique façon morse
  pattern = [1, 1, 1, 2, 2, 2, 1, 1, 1]
  unit = duration / sum(pattern)

  for i, length in enumerate(pattern):
    buzzer.on(frequency)
    ucuq.sleep(unit * length / 2)
    buzzer.off()
    ucuq.sleep(unit * length / 3)


def alarmEffect_(buzzer, freqLow=800, freqHigh=1200, repetitions=6, duration=TARGET_DURATION):
  pause = duration / (repetitions * 2)
  for rep in range(repetitions):
    buzzer.on(freqLow)
    ucuq.sleep(pause)
    buzzer.on(freqHigh)
    ucuq.sleep(pause)


def arpeggioEffect_(buzzer, duration=TARGET_DURATION):
  notes = [262, 294, 330, 392, 440, 392, 330, 294]
  pause = duration / len(notes)
  for freq in notes:
    buzzer.on(freq)
    ucuq.sleep(pause)


def sweepEffect_(buzzer, startFreq=200, endFreq=2000, steps=60, duration=TARGET_DURATION):
  pause = duration / steps
  for i in range(steps):
    freq = int(startFreq + (endFreq - startFreq) * i / (steps - 1))
    buzzer.on(freq)
    ucuq.sleep(pause)


def sirenEffect_(buzzer, lowFreq=400, highFreq=1200, cycles=3, duration=TARGET_DURATION):
  stepsPerCycle = 20
  totalSteps = cycles * stepsPerCycle * 2
  pause = duration / totalSteps

  for cycle in range(cycles):
    for i in range(stepsPerCycle):
      freq = int(lowFreq + (highFreq - lowFreq) * i / (stepsPerCycle - 1))
      buzzer.on(freq)
      ucuq.sleep(pause)
    for i in range(stepsPerCycle):
      freq = int(highFreq - (highFreq - lowFreq) * i / (stepsPerCycle - 1))
      buzzer.on(freq)
      ucuq.sleep(pause)


def policeSirenEffect_(buzzer, lowFreq=600, highFreq=1600, bursts=6, duration=TARGET_DURATION):
  stepsPerBurst = 15
  totalSteps = bursts * stepsPerBurst
  pause = duration / totalSteps

  for burst in range(bursts):
    for i in range(stepsPerBurst):
      freq = int(lowFreq + (highFreq - lowFreq) * i / (stepsPerBurst - 1))
      buzzer.on(freq)
      ucuq.sleep(pause)


def chiptuneEffect_(buzzer, notesCount=24, duration=TARGET_DURATION):
  scale = [262, 294, 330, 349, 392, 440, 494, 523]
  pause = duration / notesCount

  for i in range(notesCount):
    freq = random.choice(scale)
    buzzer.on(freq)
    ucuq.sleep(pause)


def launch():
  buzzer = ucuq.ravel.Buzzer()

  singleToneEffect_(buzzer)
  morseEffect_(buzzer)
  alarmEffect_(buzzer)
  arpeggioEffect_(buzzer)
  sweepEffect_(buzzer)
  sirenEffect_(buzzer)
  policeSirenEffect_(buzzer)
  volumeFadeEffect_(buzzer)
  chiptuneEffect_(buzzer)

  buzzer.off()
