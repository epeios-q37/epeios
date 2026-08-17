import base64  # noqa: I001
import types
import zlib

import shared
import ucuq


from show import sleepUntil as sleepUntil_
from fractions import Fraction

# No debug if == 0
DEBUG_DURATION = 0

COMMIT_DELAY_ = 1/4
LCD_TITLE_DELAY_ = 1/3
START_SCROLL_DELAY_ = .05
REGULAR_SCROLL_DELAY_ = .15
RING_RAINBOW_DELAY_ = 1/3
FAST_SCROLL_= 9 * ucuq.ravel.OLED_HEIGHT // 10
START_DELAY_ = (FAST_SCROLL_ * START_SCROLL_DELAY_) + REGULAR_SCROLL_DELAY_ * (ucuq.ravel.OLED_HEIGHT - FAST_SCROLL_)
LCD_WIDTH = ucuq.ravel.LCD_WIDTH
KIT_COUNT = 3

TILDE_CHARMAP_ = (
  0b00000,
  0b00000,
  0b01000,
  0b10101,
  0b00010,
  0b00000,
  0b00000,
  0b00000,
)

NOTE1_CHARMAP_ = (
  0b00001,
  0b00001,
  0b00001,
  0b00001,
  0b01111,
  0b11111,
  0b01110,
  0b00000,
)

