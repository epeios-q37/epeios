import base64  # noqa: I001
import copy
import types
import zlib

import shared
import ucuq


from show import sleepUntil as sleepUntil_
from fractions import Fraction

# No debug if == 0
DEBUG_DURATION_ = 0

LCD_WIDTH_ = ucuq.ravel.LCD_WIDTH

OLED_HEIGHT_ = ucuq.ravel.OLED_HEIGHT
OLED_WIDTH_ = ucuq.ravel.OLED_WIDTH

PIANO_ROLL_HEIGHT_ = 57
FAST_SCROLL_HEIGHT_= 9 * PIANO_ROLL_HEIGHT_ // 10
PIANO_ROLL_MARKER_WIDTH_ = 20
PIANO_ROLL_VOICE_WIDTH_ = 39
PIANO_ROLL_VOICES_START_ = (2, 44, 86)
PIANO_ROLL_SEPARATOR_POSITIONS_ = (0, 42, 84, 126)


REGULAR_SCROLL_DELAY_ = .10
START_SCROLL_DELAY_ = .05

LCD_TITLE_DELAY_ = 1/3

RING_RAINBOW_DELAY_ = 1/3

START_DELAY_ = (FAST_SCROLL_HEIGHT_ * START_SCROLL_DELAY_) + REGULAR_SCROLL_DELAY_ * (PIANO_ROLL_HEIGHT_ - FAST_SCROLL_HEIGHT_)

COMMIT_MAX_DELAY_ = 1/2

OLED_ANTICIPATION_ = 0
KIT_COUNT_ = 3

NOTE_UP_CHARMAP_ = (
  0b00001,
  0b00001,
  0b00001,
  0b00001,
  0b01111,
  0b11111,
  0b01110,
  0b00000,
)

NOTE_DOWN_CHARMAP_ = (
  0b00000,
  0b00001,
  0b00001,
  0b00001,
  0b00001,
  0b01111,
  0b11111,
  0b01110,
)


def isDebug_():
  return DEBUG_DURATION_ != 0


def unpack_(ns):
  return vars(ns).values()


def decompressVoiceString_(compressedString):
  decoded_base64 = base64.b64decode(compressedString.encode('ascii'))
  decompressed_bytes = zlib.decompress(decoded_base64)

  return decompressed_bytes.decode('utf-8')


def parseVoice_(decompressedString):
  if not decompressedString.strip():
    return []
      
  note_array = []
  tokens = decompressedString.split(" ")
  
  for token in tokens:
    if not token:
        continue
    midi_str, fraction_str = token.split(":")
    midi_note = int(midi_str)
    
    num, den = map(int, (fraction_str if '/' in fraction_str else fraction_str + "/1").split("/"))
    duration_fraction = Fraction(num, den)
    
    note_array.append([midi_note, duration_fraction])
      
  return note_array


def buzzerCallback_(note, turn, prev, buzzer):
  if note != 0 and prev[turn] == note:
    buzzer.off()
    ucuq.getDevice()[turn].sleep(0.015)
  else:
    prev[turn] = note

  buzzer.play(note)


def getBuzzerEvents_(voice, turn, prev, buzzer):
  events=[(lambda: None, START_DELAY_)]
  duration = 0

  for note in voice:
    events.append((lambda note = note, turn = turn: buzzerCallback_(note[0], turn, prev, buzzer), note[1]))
    duration += note[1]

    if isDebug_():  # noqa: SIM102
      if duration >= DEBUG_DURATION_:
        events.append((lambda turn = turn: buzzerCallback_(0, turn, prev, buzzer), 0))
        break

  return events, duration


def ringsActiveNotesCallback_(note, turn, counter, rings):
  spots = VOICES_MAP_[turn]
  
  for spot in spots:
    rings.setValue(spot, (0, 0, 0))
    if note != 0:
      rings.setValue(spots[counter % len(spots)], VOICES_COLORS_[turn])

  rings.write()


def getRingsActiveNotesEvents_(voice, turn, rings):
  events=[(lambda: None, START_DELAY_)]
  duration = 0
  noteCounter = 0

  for note in voice:
    events.append((lambda note = note, turn = turn, counter = noteCounter: ringsActiveNotesCallback_(note[0], turn, counter, rings), note[1]))
    duration += note[1]

    if isDebug_():  # noqa: SIM102
      if duration >= DEBUG_DURATION_:
        events.append((lambda turn = turn: ringsActiveNotesCallback_(0, turn, 0, rings), 0))
        break
      
    if note[0]:
      noteCounter += 1

  return events


def oledComputeNotePos_(turn, note, minNote, maxNote):
  return PIANO_ROLL_VOICES_START_[turn] + ( PIANO_ROLL_VOICE_WIDTH_ - 1 ) * ( note - minNote ) // ( maxNote - minNote )


def oledDrawNote_(index, pitch, minNote, maxNote, oled):
  oled.pixel(oledComputeNotePos_(index, pitch, minNote, maxNote), 0, 1)


