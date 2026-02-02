import random
import shared

from types import SimpleNamespace

from shared import devices, RAINBOW, sleep


def callback_(helper, events, duration):
  sleep(helper.timestamp)

  helper.timestamp += duration
  
  for event in events:
    if event[1] !=-1:
      devices.buzzers.off()
      if event[1] != 0:
        devices.buzzers.play(int(event[1]))
        helper.led += 1
        
  devices.rgbs.setValue(helper.led, RAINBOW[helper.led % len(RAINBOW)]).write()
  devices.rgbs.setValue(helper.led + 1,(0,0,0)).write()
  
  if (helper.timestamp - helper.start) > PANTHER_DELAY_ * helper.pantherPict and duration >= .35:
    devices.oleds.fill(0).show()
    devices.oleds.draw(shared.unpack(PANTHER_[helper.pantherPict % len(PANTHER_)]), 128).show()
    helper.pantherPict += 1


def launch(timestamp):
  helper = SimpleNamespace(pantherPict = 0, led = random.randrange(len(RAINBOW)))
  
  helper.start = helper.timestamp = timestamp + 1
  
  shared.polyphonicPlay(VOICES_, 120, helper, callback_)

  TEXT = " " * 14 + "That's all folks!" + " " * 16

  devices.lcds.backlightOn()

  for i in range(64):
    devices.rgbs.setValue(((helper.led + (i // 8)) % 8),(0,0,0)).write()
    devices.oleds.scroll(0, 1).show()
    devices.lcds.moveTo(0,0).putString(TEXT[i//2:i//2+16])
    helper.timestamp += 0.07
    sleep(helper.timestamp)

  devices.oleds.fill(0).show()
  devices.lcds.backlightOff()
  devices.rgbs.fill((0, 0, 0)).write()
  
  return helper.timestamp


PANTHER_ = (
  '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'
)

VOICES_ = ("""
  D#43, E44 R4, F#43, G44 R4, D#43, E43,-2, R2, F#43, G43,-2, R2, C53, B43,-2, R2, E43, G43,-2, R2, B43, Bb45-3, A43, G43, E43, D43, E43,-4 R5-3,
  D#43, E44 R4, F#43, G44 R4, D#43, E43,-2, R2, F#43, G43,-2, R2, C53, B43,-2, R2, E43, G43,-2, R2, E53, Eb56.. R4,
  D#43, E44 R4, F#43, G44 R4, D#43, E43,-2, R2, F#43, G43,-2, R2, C53, B43,-2, R2, E43, G43,-2, R2, B43, Bb45-3, A43, G43, E43, D43, E43,-4 R5-4,
  R3... Eb51 E54, D53, B44, A43, G44, E43, Bb42 A43. Bb42 A43. Bb42 A43. Bb42 A43. G43, E43, D43, E44, E43,-5 R6
  F#44, G43,-3 R3-5 A44, Bb43-4-3 C#53, D54, F55 -4, Eb53, Db54, Bb44, -4.
  R4. G43, Bb42 C52 Bb42 G42 A44, G43, -4 R4, Bb43, Db52 Eb52 Db52 Bb42 C54, Bb44, -4, G44, F43,-6.-4, F#44, G43
  R5 G43, Bb44, C53, D54, D53, Db53, C53, Bb43, G44, Bb43, R4, G43, Bb44, C54, Db54, Db54, C54, Bb44, G45. F44, D43, -4 R5.
  G42 Bb42 R3 Bb44 F#42 A42 R3 A44 G44
""",)

PANTHER_DELAY_ = 60 // len(PANTHER_)