NOTE2_CHARMAP_ = (
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
  return DEBUG_DURATION != 0

def decompressVoiceString_(compressed_string):
    decoded_base64 = base64.b64decode(compressed_string.encode('ascii'))
    decompressed_bytes = zlib.decompress(decoded_base64)
    return decompressed_bytes.decode('utf-8')


def parseVoice_(decompressed_str):
    if not decompressed_str.strip():
        return []
        
    note_array = []
    tokens = decompressed_str.split(" ")
    
    for token in tokens:
        if not token:
            continue
        midi_str, fraction_str = token.split(":")
        midi_note = int(midi_str)
        
        num, den = map(int, (fraction_str if '/' in fraction_str else fraction_str + "/1").split("/"))
        duration_fraction = Fraction(num, den)
        
        note_array.append([midi_note, duration_fraction])
        
    return note_array


def musicCallback_(note, turn, prev, counter, devices):
  buzzer = devices.buzzers[turn]
  
  if note != 0 and prev[turn] == note:
    buzzer.off()
    devices.lcds[turn].moveTo(15, 1).putString(" ")
    ucuq.getDevice()[turn].sleep(0.015)
  else:
    prev[turn] = note

  if note > 0:
    if not devices.tracking.go[turn]:
      devices.tracking.go[turn] = True
    devices.lcds[turn].moveTo(15, 1).putString(chr(6 + counter % 2) )
  else:
    devices.lcds[turn].moveTo(15, 1).putString(" ")

  buzzer.play(note)

  spots = MAP_[turn]
  
  for index, ring in enumerate(devices.rings):
    if devices.tracking.go[index]:
      for spot in spots:
        ring.setValue(spot, (0, 0, 0))
        if note != 0:
          ring.setValue(spots[counter % len(spots)], COLORS_[turn])

  devices.rings.write()


def getMusicEvents_(voice, turn, prev, devices ):
  events = []
  duration = 0

  events=[(lambda: None, START_DELAY_)]

  for index, note in enumerate(parseVoice_(decompressVoiceString_(voice))):
    events.append((lambda note = note, turn = turn, index = index: musicCallback_(note[0], turn, prev, index, devices), note[1]))
    duration += note[1]

    if isDebug_():  # noqa: SIM102
      if duration >= DEBUG_DURATION:
        events.append((lambda turn = turn: musicCallback_(0, turn, prev, 0, devices), 0))
        break

  return events, duration


def set(dom):
  html = ""
  for part in PARTS_:
    html += f'<option value="{PARTS_.index(part)}">{part[0][0]}</option>'

  dom.inner("ShowTrios", html)


def oledDrawNote_(oled, index, note, minNote, maxNote):
  oled.pixel(128 // KIT_COUNT * index + 128  // KIT_COUNT * (note - minNote) // (maxNote - minNote + 1), 0, 1)


def oledDrawMarker_(oled, turn, color):
  oled.hline(128 // KIT_COUNT * turn, 0, 128 // KIT_COUNT, color)


def oledCallback_(oleds, notes, minNotes, maxNotes):
  for i, oled in enumerate(oleds):
    for j, note in enumerate(notes):
      minNote = minNotes[j]
      maxNote = maxNotes[j]
      if note:
        oledDrawNote_(oled, j, note, minNote, maxNote)

  for i, oled in enumerate(oleds):
    oledDrawMarker_(oled, i, 1)
  oleds.show()

  for i, oled in enumerate(oleds):
    note = notes[i]
    oledDrawMarker_(oled, i, 0)
    if note:
      oledDrawNote_(oled, i, note, minNotes[i], maxNotes[i])

  oleds.scroll(dx=0, dy=1)
  oleds.hline(0, 0 ,128, 0)


def oledDrawAllMarkers_(oleds):
  for i, oled in enumerate(oleds):
    oledDrawMarker_(oled, i, 1)


def getOLEDEvents_(part, oleds):
  minNotes = [100] * KIT_COUNT
  maxNotes = [0] * KIT_COUNT
  elapsed = 0

  for voice in part:
    for note in parseVoice_(decompressVoiceString_(voice)):
      minNotes[part.index(voice)] = min(minNotes[part.index(voice)], note[0] if note[0] else minNotes[part.index(voice)])
      maxNotes[part.index(voice)] = max(maxNotes[part.index(voice)], note[0])

  events = []
  voices =[]

  for voice in part:
    voices.append(parseVoice_(decompressVoiceString_(voice)))

  while len(voices[0]) and len(voices[1]) and len(voices[2]):
    notes = (voices[0][0][0], voices[1][0][0], voices[2][0][0])
    start = elapsed < FAST_SCROLL_ * REGULAR_SCROLL_DELAY_
    events.append((lambda notes = notes, start = start: oledCallback_(oleds, notes, minNotes, maxNotes), START_SCROLL_DELAY_ if start else REGULAR_SCROLL_DELAY_))
    for voice in voices:
      voice[0][1] -= REGULAR_SCROLL_DELAY_
      while len(voice) and voice[0][1] <= 0:
        if len(voice) > 2:
          voice[1][1] += voice[0][1]
        del voice[0]
    elapsed += REGULAR_SCROLL_DELAY_

    if isDebug_():  # noqa: SIM102
      if elapsed >= DEBUG_DURATION:
        break

  for _ in range(ucuq.ravel.OLED_HEIGHT):
    events.append(
      (
        lambda: (
          oledDrawAllMarkers_(oleds),
          oleds.show().hline(0, 0 ,128, 0).scroll(dx=0, dy=1)),
        REGULAR_SCROLL_DELAY_
      )
    )

  return events


def ringRainbowCallback_(rings, counter, go):
  for index, ring in enumerate(rings):
      if go[index]:
        color = shared.getRainbowColor(counter + index * len(shared.RAINBOW) // KIT_COUNT)
        ring.setValue(5, color).setValue(6, color).write()


def getRingRainbowEvents_(devices, duration):
  events=[(lambda: None, START_DELAY_)]
  elapsed = 0
  counter = 0

  while elapsed < duration:
    events.append((lambda counter = counter: ringRainbowCallback_(devices.rings, counter, devices.tracking.go), RING_RAINBOW_DELAY_))
    elapsed += RING_RAINBOW_DELAY_
    counter += 1

  return events


def getCommitEvents_(duration):
  events = []
  elapsed = 0

  while elapsed <= duration:
    events.append((lambda: ucuq.commit(), COMMIT_DELAY_))
    elapsed += COMMIT_DELAY_

  return events


def getLCDTitleEvent_(title, counter, lcds):
  string = title[counter % (len(title) - KIT_COUNT * LCD_WIDTH):][:KIT_COUNT * LCD_WIDTH]

  return lambda: (
    lcds[0].moveTo(0,0).putString(string[:LCD_WIDTH]),
    lcds[1].moveTo(0,0).putString(string[LCD_WIDTH:][:LCD_WIDTH]),
    lcds[2].moveTo(0,0).putString(string[LCD_WIDTH * 2:][:LCD_WIDTH])
  )


def getPrologLCDTitleEvents_(title, duration, lcds):
  title = KIT_COUNT * LCD_WIDTH // 4 * "\06\07\06 " + KIT_COUNT * (title + LCD_WIDTH * " ")
  counter = 0
  events = []

  while duration > 0 and counter < KIT_COUNT * LCD_WIDTH:
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
  title = KIT_COUNT * (title + LCD_WIDTH * " ")
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
  lcds.uploadForwardGaugeChars()
  events=[(lambda: None, START_DELAY_)]

  for i in range(15 * 5 + 1):
    events.append((lambda i = i: lcds.moveTo(0,1).putString(lcds[0].getForwardGauge(i)), duration / (15 * 5 + 1)))

  return events


def launch(part, timestamp, devices):
  devices.tracking = types.SimpleNamespace(
    go = [False] * KIT_COUNT
  )

  devices.lcds.uploadUpwardGaugeChars()\
    .createChar(5, TILDE_CHARMAP_)\
    .createChar(6, NOTE1_CHARMAP_)\
    .createChar(7, NOTE2_CHARMAP_)

  timestamp = timestamp + 1
  prev = [None] * len(devices.buzzers)

  sleepUntil_(timestamp)

  eventList = []

  maxDuration = 0

  eventList.append(getOLEDEvents_(PARTS_[part][1], devices.oleds))

  for voice in PARTS_[part][1]:
      events, duration = getMusicEvents_(voice, PARTS_[part][1].index(voice), prev, devices)
      eventList.append(events)
      maxDuration = max(maxDuration, duration)

  eventList.append(getCommitEvents_(maxDuration))
  eventList.append(getLCDTitleEvents_(PARTS_[part][0][1].replace("~", chr(5)), maxDuration + START_DELAY_, devices.lcds))
  eventList.append(getLCDDurationEvents_(maxDuration, devices.lcds))
  eventList.append(getRingRainbowEvents_(devices, maxDuration))

  cb = ucuq.setCommitBehavior(ucuq.CB_MANUAL)

  devices.lcds.backlightOn()

  timestamp += ucuq.playEvents(
    eventList,
    lambda _, cumul: (
        sleepUntil_(timestamp + cumul),
    )
  )

  devices.oleds.fill(0).show()
  devices.lcds.clear().backlightOff()
  devices.rings.fill((0, 0, 0)).write()

  ucuq.setCommitBehavior(cb)

  ucuq.commit()

  del devices.tracking


PARTS_ = (
  (
    (
    "Titelouze",
    "Jehan Titelouze ~ Ave Maris Stella ~ 3rd verset"
    ),
    (
      'eJyFUtsVwyAIXaUbNAqSxP0HqwKKGHL6E4PAfYB01/Q5U//kmr6Z/9tBfI/tHyWDe5QqaF0/ztklOa0Ei7TScooJG6ZGl/C1g6SPIhG7pIXI+MBJ2itRxHPkHcFirLF/DgHEMSyHOrJeGM0WyYGf8EJQ5JBKyhah5ERmZxkAvLWHhbm8cVVcgUYKnGfEmZ2+k5F5YwEBQiTUW3oOYnlqwTNxhgInLOjN1G35Oyr711/McHYrQh1HLxKAYjt8DgYcQvEMr8/uGksNn4btjCmp5ib1+AHFELlH', 
      'eJyNUlsSxCAIu4o3EB/o1vsfbBuoiN12Zn+IGHkkI9PIgTvCgcBb2sC2PJKEmA1o9FgB6YT5tCiDB+dVCnpsHeUsL1tV4MVeRFc4rEQ5aVlvo+eAKKsK8MqqcrodpliDOnXY5k6VE5M2aQJXY7Ys8AdhG49Z7KRJvjWglzWXINn37kJyLsCTZeSbmmnUjxlv0sQCemj6Z73YQd6NtsSaccW58GxP4IzPVxDkRAP39AUH9YHa', 
      'eJxtUesZwDAEXKUbFKFpsv9gJeT59c9xxfUIVLweMmADqXhTyy2071lz9gqfjGuKPgswprwWnWlhNPVXzXRoBnv9fxqKz5U/E6clC+Abpc0IHkZam5NlDclVQWrPJoABjWoaFJxiQLRgQF5gU9kF+HWKASFgzkT6gUXtii8scYy/HR6MZ53PIqVv14alT5EeAT6/+2M6'
    )
  ),
  (
    (
      "BWV 528a",
      "Johann Sebastian Bach ~ Sonata No. 4 in E minor (BWV 528) ~ I. Adagio - Vivace"),
    (
      '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'
    )
  ),
  (
    (
      "BWV 528b",
      "Johann Sebastian Bach ~ Sonata No. 4 in E minor (BWV 528) ~ II. Andante",
    ),
    (
      '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'
    )
  ),
  (
    (
      "BWV 528c",
      "Johann Sebastian Bach ~ Sonata No. 4 in E minor (BWV 528) ~ III. Un poco allegro",
    ),
    (
      'eJztmWuS2yAQhK/iG0hIgED3P1i0TuxE/WG3xMpVSVX8b7XTME+mGZawTlOqdRri9kvhtuQ1THGqMQwlxBKW25JEZJS/y7iGMNUahrz94nIrs34I+kEhS9EPWT/ENeQaa3xuO68px1qemkc1ZXaKw/hpDeN9lyGM999tURmCqn4olLjbkv+QkA9ZP6QXEr/9oT59QN64EBBIIAyAQKKejj4hfhevadQPqkczpc5CoCkyWSFZNc1q/oHIPVMq1DEulU72HiPEmk+IN9/vAgdBwip2ANIRbBgHCVh7BQSaIj9szR2wFhI+UFcUoS91hTDpJltAWNRDfFp2hMHqwW2vOJNVD6ieYdxyGuJznRB/sHkn+9SGk1VTGgfzOxxkJa5Ih69Ff1GS8pORbP1kx3s2iT0PCus8l1rmIT0BH1A0q15bsPd6ZPm7CIGDQPq2wMM1eY51/jJr/++q+ABXCse0KxQYLQL0Skc/2AeUEgiXD3njtJddjhxVAoEeICFBiAwXbbSQ/S68TdjOdQDS0NRB4kOx6XlX6Cmjs03mfFv2DLzz2H1fLOfPZUp0HLKe6F3QQcgwbEshRPXIVo9WRklB+UrHGj4MkOjoqB2szZJndmXPt6+gC58gWID44/TAeXI+pZqBkrGIjlI23WXmETFHcuOYv+fYEr104gPFMQGiwzJk/NgoNxz0nv/ojGzhjOzbzYQXNsz/zt/xig7vMGZDxuHw7OD0WMPetTh5aHQXoQXnS5AebKwhLN93ShyNViKDel5BcXDOeYlGFe+YvhSCHzj3SFge0bFGxy4+BiPH2OdnKCMO8KxUw6pKRQ60Qa3BhjWoSiTua5dMqT3Y///y8ZmXj4vvyx03ggPEyjYT6qGzLaQcu4uHeNb4uhE8Swz7+icJQLxT7bUCqiZL1g9ArHGE+GGIJ9r2/Oy5AGFR+87BRb3EBQXjbemBQHWYDwg0hQuPDDuljdmRHNfwTsaiPnJ2nu5DmSBhFTsA6Qi2T8uOXPcQX9nnr799V3lh577BTJKW3h+4AzCTWw8wu3677aIjcFnT8xNs4l9WL3jUORQ4uTO+tP7lNPofHsZ3TJL9uzKeYApvXu/JKihhg/E5zigss/EuVOISUxpSmEqoG/8dh/AD7KRwLA==',
      'eJztWkm24jAQuwo3iKfykPsfrE1/+DxLBiVu6BXskleKa7Zcxu3RmaupbMFc/11y2kOw1sKW+s/8pfjdhxRa8lv1qfpyKQ5E8LnY7n1ozW+5/1JHVHyR8QVBIr7w8CK33eeWWvpdtu6WU6v35y4w6pWrUjwjouze/V1l8879OAhlCFTIhZElQPU4qn41dhRwLDB4wxq6h/wVJCThCwwTQzCymSSc0oOXJQjqcY2LgKAepLphyhl+VEPYyZi2DNFOlnrQsgQhPWhZhpAe5CDKIProeZ9qF7LHtAQljJYgf6Cm3IGkC7kaFiDa/PO1r+u2W3trWr65VNqkZ8868us2r81niDb/fCg5+XU1aMhCsHVaLuS6hlCgMD8otiRxwFqSmAQqxtpq3Mzd2Yf4aNdjTEtO7Umewir0UbI2A0SbX2RceJWEq8gO0/W4QcIziIytjhxDdN1KJ+t+Si5kEojUyjE/CxMONxJYonDEA7VmsmAO1IchyUtAYA1NYfNBcTI+aQcR6NH6nzFp4qddYlS9oEBmAbFF6bau05SCoOv4DbH/TLOUvXEFQprKFsQMboGuNyQXcoviJnWe9DFEm3+eODLll4odgCwEWx+0NE9cgMjd9S3MmiQmgYIuhn0Ou+dHaBFPNiTj53EJ9V+1g3GR6kz/yHxAVv6hUANEn6lNEsvJiUhkw3QDP1uC2Ct1N+WDxwEShCJXY4AEyWEYkS/ifJqvHWJFIwliogCmSPZGxpt2EA/tJCu6135G2pgxhR4v6hOJFymkJ2wUBupS8kR4oEvJzZS7pVTsO2P5zljOQb4zFiGxRJROQ3TdTrrDbUv+7cG0fWrrqE1pHxKEjNH3D++4sqBuMLmyQA/pdXW26/1DzzJIVWk/l/IbvsHXCwsXEAtXFDIf+KbocXFYf2JpwGu6xPjcgLLawr3QocQd9cpw9ZhxCJVxkoMC8Z8F7q7JMbV4Nev1LAkFjIZNp6dReCE78Yry/WTWos4gsmlwFU2mZLDKkWMcQBaGDXqLoKijz+n+3quoTYKiwgongUkqluaala3VkCxM7jhpl3JA2oz61iRZVCrM+MSY9IGSXkVRL6L/RfBfTrSGg26bWF9TSWab+VB964c+t/k/urj+pQ==',
      'eJztl1luAyEQRK+SG7A1MMz9D5axPyy7HlIzI0dRIvOJqrfqDWrec65j5GDHqemrVr0AYuwppjZshBTv58u6K2R60fSiQy19MWJgKS1g4O+QCz8iK56IRVeHmp0EaBCCHWhJNAxO1DlbSKtp0uicsuJXwixA9STuJfe2lRFs1J77ND8pWx6WwpZsS50sIB0owag6QC10gKJtoTtwMSn0CwVayja2Euqje1LKY6TQjmP9TtHrRdcLiAAR1YoR4SmFiCIOEsWKun6j2VGKaBVxUChW1HVD+FCKaOEpcnsh+2gi1OE7dPhD+5IV7YeyuaNU7XASsc04XStbEZZUiM5hUCoCRC4EiBpwE0odcIzxstYuJR1qsXHWFszZLLPeUAdAuOliLflUgyS3mRjtebML3TXZ9Gcd+xnG1DFWK9oVD4Mq8xlDH/OZCCyfpAhsNH/GF3ctNG8L+DOvYAliPQ3PU4Q/o1CsQCmWIBAaLUWaWpkgPB0gGWnwH9yTmXm29xe21cKLdjZCf/HL5K/b9/+g+DJAAgmBJxOIWp5AlKYFLZ8fxv/6YbwG11a2YG02Wg3dYi/5MQfbk457XuyJ5JvI9vyUegV0AXyS8BeSYGjjuMeQvgENm9mT'
    )
  ),
  (
    (
      "Ano. Loeb Gott", 
      "Anonymous (18th) ~ Lobt Gott, ihr Christen, allzugleich"
    ),
    (
    'eJzVWmt64yAMvMreoPiF7d7/YBu34JRRJoMM7n77UxHoLSHJievnsgzz+jGMSwjhzzoDPBD8AR3wCPAg8Eh/J/TjAVv2oxBXqRMFPcTD/U3JA/iI6g2lehn9hX3AG8CIHwAeK9kxcZFfJPKgt5i87D7DzwBPQl/E4319ftpiGPdqgZjBExyZg7JDbPwNcZnnodpCTo0jeqzI12d+1Oo/Sns4DSoIGoOyCHwmJBgUGaqQ3L0eUTlqzycGTAV0MRDc0OZWgNIH5oK3yjg1VvzcCjQLgOcxJjpngSm78IrYIPXWUW9ads7CuL7Hm/toYFU2dVcABlQKXBWAGVBFDOItvbIIhISfDtgeV/HgzOiKDOz7jl+Vn5RElN+UTKYPScjw87h9Y69qh01irTdU1zW/lV63yFBdRU+D4mxlz7oF4qvU0jJjODvedHwCZbbXzGTa5R9UO3X15Ul5nNGV1GYRGIjP0k9radsEn+wzjIHEzJWKopgmYiT4r+s/im6Go8Cz2Q/pfzvbsF/fi+sdjpCenOWUPIgHeUJ756qKJCT+3dOYd1rzdtbKAOLVaJ1em+kp/Xt3hd5X2T/89aXXuUs95SFN1tVRNJFr1XYvyTU65xGckO13zRi1uyAcrGn6sGUUex6Yv3BIwfrvHGKkQbzpfdcMke0DvRJ2Xr89Y1ydQWjPXmr/qPYQX+E9Q4Vv9Zehp+4vuBjy1vOrawwICL61eI1P19UqvvdUpFb7iEf+OErg/d6vHfMOMa+Zq7Cgb2waqIx3086Ewp9oH0OukT09TyY91Yx2XjnYIRuSc3trrUcyv46+Z7I3VVv5eLJqWWktlYzC+XKBpPDM2+ec33mB6h1NWntHf/OE90sDnAz2Y9Z/0s+T//gajcGej0eA1/I6ovH6CDBIcwqb4RXOi488WMhUZ6r2GGzQz7ZtXR6rlwzl142fC4+VWvJ39h0m+Z0fTRXeFJ/aj65pT/Sf/aWhF3vVN9XiGb3av0zgLr/2LxMk+8yUH8l5MhU1/sWCLkGZeGhO9a2wcul5EzvpDTUkq1rQugP07wwbP4brzgH2LHdv9W5ufLt9a7tqcPMHDPb96apBvfhfD7nWf5B021w5X7BWdldfpH/1YoH632D4DB/DX5csFvQ=',
    'eJztWlmW4yAMvMrcIN7Adu5/sHG6TToUqZQE+PV8zCdPLBKSCi0M92WP8zTf4hSG4U+c7iGMy3obH8NjvMI4Evr38nUUy3fjdmT+iuwhXZxf0HG94ifRv4Yv9DRG+iLoE5l/nhfK+xhjWJYxLXgKlDbYxYHIMGMwMVBeMDAAEkiGNuONEY0dGgIGQIJmhvb7vMVh2p8bAIetB0qGUEVi/ToT/tBn2PrJaVNvNvAJvIoLbdy/WSGlAsAi1IEXW0yxH1oA+lTaj2L8Z/mkhWrUOy0MYbXWZxUDK5h0gbO4IWMg+VCJSnCA4FCqWDupz6SsPpU0giobYBzEw4UPrVMeCnrzY8Py/ufP+sFnLJOmn3IwamCXj3SG4CQqAe6Zd3tND+/OaEoUnawx3Jip1vAe9/UUvJ5GsP518G/FTjwPH5N2LO6zXzInQK5BIHE3807jzalvpJfhmjHeROxDOvB3ZmS4enud/XJaGi+CntYTYI7kuHO8sYf1ff4oL1cYK72r2vmKjvyisYBxbTkWIlnaWiB0c/LkNWar/IDtRNtWaD3jVibdSbYCHY2Cnam1Mwo+pLk4sSyQxKtdpY+IB3jtVZlTZ4apykg5iaLZvOb0NJ5gzMpLeP73MMV1YzhM0h9IqMsS2CPp5X55FjeAsBiTg3v++xnRZ/8/Jpyl0kpAwAuBpzHm4PjcvZP4KgEscg5I2XP07F51Q/AUWYBhfueaDUsbrFmUDvOBYW+eopLMznkKnc9SdIzjIcNHb2BZI78/31OjouwA443wozoNp7+oyMwbyNY+DhiHE/Av6OxxYeqScX1jsIV00Wi5oKRZJb/RessCZjpvf4QaP+yegcdzPyAXJRcStyzZchrW4GlpjNxA2BQhbIp5XI+lxkJ23TR0NjAUNovytCwxOBsSEpq9DRYvNuoGiIuu+KUlotweFNKm1bW1fbsv1mnjIn4vawVYA4veBUjVona2tKvbh+/TmubuIatfWl8a73VZvxj8zBe9st9nkLwP1k8Z3j8RzCErGyaFhYhmFX8Aa4MV8cvE/MOAMMwKcWw6VKitiQ1JHNh3B+K/1/8O8OJlbX/NKkBrw6l2/UX8/n//EB4wfBpu41/c280w',
    'eJy1WEkCgyAM/Ep/UJDF5f8Pq7Zqy8RkwOoRAnEyWdFNKfnYP32XnHOPlCafU4x+34i4gSdijxsDbnS4EZhS+VlHryAOcSUK6OKE0CGgI7BZaclgD+uuXM/slOtky2crTH0zU+hBW473kYMg3Ife2hDlZbmITcBBMygsG5LhBOqRLxpuqKDRIYj/a/5H307wB78wX/Pnepu5k6Dd3bkaN5JoQe+jemer84J8U76jXY1lsYnGkVwSuYLykZzX2FrhstRi5GJ9Yb7OjeZipALbmjriDGL8cdzGUvn9zLZlzVhneiXxvEZWnSCQWDtDitHm9sJPEGQJyXLqn9knkjmUYi33j7tQBOWIFY+zytLYla/Wh868Wp/ata6aQrS+c1Yf8t3IBw4lEGz2hEOdi+cJuNvaWqW+q7s89qE/2x6UnbPim9C1OteZaJtDxR6uD4bnY3VKCa79umIMKyIs7irnm5M1ubqB1o049ngVs2KrQl1Zj1gG2imBk0NGbb0tz5VTfZ2bmqsXqb7fSeu9/mn921r2fvajIJj0YtizNxh8H+Dt4m2N9rMs0kJH5/OXrxmO92lwQw0/Fz3ZXfmilv9l6OOivD8SwItFpY1uck//AtOOtgE='
    )
  ),
  (
    (
      "BWV 848b",
      "Johann Sebastian Bach ~ Prelude and Fugue in C-sharp major (BWV 848) ~ Fugue",
    ),
    (
      "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",
    ),
  ),
  (
    (
      "BWV 870a",
      "Johann Sebastian Bach - Prelude and Fugue in C major (BWV 870) - Fugue",
    ),
    (
      'eJzlVUuWxCAIvEpu0AYlmtz/YBMEBKLpN7OeTWh+JZZAp2v/wHbUW5TtQBaVjYnFee3dtIkuQWVKmYwQtGXC+QUFVnnLE8SYusDTaxoStBiC9UueQB+jwPHbPGQ/Q3E5IvBvkHwMV49EAAUw0emCrTJG3VkYyi0qAZOJ3WzQqMIaPx/5qMyRIQaNKqzB1gYQfp6HK9BOFc61g7RH99esOERE5ejGcE3uwsZa7XyrJrsLZg/u/NMNidt+zfTGhp0TjXvQlgn1DeWFSfEpoRAqLYOpt1dTnySk8O4z2F+uKW/nW+qpxRB/7JQn0GmRHjtbQh7acwvgaxsji1+vhnuasw31PeLZTfod0j83IjI+8sxiGQEkZFtQGwNDSeTYjh0YdL77oSNSFyhY6f991X5LW2zasW4h0MKkOWXi00bE7VxY763DRs4ydAbjMIQZ7E1M7m7tr5XHtseZR7C2HjtAmwJGG1QmBoUf+QSKkvZh5zJbx8JWmnYlN7jG5tDPvFLRcHgwno2LTWenixZaFa1V3f/acDfP1kNDf3XhI3nl8LaDDkhX+gENIal8', 
      'eJzNVVHahCAIvEo3WEPUzfsf7E/Ripyo/fZh/5dsEEaREV2e04umRHl+8ZRmGQqiKaY6pJjnKfH6cYJHX67zgzEuygUGxGuWFh6CDH5HNPG7DmHdYjW1vXUnGkIGo1MIBiSDxaE4uILlMqZ2wcIL4mQUp42MMvo4v8YSVRw0arQgFBCLlQMKj+5obCgSQIOLL9oWiTc1RVkhNup0lN/JyJnKp/wfVmnKE0GWQeToMr1FqmsFhaAJl5s7Ff26Tb/Ad5eAMnJQCAW0w4QsHaEAqN/uacn/P9wznJHKlqM6QWFh6TnsFPIIKRevy2HU4bTdkGPP3OXQdUqi001IXV1uV81KT2o/aGlshLJ6IDK+zfEBNawoZrk/zAfUz8XyQdWs9g21BjMyCvflZR9Edn3BrKZsXeg7z70XSnOtTwJJDvTta75dhepWTD97kR80Gl182EyMJtRai49qPaXc01wAc71BwcaGFHjidMacv5almbuVnz5dul5PZxuMkzjtbM7yNh/eYQHrTsqv+wO+/x55',
      'eJytVVuWwyAI3Up3UB/4iPtf2ERQkIQ6mTn9qQHuBUSgrsX4Dq/im3/DqwQ6lJSPizIuSkdSYSThApLHjyj6MYjEQIlt1Xc4OqmsmCgg6QQD2eKJQ0Z1rJgoIOkEZ7JBS3QwMnDwLAElOBAVuhQlh4VzHnhhij5LkOiQgtyUTiEsfHEbJ2DxtKQh4xWdksCSFCQdGx6VJld59vktFk68qrt5S9I3zVasYkkPIMevD2IXwyz3A8jDF/lLx/w7wdGauzy/2SupGJ1zka6Qvn1urqOiRxWhExJN4aCjT/Sy2oBccwk4EFWeKh2W7VTwe4yzsQnHi82FATss0Jb6tEp3hPzJS2BpsYWZA+c092y+eQ18535/ZgzFEruoyuBKnIwJRj1+YyjeyjO6VwULjVT7Li9rrS+F0y1sDsL3ZpN39GYAHoyIlYJ0rteN7Jf2BCmezlZsuHKlBY1Y7G7xref2DJ+UUyXpv23tCwxdUg8PrRvcD6b1m5g='
    )
  ),
  (
    (
        "BWV 847b",
        "Johann Sebastian Bach - Prelude and Fugue in C minor (BWV 847) - Fugue",
    ),
    (
      'eJzNl1luxTAIRbfSHdROPKX7X1irSvGTcgBjy69qPhFcwFyGhK/arlTPzyP8fh/1uCXplkRIjqdVqZC0Pcg1jX1tQ85Pq5evLul5RV2HOKceT5dckDRdh7l3SYZkCbnF8YvtQi7FwSjgWFZ3dQJKQQlKwXI5qXGcpaV47YfmOwc6W416rOMgdCERp9oy6las2FTMPR4ODodOgAq7wOOK3eSYSC6rtblhZIHe6SpoOCFRVOJllVQrNneld/JAagt1qDuGxMw+EyS0IjPgK+NRM6wEHeKAK/lcsSrUQaaumClhPIx5l3fqeKwYoUGfTkMQXGACOQZfi8iO1tmFPLc8o64DHFZZWHDESTN5zW1TQq8uau48OFuNelxnI2isuKi6ssJRYbjuhRwwAQjz/39J2MqMhzocLX/wA/K+Hz19m75vuXue2ThV9efhPHrOLNdxz6wcKsDN414TyMSSgxYVQ463rIe4wtFHX8Z1BOpMpeW569Gza1zixWDsSAOZEsc16WgsofM9v6Bcf8wrPRr9J5zwDciImJw=',
      'eJzFl2FyxCAIha/SG6xGULP3P1g7O41p+ymD7mabn4w+4PFAEu4xyRaDxNsWHt9HifdSdynpJt+WvMNSYFFYEiwbLOGwNO8Ki8CywQKcM+bxmQ4OIjy9N0uLMI7PEMfI1OOr5VVgqUBGdTq+iONhDEro+CJOdDBv5P7D15ZylbhPkRhwqxqJGbJjMUB9pzyeEnqahzgg8UQ+pMlEPbWgejETeMtS5jgcQwjjS47SrHWXa0asIYOdFw2ETiNX3Arj8sXhGeJ0xr6hU+PWVIQeNowzazjGWDssFU1R+cC9k43syGJKY0+yAW1UNG7nDEeN59GZUsJzy0Zn7i4tGznD4niUPbfmugADqY0ECsoQ3RiG+iYwXlLAuPbJ9BdGUWIlgUvPr4J2NdYBz0BoOCw6h/PSvg1VKlSpoFCwMiQEmMb1azAQnDhcWWcE4cgMDmSpYFnhi2eII5C3oG8E1WJeygiBrNCBAvllWTgYu44NVvmf2WAWDsauYyOxOtexgbkm8HVmgUW+DvMkCj2t9S0z97DzToXhHXDxjsHbmXScvEvIypnumKqLyOCwoxb8Ks51zvAHU/F8dAJkElgRSE/Kv51/+Q6fHg/YfQ==',
      'eJy1l2uOwzAIhK+yN2gSY5P0/gerdrVxpH5AiJv2J8LDMLzS6VnWtsqs+limv99Pm566bqLlIf+Wur1bDp/9Va2wtHfLGHJbzmPdhlyAU2Hpec2+D3Fmn4/PuWqCTyJWRSxZz33GcKTBIrCAszAWGQL5e2oYWSQU+54ahb1xkxoC5GtZcAb7NK2wYCcYe6Oc4zAWg2fkIZ1E8LuSOErRLchC+ArIDTiZUhg+5JxgSJ/uUr0cBAoKFEwESskV+GRmPcAJShzs7wQyMzVuBWIZBQ3uG2+gf5eMO4npP0Zgv4pcjlxzmEiBYMlDtZTfz5gtgh7a6Mb1KAw2yvqs5zN1zyw6AnMfKCz8zIKPon0UginaR9k+m5968LkWvEIbdhdeLiYKBRuutvEqoOzTCVT2H8GloS8UvXOtWOIiN8x6pODuo1DQ4DPUGKi50cvoHT4KRqLzowWdksqT/wb4f4WxkMTgGPMKJHCCJgzGBjufdFjiS0X3XRQL1lAwQzlzIz9bPP6jK5XxW5mK8msh4dL51t1jegFy7zM4'
      )
  ),
  (
    (
      "Gimo 359a",
      "Anonymous (~1760) ~ Trio for 2 Mandolins and Continuo in C major (S-Uu Gimo 359) ~ I. (no indication)"
    ),
    (
      'eJztWFuOgzAMvAo3ICEhD+5/sC0gsarHaEKUdGFVPl17Yju2x2mcFrd942zWb4h5sWH9xrx+cYhRCoIUeCk4QK3ZUYMBiQdJlJL4DOcOCRylOCNtQKUqIiGwPOZ/Fs+rMoQkWdABV2Q5qTb0pIKYNRt+Es+/ZkO9q8o3w6jIgVKD0N/ynOSkwEiTxDSSDI9jtEhigIwABuQ9ywEIjiklTDS6BIcm9CqbYIBjEAtggEYLjG8+3gWyTUED67QFBphAgmA6AAa0RwuMP8oHJ+yAVKrMGORWv/24q2SNkIFKA5JgmxF5lTIKJmLJNlE1V/nS9am88bbnjaBRuvAsLzG4bMbkgw3bKbNLNo9xMnmahxfzRrdru1gWfMluflj5syWINlOA+614fIBnYT7f+/wR4NXtC++/YuvmBcGrjBNDxd4kQfG+jVyTnvFwvLVzT3wFqvGwVuF1z6uabuH4buFE1iNnWjMJwSwFMG1ghqlTmo1TSi+NnjKdKPfCVDovT8htxfLdBAMuHVINjcTrVZrghULx3SQfN+rOd66QTFfD/PRvsBoMPkUr/lS6jvHNRw9u5p4VcHOjfeR2OHVbVZedD5lM1emwEkAfwqCSW+9v3o7RZkb7A9n6aTU=',
      'eJzll2tywyAMhK+SGxhiA3buf7DWSZpp95Mr4oGJ0/qnDJJWz6WcL+P1G1JYv1PJl5jXb1jWr5zKpIKzCiJP3JXGcNOaAyQTJEUl5T2ce0gMU3BX7wBRUUEfzDV4YMhw5SB4PrWqhAh9PNYd35KRZhiqiXaLeoo7vKuJt4/Qy/tSUYOLZ2ceVRD0yuydmBWer6NF0WZEBDoQ90UHIBzTiAEcY9oGHFMnrlqV6F6yhmofS2zJUSVz1Es4wg7kJTZpG0uZKI3yoKXp+vN2ZDnlir7MCJbRu8wCgcNWncdUs6OkFUE/3FZe3EhgPGRF+Zx/SQ1NdwFCoyMVJ+BJxcSAUiYgba/sL1/9QeTP0Cb0wirlDivCT3nQ/L4HRz60c3+GwHuEA57AsF/VLuEgRfMpSY+YWc0kgqQCtcIZxbUB1zgusZ5Aa9uwtpoKd/EYa0ZjndS7lKTR2YCYBUaP1kSbmNgJvzy3sBa/0YyjVOlPV3XiV7wjXvUIf/7dyBasoUH/HX+DHbSDSGkPbVOR1ou5mZ59tKDNIGCx+Ja77DTwBEyY7VH9SH0Y4gesaXih',
      'eJzVllsWgyAMRLfSHYhKtHb/C2tR0ZprgHL0o/yZE4ZJJg/989XPpxEXzsO9pvk0rVsMfvOIFulgEW3xN+HShzh+hKW/gl8VrmwunawP6ZAAsge5kcunyqk7OzfZqK0hWqh+slFX9rsiEZVJqUAR3oH0pFtQQfQhDEUsEPo2Nmwl5IY+LBBafN7nIjaoRTYXCoDsRBdNFlWg28kASTyU0J/DoOoWU94TWTcuVRlsNrEt62TKB4mp8tNQTMy8xFNfOH5RfBE+CN4O4SyGMaAoQ68NnTY4Zbhrdf3hSjx+22sJDrFlzVJG21uboWSOlZXOcflhL3/IZ9Zj4cta1DEXUWpwmKWCO3WwSg6tV2Fq06i2Q0kJXwh6T3j8JTr589IQrmnf5Ac4QQ=='
    )

  ),
  (
    (
      "Gimo 359b",
      "Anonymous (~1760) ~ Trio for 2 Mandolins and Continuo in C major (S-Uu Gimo 359) ~ II. Largo"
    ),
    (
      'eJztVtFuwyAM/JX+QTAQG/L/HzZC2m26gzmNOm2TxlPlFPt8Phtb3VI/yxr2czPbRPez1P3YzRQNGQ0RDEUeTiXcvVa0BHRS3bgYpgHBMHQHs1GjO4YM6B/A+tlLPx+WTJb4sMT1ng9l7MEf1I+RoIWEIhfcMnEITrEcrD92G8mC4JQ6wQ3cwPZfdQ6WSSHeuO6qWz78Hu4ZG0Mhri8gseIqf1Qel9lXgKUrKGLmiGQ+kuyZdNzp1oi70B5pHnx9j32CSmj/SpZClqfGyJwJJSYUxysNn4wGqr2bdAtimmpYSlbRLp8Yyu7SJMc+wC0d/05dS199PSEKehBcdY4a1muTERHMt0Td0acSpQ0GyEWI/B8BrtxEF6YEz0XS0v8283u3Ga74cJtxqzPTwPz5ZD36shhsQE9fCfhq++vOoLuQAh759ErjlUId6l5hopm0gdb8FeM7xOe+GINsyIuup5SEAzUs8ga0dKpg',
      'eJztVltSwzAMvEpv4LcU9/4HI3YxlF0lCvAFU390OooeuytZifZ7mSe0OM5N9Z5knNDH0ZsKGioaMhp0JU3xPaugJbpJqC55JCpDLohVGFpFBfIfwPqUBSyCDRTKG5GxAb/Ov6HmrWkyep7QA+lIXx7ztz9BXWUTE/ZGDUMMRUhp1nHH5uT91OgkSwOGLL1bx58C7jC7GFfUnROm/AOwV7QmcJ2gbP6+MChd8fFpazkOOhxUS6p5vjQJLJksFDUSg0WXJbel56Hmbe0rwG+sOG/+keFeRKX0GLYqSaZDjttIqanmuSO1PLzLzHf21OqKt3PdVWDdPrf5FyZ6VyLLQF+2nPZbTkxR/N8Dv7DUqT8cQ/SNy4n8G+ZtDWfn9cXwT74YcFscj8keMyv0450jjTVwB9LgyHh5aC183qsL8V4YUuPF9e0mEh0TPPpwFKl7luejsTGkN0oCYI4=',
      'eJy1VMkRwyAQayUdcK6x6b+wBIJhIoEPxtmfNYv2kuzXuOVQolO8xEaXowIOAL1/G10yBBG/Isl/WCWaJYXKI4TECoBFQAPQSK18qwQEBMt67uNkmEY6HIbfbLQSPXojow2NW61l3IVmb7RSM/z4ovVN0V7NoMqyEGLvKIX73RFHOR412RMLAAEBlOSH9Ndgbbujo/EqD8zxJCsv4BmDnfxhLrR6cOHiUmJlEhaOIwFyzoTQaY8dR/FEeMEZR3FldkJvDaf77jhziqdza63MGxr1RQY='
    )
  ),
  (
    (
      "Gimo 359c",
      "Anonymous (~1760) ~ Trio for 2 Mandolins and Continuo in C major (S-Uu Gimo 359) ~ III. Allegro"
    ),
    (
      'eJztlusJwzAMhFfJBn4kkZ3sP1ipodDqMz03hEBL9fNQpJMsnVLyvjULKTabygLE9mR3Cw0vUyke2BxQk/Jg0GWfmz3n9Ujp+HwRt8UD2X8TdZDsAdQDD5IFEx/E0BSk6TVFMGHv60CPFBFQRVBdDDyQ9kAWHeOXapnVY9cox0HGwHwcySJjXFQLuq4VAx7y5c7YOapBZyu9GkDchmS0Atl6OtPsRc8ckoGAoSGyFRy//4G8kNvnt8307K4nZJFMzbd14ICCh972Xg9Htkw9KIZi5N9FzgAV4I1KrI8/oBjSDTwtKRQ=',
      'eJztlEsOwyAMRK+SGwAJ4Xf/g7WBLKgfkhFKpS7q5Wg8HmzjuJdcwzhbY4sOyF5cuMJUPG7RSyBIIKoMiLpy1OjrSsQPOL/rDbrwBhWriwzMgeHbBNsgB3VlSshkCA1ZFikJPtLE+9VGZ71FnMVE0jOVAjhMOiSSUJtJ2KaZpKVKmJK+tmBA4xvLwSXV1ydgqMt/eXB5avTKArkcCyTCIZTfnPbp+loS+V/p57zdyHm3H5Rw6ms1HKN+ZBduOzqpP3rUGOXDTvRfv+ar3j4HYos17gVMR7uJ',
      'eJzVVFsOgCAMu4o3YAjzwf0Ppiwx6ApiiCa4z6brYFtHwUkYSxIDjxrxC3AIENek84DjZ0AYEKjeWy1GnSWsEufqGoEs9hlllQXDSQ/kAiM9r8Soa/iqRlqbLzX2Fuk24shwHDh6XI+mLDSLQ2W0Dwc7xTDylzk6TAGjBkgBvZng37W4VCrdvoOSM+mVgpv/0o5mTvPNg2/OU70TFMjYDUN9NPA='
    )
  ),
)

PICTURE_ = shared.unpack("eJytkmEOwyAIha8EtSvsPETvf4Q9EWz1z7Jkpm366ROeCJGPQuv4mXVj27hu3HRj23gVgJcI3FYB1hdB5xb/kqy3VZ7MnpjfYLtPxkrBF6VKnHWy72SaTDa3Dz7xHhtfD6ZvfGxcZjyyOEpZ1m1ejMUsa5arF6iGSS8WZk5P0C/D9VJ7Dm54vJiHKAJIr0X1KD0NfsuoTfGAvvzg2jjZwGxee0ub8CzzLrAXtzNZmvsJPftsDfN5YYMrvV6nhxh8d0/demMwrfxoNun5IOdoH1iCxbs/vJO5BxgK/0puxWgaRY7aowoXPdYh0Ew9BOEuM+LY7me6OmUcNy3q0s7Zcv8ZH/vm6ME=")

COLORS_ = (
  (10,0,0),
  (0,10,0),
  (0,0,10)
)

MAP_ = (
  (0,7),
  (1,2),
  (3,4)
)