def oledDrawMarker_(turn, color, counter, oled):
  width = PIANO_ROLL_VOICE_WIDTH_ - PIANO_ROLL_MARKER_WIDTH_
  trueX = abs((counter % width * 2 ) - width * 2 + width)
  oled.hLine( PIANO_ROLL_VOICES_START_[turn] + trueX, OLED_HEIGHT_ - 1, PIANO_ROLL_MARKER_WIDTH_, color)


def oledDrawSeparators_(counter, oleds):
  for position in PIANO_ROLL_SEPARATOR_POSITIONS_:
    for y in range(OLED_HEIGHT_):
      oleds.pixel(position, y, 1 if ( y + counter ) % ( KIT_COUNT_ * 3 ) == KIT_COUNT_ * 3 // 2 else 0 )


def oledPianoRollCallback_(pitches, tracking, separatorCounter, oleds):
  minNotes, maxNotes = unpack_(tracking.extrema)

  for turn, pitch in enumerate(pitches):
    if pitch:
      oledDrawNote_(turn, pitch, minNotes[turn], maxNotes[turn], oleds)

  for turn, oled in enumerate(oleds):
    oledDrawMarker_(turn, 1, separatorCounter, oled)
  oleds.show()

  for turn, oled in enumerate(oleds):
    pitch = pitches[turn]
    oledDrawMarker_(turn, 0, separatorCounter, oled)
    if pitch:
      oledDrawNote_(turn, pitch, minNotes[turn], maxNotes[turn], oled)

  oleds.scroll(dx=0, dy=1).hLine(0, 0, OLED_WIDTH_, 0).hLine(0, PIANO_ROLL_HEIGHT_, OLED_WIDTH_, 0)
  oledDrawSeparators_(separatorCounter, oleds)


def getExtremaNotes_(voices):
  minNotes = [100] * len(voices)
  maxNotes = [0] * len(voices)

  for i, voice in enumerate(voices):
    for note in voice:
      pitch = note[0]
      if pitch:
        minNotes[i] = min(minNotes[i], pitch)
        maxNotes[i] = max(maxNotes[i], pitch)

  return minNotes, maxNotes


def getPacedNotes_(tracking):
  elapsed = 0
  pacedNotes = []

  voices = copy.deepcopy(tracking.voices)

  while len(voices[0]) and len(voices[1]) and len(voices[2]):
    pitches = (voices[0][0][0], voices[1][0][0], voices[2][0][0])
    start = elapsed < FAST_SCROLL_HEIGHT_ * REGULAR_SCROLL_DELAY_
    pacedNotes.append((pitches, START_SCROLL_DELAY_ if start else REGULAR_SCROLL_DELAY_))
    for voice in voices:
      voice[0][1] -= REGULAR_SCROLL_DELAY_
      while len(voice) and voice[0][1] <= 0:
        if len(voice) > 2:
          voice[1][1] += voice[0][1]
        del voice[0]
    elapsed += REGULAR_SCROLL_DELAY_

    if isDebug_():  # noqa: SIM102
      if elapsed >= DEBUG_DURATION_:
        break

  for _ in range(PIANO_ROLL_HEIGHT_):
    pacedNotes.append(((0,) * len(tracking.voices), START_SCROLL_DELAY_ if start else REGULAR_SCROLL_DELAY_))

  return pacedNotes


def oledActiveNotesCallback_(pitches, tracking, oleds):
  minNotes, maxNotes = unpack_(tracking.extrema)

  for start in PIANO_ROLL_VOICES_START_:
    oleds.rect(start, PIANO_ROLL_HEIGHT_, PIANO_ROLL_VOICE_WIDTH_, OLED_HEIGHT_ - PIANO_ROLL_HEIGHT_, 0, True )

  for index, pitch in enumerate(pitches):
    if pitch:
      oleds.vLine(oledComputeNotePos_(index, pitch, minNotes[index], maxNotes[index]), PIANO_ROLL_HEIGHT_, OLED_HEIGHT_ - PIANO_ROLL_HEIGHT_ - 1, 1)    


def getOLEDEvents_(pacedNotes, tracking, oleds):
  events = []

  for i in range(len(pacedNotes)):
    events.append((
      lambda pacedNotes = pacedNotes, i = i:(
        oledActiveNotesCallback_(pacedNotes[i-PIANO_ROLL_HEIGHT_][0], tracking, oleds) if i >= PIANO_ROLL_HEIGHT_ else None,
        oledPianoRollCallback_(pacedNotes[i][0], tracking, i, oleds),
      ),
      pacedNotes[i][1] - ( OLED_ANTICIPATION_ if i == 0 else 0 )))

  return events


def getLCDActiveNoteEvents_(notes, minNote, maxNote, lcd):
  events=[(lambda: None, START_DELAY_)]
  counter = 0

  for note in notes:
    events.append((
      lambda note = note, counter = counter: (
        lcd.moveTo(9,1).putString(lcd.getForwardPeak(( note[0] - minNote ) * (7 * 5 - 1) // ( maxNote - minNote) , 7 * 5 ) if note[0] else lcd.getEmptyPeak(7 * 5)),
        lcd.moveTo(7, 1).putString(chr(6 + counter % 2) if note[0] else " ")
      ),
      note[1]))
    if note[0]:
      counter += 1

  return events


def ringsRainbowCallback_(counter, rings):
  for index, ring in enumerate(rings):
    color = shared.getRainbowColor(counter + index * len(shared.RAINBOW) // KIT_COUNT_)
    ring.setValue(5, color).setValue(6, color).write()


def getRingsRainbowEvents_(duration, rings):
  events=[(lambda: None, START_DELAY_)]
  elapsed = 0
  counter = 0

  while elapsed < duration:
    events.append((lambda counter = counter: ringsRainbowCallback_(counter, rings), RING_RAINBOW_DELAY_))
    elapsed += RING_RAINBOW_DELAY_
    counter += 1

  return events


def getLCDTitleEvent_(title, counter, lcds):
  string = title[counter % (len(title) - KIT_COUNT_ * LCD_WIDTH_):][:KIT_COUNT_ * LCD_WIDTH_]

  return lambda: (
    lcds[0].moveTo(0,0).putString(string[:LCD_WIDTH_]),
    lcds[1].moveTo(0,0).putString(string[LCD_WIDTH_:][:LCD_WIDTH_]),
    lcds[2].moveTo(0,0).putString(string[LCD_WIDTH_ * 2:][:LCD_WIDTH_])
  )


def getPrologLCDTitleEvents_(title, duration, lcds):
  title = KIT_COUNT_ * LCD_WIDTH_ // 4 * "\06\07\06 " + KIT_COUNT_ * (title + LCD_WIDTH_ * " ")
  counter = 0
  events = []

  while duration > 0 and counter < KIT_COUNT_ * LCD_WIDTH_:
    events.append(
      (
        getLCDTitleEvent_(title, counter, lcds),
        LCD_TITLE_DELAY_
      )
    )

    duration -= LCD_TITLE_DELAY_
    counter += 1

  return events, duration


def getMainLCDTitleEvents_(title, duration, lcds):
  title = KIT_COUNT_ * (title + LCD_WIDTH_ * " ")
  counter = 0
  events = []

  while duration > 0:
    events.append(
    (
      getLCDTitleEvent_(title, counter, lcds),
      LCD_TITLE_DELAY_
      )
    )

    duration -= LCD_TITLE_DELAY_
    counter += 1

  return events


def getLCDTitleEvents_(title, duration, lcds):
  events, duration = getPrologLCDTitleEvents_(title, duration, lcds)
  return events + getMainLCDTitleEvents_(title, duration, lcds)


def getLCDDurationEvents_(duration, lcds):
  events=[(lambda: None, START_DELAY_)]

  for i in range(6 * 5):
    events.append((lambda i = i: lcds.moveTo(0,1).putString(lcds[0].getForwardPeak(i, 6 * 5)), duration / (6 * 5 )))

  return events


def getOLEDDurationEvents_(duration, oleds):
  events=[(lambda: None, START_DELAY_)]

  for y in range(OLED_HEIGHT_):
    events.append((lambda y = y: oleds.vLine(OLED_WIDTH_ -1, 0, y)), duration / OLED_HEIGHT_)

  return events


def getCommitEvents_(duration):
  events = []
  elapsed = 0

  while elapsed <= duration:
    events.append((lambda elapsed=elapsed: (ucuq.commit(), print(elapsed)), COMMIT_MAX_DELAY_))
    elapsed += COMMIT_MAX_DELAY_

  return events


def set(dom):
  html = ""
  for part in PARTS_:
    html += f'<option value="{PARTS_.index(part)}">{part[0][0]}</option>'

  dom.inner("ShowTrios", html)


def sleepCallback_(tracking, user, timestamp):
  if tracking.cumul - user.timestamp >= COMMIT_MAX_DELAY_:
    ucuq.commit()
    user.timestamp = tracking.cumul

  sleepUntil_(timestamp + tracking.cumul, 0)  # The commits are handled directly.


def launch(part, timestamp, devices):
    tracking = types.SimpleNamespace(
    voices = [],
    extrema = types.SimpleNamespace()
  )

    devices.lcds.uploadHPeakChars()\
    .createChar(6, NOTE_UP_CHARMAP_)\
    .createChar(7, NOTE_DOWN_CHARMAP_)

    timestamp = timestamp + 1
    prev = [None] * len(devices.buzzers)

    sleepUntil_(timestamp, 0)

    eventList = []

    maxDuration = 0

    for voice in PARTS_[part][1]:
        tracking.voices.append(parseVoice_(decompressVoiceString_(voice)))

    tracking.extrema.minNotes, tracking.extrema.maxNotes = getExtremaNotes_(tracking.voices)

    pacedNotes = getPacedNotes_(tracking)

    for turn, voice in enumerate(tracking.voices):
        events, duration = getBuzzerEvents_(voice, turn, prev, devices.buzzers[turn])
        eventList.append(events)
        eventList.append(getRingsActiveNotesEvents_(voice, turn, devices.rings))
        maxDuration = max(maxDuration, duration)

    tracking.maxDuration = maxDuration

    eventList.append(getOLEDEvents_(pacedNotes, tracking, devices.oleds))
    eventList.append(getLCDTitleEvents_(PARTS_[part][0][1], maxDuration + START_DELAY_, devices.lcds))
    eventList.append(getLCDDurationEvents_(maxDuration, devices.lcds))
    for turn, lcd in enumerate(devices.lcds):
        eventList.append(getLCDActiveNoteEvents_(tracking.voices[turn], tracking.extrema.minNotes[turn], tracking.extrema.maxNotes[turn], lcd))
    eventList.append(getRingsRainbowEvents_(maxDuration, devices.rings))

    cb = ucuq.getCommitBehavior()

    if True:
        #    eventList.append(getCommitEvents_(maxDuration + START_DELAY_))
        cb = ucuq.setCommitBehavior(ucuq.CB_MANUAL)

    devices.lcds.backlightOn()

    timestamp += ucuq.playEvents(
    eventList,
    lambda tracking, user: sleepCallback_(tracking, user, timestamp),
    timestamp = 0
  )

    devices.oleds.fill(0).show()
    devices.lcds.clear().backlightOff()
    devices.rings.fill((0, 0, 0)).write()

    ucuq.setCommitBehavior(cb)

    ucuq.commit()


PARTS_ = (
  (
    ("Titelouze", "Jehan Titelouze * Ave Maris Stella * 3rd verset"),
    (
      "eJyFUtsVwyAIXaUbNAqSxP0HqwKKGHL6E4PAfYB01/Q5U//kmr6Z/9tBfI/tHyWDe5QqaF0/ztklOa0Ei7TScooJG6ZGl/C1g6SPIhG7pIXI+MBJ2itRxHPkHcFirLF/DgHEMSyHOrJeGM0WyYGf8EJQ5JBKyhah5ERmZxkAvLWHhbm8cVVcgUYKnGfEmZ2+k5F5YwEBQiTUW3oOYnlqwTNxhgInLOjN1G35Oyr711/McHYrQh1HLxKAYjt8DgYcQvEMr8/uGksNn4btjCmp5ib1+AHFELlH",
      "eJyNUlsSxCAIu4o3EB/o1vsfbBuoiN12Zn+IGHkkI9PIgTvCgcBb2sC2PJKEmA1o9FgB6YT5tCiDB+dVCnpsHeUsL1tV4MVeRFc4rEQ5aVlvo+eAKKsK8MqqcrodpliDOnXY5k6VE5M2aQJXY7Ys8AdhG49Z7KRJvjWglzWXINn37kJyLsCTZeSbmmnUjxlv0sQCemj6Z73YQd6NtsSaccW58GxP4IzPVxDkRAP39AUH9YHa",
      "eJxtUesZwDAEXKUbFKFpsv9gJeT59c9xxfUIVLweMmADqXhTyy2071lz9gqfjGuKPgswprwWnWlhNPVXzXRoBnv9fxqKz5U/E6clC+Abpc0IHkZam5NlDclVQWrPJoABjWoaFJxiQLRgQF5gU9kF+HWKASFgzkT6gUXtii8scYy/HR6MZ53PIqVv14alT5EeAT6/+2M6",
    ),
  ),
  (
    (
      "BWV 528a",
      "Johann Sebastian Bach * Sonata No. 4 in E minor (BWV 528) * I. Adagio - Vivace",
    ),
    (
      "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",
    ),
  ),
  (
    (
      "BWV 528b",
      "Johann Sebastian Bach * Sonata No. 4 in E minor (BWV 528) * II. Andante",
    ),
    (
      "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",
    ),
  ),
  (
    (
      "BWV 528c",
      "Johann Sebastian Bach * Sonata No. 4 in E minor (BWV 528) * III. Un poco allegro",
    ),
    (
      "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",
    ),
  ),
  (
    ("Ano. Lobt Gott", "Anonymous (18th) * Lobt Gott, ihr Christen, allzugleich"),
    (
      "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",
    ),
  ),
  (
    (
      "BWV 848b",
      "Johann Sebastian Bach * Prelude and Fugue in C-sharp major (BWV 848) * Fugue",
    ),
    (
      "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",
    ),
  ),
  (
    (
      "BWV 847b",
      "Johann Sebastian Bach - Prelude and Fugue in C minor (BWV 847) - Fugue",
    ),
    (
      "eJzNl1luxTAIRbfSHdROPKX7X1irSvGTcgBjy69qPhFcwFyGhK/arlTPzyP8fh/1uCXplkRIjqdVqZC0Pcg1jX1tQ85Pq5evLul5RV2HOKceT5dckDRdh7l3SYZkCbnF8YvtQi7FwSjgWFZ3dQJKQQlKwXI5qXGcpaV47YfmOwc6W416rOMgdCERp9oy6las2FTMPR4ODodOgAq7wOOK3eSYSC6rtblhZIHe6SpoOCFRVOJllVQrNneld/JAagt1qDuGxMw+EyS0IjPgK+NRM6wEHeKAK/lcsSrUQaaumClhPIx5l3fqeKwYoUGfTkMQXGACOQZfi8iO1tmFPLc8o64DHFZZWHDESTN5zW1TQq8uau48OFuNelxnI2isuKi6ssJRYbjuhRwwAQjz/39J2MqMhzocLX/wA/K+Hz19m75vuXue2ThV9efhPHrOLNdxz6wcKsDN414TyMSSgxYVQ463rIe4wtFHX8Z1BOpMpeW569Gza1zixWDsSAOZEsc16WgsofM9v6Bcf8wrPRr9J5zwDciImJw=",
      "eJzFl2FyxCAIha/SG6xGULP3P1g7O41p+ymD7mabn4w+4PFAEu4xyRaDxNsWHt9HifdSdynpJt+WvMNSYFFYEiwbLOGwNO8Ki8CywQKcM+bxmQ4OIjy9N0uLMI7PEMfI1OOr5VVgqUBGdTq+iONhDEro+CJOdDBv5P7D15ZylbhPkRhwqxqJGbJjMUB9pzyeEnqahzgg8UQ+pMlEPbWgejETeMtS5jgcQwjjS47SrHWXa0asIYOdFw2ETiNX3Arj8sXhGeJ0xr6hU+PWVIQeNowzazjGWDssFU1R+cC9k43syGJKY0+yAW1UNG7nDEeN59GZUsJzy0Zn7i4tGznD4niUPbfmugADqY0ECsoQ3RiG+iYwXlLAuPbJ9BdGUWIlgUvPr4J2NdYBz0BoOCw6h/PSvg1VKlSpoFCwMiQEmMb1azAQnDhcWWcE4cgMDmSpYFnhi2eII5C3oG8E1WJeygiBrNCBAvllWTgYu44NVvmf2WAWDsauYyOxOtexgbkm8HVmgUW+DvMkCj2t9S0z97DzToXhHXDxjsHbmXScvEvIypnumKqLyOCwoxb8Ks51zvAHU/F8dAJkElgRSE/Kv51/+Q6fHg/YfQ==",
      "eJy1l2uOwzAIhK+yN2gSY5P0/gerdrVxpH5AiJv2J8LDMLzS6VnWtsqs+limv99Pm566bqLlIf+Wur1bDp/9Va2wtHfLGHJbzmPdhlyAU2Hpec2+D3Fmn4/PuWqCTyJWRSxZz33GcKTBIrCAszAWGQL5e2oYWSQU+54ahb1xkxoC5GtZcAb7NK2wYCcYe6Oc4zAWg2fkIZ1E8LuSOErRLchC+ArIDTiZUhg+5JxgSJ/uUr0cBAoKFEwESskV+GRmPcAJShzs7wQyMzVuBWIZBQ3uG2+gf5eMO4npP0Zgv4pcjlxzmEiBYMlDtZTfz5gtgh7a6Mb1KAw2yvqs5zN1zyw6AnMfKCz8zIKPon0UginaR9k+m5968LkWvEIbdhdeLiYKBRuutvEqoOzTCVT2H8GloS8UvXOtWOIiN8x6pODuo1DQ4DPUGKi50cvoHT4KRqLzowWdksqT/wb4f4WxkMTgGPMKJHCCJgzGBjufdFjiS0X3XRQL1lAwQzlzIz9bPP6jK5XxW5mK8msh4dL51t1jegFy7zM4",
    ),
  ),
  (
    (
      "Gimo 359a",
      "Anonymous (c. 1760) * Trio for 2 Mandolins and Continuo in C major (S-Uu Gimo 359) * I. (no indication)",
    ),
    (
      "eJztWFuOgzAMvAo3ICEhD+5/sC0gsarHaEKUdGFVPl17Yju2x2mcFrd942zWb4h5sWH9xrx+cYhRCoIUeCk4QK3ZUYMBiQdJlJL4DOcOCRylOCNtQKUqIiGwPOZ/Fs+rMoQkWdABV2Q5qTb0pIKYNRt+Es+/ZkO9q8o3w6jIgVKD0N/ynOSkwEiTxDSSDI9jtEhigIwABuQ9ywEIjiklTDS6BIcm9CqbYIBjEAtggEYLjG8+3gWyTUED67QFBphAgmA6AAa0RwuMP8oHJ+yAVKrMGORWv/24q2SNkIFKA5JgmxF5lTIKJmLJNlE1V/nS9am88bbnjaBRuvAsLzG4bMbkgw3bKbNLNo9xMnmahxfzRrdru1gWfMluflj5syWINlOA+614fIBnYT7f+/wR4NXtC++/YuvmBcGrjBNDxd4kQfG+jVyTnvFwvLVzT3wFqvGwVuF1z6uabuH4buFE1iNnWjMJwSwFMG1ghqlTmo1TSi+NnjKdKPfCVDovT8htxfLdBAMuHVINjcTrVZrghULx3SQfN+rOd66QTFfD/PRvsBoMPkUr/lS6jvHNRw9u5p4VcHOjfeR2OHVbVZedD5lM1emwEkAfwqCSW+9v3o7RZkb7A9n6aTU=",
      "eJzll2tywyAMhK+SGxhiA3buf7DWSZpp95Mr4oGJ0/qnDJJWz6WcL+P1G1JYv1PJl5jXb1jWr5zKpIKzCiJP3JXGcNOaAyQTJEUl5T2ce0gMU3BX7wBRUUEfzDV4YMhw5SB4PrWqhAh9PNYd35KRZhiqiXaLeoo7vKuJt4/Qy/tSUYOLZ2ceVRD0yuydmBWer6NF0WZEBDoQ90UHIBzTiAEcY9oGHFMnrlqV6F6yhmofS2zJUSVz1Es4wg7kJTZpG0uZKI3yoKXp+vN2ZDnlir7MCJbRu8wCgcNWncdUs6OkFUE/3FZe3EhgPGRF+Zx/SQ1NdwFCoyMVJ+BJxcSAUiYgba/sL1/9QeTP0Cb0wirlDivCT3nQ/L4HRz60c3+GwHuEA57AsF/VLuEgRfMpSY+YWc0kgqQCtcIZxbUB1zgusZ5Aa9uwtpoKd/EYa0ZjndS7lKTR2YCYBUaP1kSbmNgJvzy3sBa/0YyjVOlPV3XiV7wjXvUIf/7dyBasoUH/HX+DHbSDSGkPbVOR1ou5mZ59tKDNIGCx+Ja77DTwBEyY7VH9SH0Y4gesaXih",
      "eJzVllsWgyAMRLfSHYhKtHb/C2tR0ZprgHL0o/yZE4ZJJg/989XPpxEXzsO9pvk0rVsMfvOIFulgEW3xN+HShzh+hKW/gl8VrmwunawP6ZAAsge5kcunyqk7OzfZqK0hWqh+slFX9rsiEZVJqUAR3oH0pFtQQfQhDEUsEPo2Nmwl5IY+LBBafN7nIjaoRTYXCoDsRBdNFlWg28kASTyU0J/DoOoWU94TWTcuVRlsNrEt62TKB4mp8tNQTMy8xFNfOH5RfBE+CN4O4SyGMaAoQ68NnTY4Zbhrdf3hSjx+22sJDrFlzVJG21uboWSOlZXOcflhL3/IZ9Zj4cta1DEXUWpwmKWCO3WwSg6tV2Fq06i2Q0kJXwh6T3j8JTr589IQrmnf5Ac4QQ==",
    ),
  ),
  (
    (
      "Gimo 359c",
      "Anonymous (c. 1760) * Trio for 2 Mandolins and Continuo in C major (S-Uu Gimo 359) * III. Allegro",
    ),
    (
      "eJztlusJwzAMhFfJBn4kkZ3sP1ipodDqMz03hEBL9fNQpJMsnVLyvjULKTabygLE9mR3Cw0vUyke2BxQk/Jg0GWfmz3n9Ujp+HwRt8UD2X8TdZDsAdQDD5IFEx/E0BSk6TVFMGHv60CPFBFQRVBdDDyQ9kAWHeOXapnVY9cox0HGwHwcySJjXFQLuq4VAx7y5c7YOapBZyu9GkDchmS0Atl6OtPsRc8ckoGAoSGyFRy//4G8kNvnt8307K4nZJFMzbd14ICCh972Xg9Htkw9KIZi5N9FzgAV4I1KrI8/oBjSDTwtKRQ=",
      "eJztlEsOwyAMRK+SGwAJ4Xf/g7WBLKgfkhFKpS7q5Wg8HmzjuJdcwzhbY4sOyF5cuMJUPG7RSyBIIKoMiLpy1OjrSsQPOL/rDbrwBhWriwzMgeHbBNsgB3VlSshkCA1ZFikJPtLE+9VGZ71FnMVE0jOVAjhMOiSSUJtJ2KaZpKVKmJK+tmBA4xvLwSXV1ydgqMt/eXB5avTKArkcCyTCIZTfnPbp+loS+V/p57zdyHm3H5Rw6ms1HKN+ZBduOzqpP3rUGOXDTvRfv+ar3j4HYos17gVMR7uJ",
      "eJzVVFsOgCAMu4o3YAjzwf0Ppiwx6ApiiCa4z6brYFtHwUkYSxIDjxrxC3AIENek84DjZ0AYEKjeWy1GnSWsEufqGoEs9hlllQXDSQ/kAiM9r8Soa/iqRlqbLzX2Fuk24shwHDh6XI+mLDSLQ2W0Dwc7xTDylzk6TAGjBkgBvZng37W4VCrdvoOSM+mVgpv/0o5mTvPNg2/OU70TFMjYDUN9NPA=",
    ),
  ),
  (
    ("Bartok", "Bela Bartok * Romanian Folk Dances * VI. Fast dance"),
    (
      "eJztVVsSgyAMvIo3kACF6P0PViSIkEA71TrjtH4h7G5eJIIwWz/CpAc1Q1w9hg8cEGhRHEcVgY3G8SwsaN5WIjVrw0WHwvBO6N3qmLkKwGOEtNcLgSuhCtkI3BCQaRzPwoLmfCUyIqoDYTBTbuLUcJJikNSyFkdv4W6GH2qGtWappsJOBBbelFbMulb1bWFJ3vdJjm1hEYq9boR4506E2Jxp6xZ6sXuDccPSlaa8aFxTJ3rxA3jlpm+0NdwdqhiTAFytBh8N7jnU/x0JfeeuatPU4Gir5t+JIT1jSJOwvupaDKXIF8XD2DyJ5pyoLfao4gEOwEVqEIFNBP2++S4tpa9GeALWA1l3",
      "eJzNlVsSgyAMRbfiDniT4v4XVkdsa7whUmyn/XK4Q07eaGdn4pT9nIzzk11Oy2c5RjKubELhSixVKi+bMEa4MQJxAgGBgEDxKmFvE1hObk3xSChnMYwQPCNkTshAyJgFJyROSEBISHAPG1ptIthEyavS5KYioVm8gie1CKgUarv6YRZok+v6CXOpB6rcEnqLi2CPCoGij26P8o1U1Fm+qOzbl/hbQgEKFiA4gv52KRK65XtwH6ry5zmNTRfha9gpCb8T3fDDe/F+5M9yn7Sxpx+jdzbX1rg7i3iaDw==",
      "eJzdVlsSgyAMvEpvAIEIwv0PVrVMW7I+UNGh/XKybjaJSUDbR/aKgnnoSNOz07FTlOzJRMIb4fCCfOZj64iGK0S7K0Tz8tmAD+eiPEPYKL+SqMjUgk/+fQYTCVuZVhFl0Sh3IK9V0i5kKfapSG3XxE76DAgpHjtDqh/bbGz+niAKjMK/ckqQ1nKeXdQDiIMzEhF5Rojx88D/Qj5n1wppF7IU+1SkRmvCWyv1CC6UEqRkZn6SU2vH78xZy52SLvjPgIOBLS7TSaG1oieB3f0E",
    ),
  ),
  (
    (
      "Brahms",
      "Johannes Brahms * Variations on a Theme by Haydn * Theme - Chorale St. Antoni",
    ),
    (
      "eJztVEEOAyEI/Ep/IG5Bov9/WKltExna3SbtwU08mREEhgGVm+ZUy4VaP1Tadh0xN9Y9LE3SA3XjALYRkLf4nAw5xU6+u2Ep/ZreXOfgXSq44bMYfb5GkM9hnHxOiPwycp2W0ZL2H9IW8dGLQocEoiNWeA8dNTv6Y7WeHQWF9tlRYIsKDOyBrGqYKZQLg/0m/5GUWDySG+fCOuFm6XyDeVQzjErAqOaHH+Lrj2Ouagxzh7yWdC3pWtIpq3kuKaV8A3ECJoM=",
      "eJztkl0OxCAIhK/SG6AVZeX+B9vWbbJ0aNyfJ9P4ZL4y2gGmZJVItSxB21FE12Q5K0uPRTO9qBUNVFCujo1YlCkZsErZz7g/iNbOjNZBvz0zSKsGUBmA07WY6+FwkI7m8v5aHnGr8lLYQrKAjVQ33/dPEFDZvdkVnxsXV/x22MMk9oc1fvL8AD2ywH0f/WPRl5+Tm9BYbjY2WZ2RnpG+S6QDxSc2q8fo",
      "eJztklEKxDAIRK+yNzDWMWly/4NtSGnXZIlLvwJLf5SHwzCouhel+AqFa0U0oDydSEGifGBtioF14FHPBSSn2eaLwRfn1nVN4rmZSXhw/Dk3Zs/+l+4fp3NyQcPgsXue0kOv/E7fpXGjSzbiCr34kxF5csrlj3frjInQCDdgEt0FY/C8w3+9wyaNAvEbKlBXqA==",
    ),
  ),
  (
    ("Elgar", "Edward Elgar * Salut d'Amour (Op. 12)"),
    (
      "eJztUkkOAjEM+0p/kDp7+v+HwYBGQhkEHJCYA73VsRU7cviKLA0hzNsbHovBZiCTVJcR3gHtAHcAR4aYZoIKCceYC1lJLDMqRlx3iqeiHm10BdcUKwqe5rbZ6s7zB851WXgxE8+Mwgh7zT/FvRPLZ3Aa1YboNmaoxf7/hNByRHUPT4J1zdtkXgfNcTPviNyBa1WUC0rqMDnL0f8l/5f8qyWfhAuiiyR9",
      "eJztk7sNwzAMRFfRBiSPf+8/WOwilQs6cGMEViUBDw/UEccbBO5CrmWhK2wLTpRTQzlt8SYQ8/y+d0DdqoRaSkJ2AM3qTQn28BU8GXgy9GToyYDJgMkwfvMCcDfJmAzxew6e0QAFQvMx674L+AkI7BelrLSUFTkNeQZgaDGyENe8EPV5BqkuOnSdR45ZbamkfJynbuIt3lu8fy8ek3wAQMBjpw==",
      "eJztVMkNgzAQbIUO9r7ov7BglHxMZCtCSEHCL8zOXsMwmquYZhIUJTktuFJWAgtGxWK2OganQbU32sJMavG5b4BhPl9bHodhx0l5H+fPutds+hrma65MbEZgkuoy66fR432MH5c7zc7l5Hfb1pwuLhQrCEZzawTfWdzS7TsjjHs8zb5fhz/u47w9CESGBrWBI0tDgHA/xxlnnBx6/iiCLzN2ohuWi1P/+7j3prY3O2E7OduuykUK6mQSd5fj47WP1z5e+3jtn3otAr0Aiskofg==",
    ),
  ),
  (
    ("Plaisir d'amour", "Jean-Paul-Egide Martini * Plaisir d'amour"),
    (
      "eJztVltuwzAMu0puIEuyXr7/weas3YYFhTigGLaP5jOULZJmFMdYxdOVpMRTjrFmulEoe8XhuVxTKojH+3N4LBUvFfJzme4FLhJKlqYeJ54+hzpFqHFtnGdkFZ37q/2gwJZmyTCqW4ez5fcXubSiNumyMayupGPxrsxiyhvpa4sYqMIVsNxbABm6RCy0iCV96COdnfMBzuV5l6/0JotZUjrvwsOyJQDlC/YH56A/5RaGGYHdIf9XhgC9naF+WLxSBFMU7YB+Cp0tiqz/RWI9+ofEnnas/Rw2fv/bht2zcMV/SRicBV/UPi4CWy2nJ9cnu94c9CUkdA9Nm2jHXVSHJjgaB5Ns797jBvBA4lB2oH0T+wsK+ll5WtDAp8P9atgd8tfJITKplEfwPxMAA54P7q2D+A2ORlgm",
      "eJztVVtuwzAMu0puIEuyXr7/wZZ0+9iaQdwQFGuB5dOUbIpm6LE4PbnI0tRjc13pc6hThBrXNhbPyCoq8VTbXFAB3GEszZJhVDxd9ei4W7ClFeVKZWPYscVMNwplrxtH3iuzmHIc3/mIgBWIZQw8p4iFFrGkD/1Oqds8JMeCnIfo0asq76KKlwr5u6hjuUjop4vucVmuKRUU9qHgF9yy5Y/Us8IuwTbqTdLC0GL3p08WsyTJENefePDfYdBhLb47rO+H+sGoejaP/T5qcRB2HriA7u7teuHv/TBiAP07YtcV63+H6AP7gZoaYPZoHCvz2rhdMB3KEPwKJXiF9h1a+pjCRAWGCqRN2uiDOAJ1X5VwP2ByiEwq5RH8bAPAC6jzQzOI3wDSLHav",
      "eJzVmF1uwzAMg6/SG1iyLMnK/Q82t0Mf9gOymBF0ee1nuxLNUE3l0BlTq/l0i7yFHDOGWLRMc62bHDpyVrXqMc1vXmzBZAvisFldvJWOMLvv+PrBKsIqK6yVi/j9iDHDW5pG5WN9j7Le4nO9HNF72rOHs/mIbf5otPW7Iv1bd2NAapAqolakbyVc9vhguu7qvqPcoGfvacd52OyVLZflRX7RBlS/lMe7meO2el/KbnH3FxKD5AHAPE3wt0fnibebN+hu4d0t7RCFnmeec5gmzHOLI8/Bng32jCk++YWM+Xs2Xz1DsM1p+Syek+xn48k3Y+bkFNmbXSwj2Ozd9w7jOEkAXQF6Fk1Igyf7e8p+Y2HbikGbLA4jKOBA2qLsR8QrYxxZ/DT6NhfCAf1PKe7oPHedR6/YEbuj7xnhGdLH88Gj/zHQR3WVd+03hjVth2ZfmpSppF6tAX4B+mOBNP0A4uKy7w==",
    ),
  ),
  (
    (
      "Rachmaninov",
      "Serguei Rachmaninov * Piano Concerto No. 2 (Op. 18) * Theme from the 3rd movement",
    ),
    (
      "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",
    ),
  ),
)


PICTURE_ = shared.unpack("eJytkmEOwyAIha8EtSvsPETvf4Q9EWz1z7Jkpm366ROeCJGPQuv4mXVj27hu3HRj23gVgJcI3FYB1hdB5xb/kqy3VZ7MnpjfYLtPxkrBF6VKnHWy72SaTDa3Dz7xHhtfD6ZvfGxcZjyyOEpZ1m1ejMUsa5arF6iGSS8WZk5P0C/D9VJ7Dm54vJiHKAJIr0X1KD0NfsuoTfGAvvzg2jjZwGxee0ub8CzzLrAXtzNZmvsJPftsDfN5YYMrvV6nhxh8d0/demMwrfxoNun5IOdoH1iCxbs/vJO5BxgK/0puxWgaRY7aowoXPdYh0Ew9BOEuM+LY7me6OmUcNy3q0s7Zcv8ZH/vm6ME=")

VOICES_COLORS_ = (
  (10,0,0),
  (0,10,0),
  (0,0,10)
)

VOICES_MAP_ = (
  (0,7),
  (1,2),
  (3,4)
)
