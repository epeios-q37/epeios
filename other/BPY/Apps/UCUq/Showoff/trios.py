import base64  # noqa: I001
import copy
import json
import sys
import zlib

from dataclasses import dataclass
from fractions import Fraction

import shared
import ucuq

from show import (
  KIT_COUNT as _KIT_COUNT,
  sleepUntil as _sleepUntil,
  waitUntilNtpTime as _ntpSleep
)

# No debug if == 0
_DEBUG_DURATION = 0

_PANEL_WIDTH = ucuq.ravel.PANEL_WIDTH
_PANEL_STRIP_WIDTH = _PANEL_WIDTH * _KIT_COUNT
_PANEL_PEAK_WIDTH = 7 * 5
_PANEL_DURATION_POSITION = _PANEL_WIDTH // 2 + 2
_PANEL_SLOW_DURATION_WIDTH = 3
_PANEL_FAST_DURATION_WIDTH = 3

_SCREEN_HEIGHT = ucuq.ravel.SCREEN_HEIGHT
_SCREEN_WIDTH = ucuq.ravel.SCREEN_WIDTH

_PIANO_ROLL_KEYBOARD_HEIGHT = 5
_PIANO_ROLL_HEIGHT = _SCREEN_HEIGHT - _PIANO_ROLL_KEYBOARD_HEIGHT
_PIANO_ROLL_MARKER_WIDTH = 20
_PIANO_ROLL_VOICE_WIDTH = 39
_PIANO_ROLL_VOICES_START = (2, 44, 86)
_PIANO_ROLL_SEPARATOR_POSITIONS = (0, 42, 84, 126)
_FAST_SCROLL_HEIGHT= 9 * _PIANO_ROLL_HEIGHT // 10

_REGULAR_SCROLL_DELAY = .10
_START_SCROLL_DELAY = .05

_PANEL_TITLE_DELAY = 1/4

_RING_RAINBOW_DELAY = 1/3

_START_DELAY = (_FAST_SCROLL_HEIGHT * _START_SCROLL_DELAY) + _REGULAR_SCROLL_DELAY * (_PIANO_ROLL_HEIGHT - _FAST_SCROLL_HEIGHT)

_COMMIT_DELAY = .05

_SCREEN_ANTICIPATION = 0

_NOTE_UP_CHARMAP = (
  0b00001,
  0b00001,
  0b00001,
  0b00001,
  0b01111,
  0b11111,
  0b01110,
  0b00000,
)

_NOTE_DOWN_CHARMAP = (
  0b00000,
  0b00001,
  0b00001,
  0b00001,
  0b00001,
  0b01111,
  0b11111,
  0b01110,
)

@dataclass
class _Extremum:
  minNote: int
  maxNote: int


@dataclass
class _Monitoring:
  flags: list
  peaks: list


@dataclass
class _Tracking:
  voices: list
  extrema: list[_Extremum]
  monitoring: _Monitoring


def _isDebug():
  return _DEBUG_DURATION != 0


def _unpack(extrema):
  return [extremum.minNote for extremum in extrema], [extremum.maxNote for extremum in extrema]


def _decompressVoiceString(compressedString):
  decoded_base64 = base64.b64decode(compressedString.encode('ascii'))
  decompressed_bytes = zlib.decompress(decoded_base64)

  return decompressed_bytes.decode('utf-8')


def _parseVoice(decompressedString):
  duration = 0

  if not decompressedString.strip():
    return []
      
  noteList = []
  tokens = decompressedString.split(" ")
  
  for token in tokens:
    if not token:
        continue
    
    midiString, fractionString = token.split(":")
    midiNote = int(midiString)
    
    num, den = map(int, (fractionString if '/' in fractionString else fractionString + "/1").split("/"))
    duration += Fraction(num, den)

    if duration > 0.04:
      noteList.append([midiNote, duration])
      duration = 0
      
  return noteList


def _buzzerEvents(voice, turn, buzzer, stops):
  prevPitch = 0

  yield _START_DELAY

  for note in voice:
    pitch = note[0]
    delay = note[1]
    
    if pitch != 0 and prevPitch == pitch:
      buzzer.off()
      rest = min(delay / 2, 0.03)
      delay -= rest
      yield rest
    else:
      prevPitch = pitch

    buzzer.play(pitch)
    yield delay

  stops[turn] = True


def _ringsActiveNotesEvent(note, turn, counter, rings):
  for k in range(_KIT_COUNT):
    if k == turn:
      colors = _VOICES_MAIN_COLORS
      spots = _RING_SPOTS[0]
    else:
      colors = _VOICES_REPEATER_COLORS
      spots = _RING_SPOTS[2 if turn == 2 else (1 if turn == 0 or k == 0 else 2)]

    for spot in spots:
      rings[k].setValue(spot, (0, 0, 0))
      if note != 0:
        rings[k].setValue(spots[counter % len(spots)], colors[turn])

  rings.write()


def _ringsActiveNotesEvents(voice, turn, rings):
  rings[turn].fill(_VOICES_MAIN_COLORS[turn]).write()

  yield _START_DELAY / 9

  for l in range(2, 10):
    rings[turn].setValue(l, (0,0,0)).write()
    yield _START_DELAY / 9

  counter = 0

  for note in voice:
    _ringsActiveNotesEvent(note[0], turn, counter, rings)
  
    yield note[1]

    if note[0]:
      counter += 1


def _screenComputeNotePos(turn, note, minNote, maxNote):
  return _PIANO_ROLL_VOICES_START[turn] + ( _PIANO_ROLL_VOICE_WIDTH - 1 ) * ( note - minNote ) // ( maxNote - minNote )


def _screenDrawNote(index, pitch, minNote, maxNote, screen):
  if pitch:
    screen.pixel(_screenComputeNotePos(index, pitch, minNote, maxNote), 0, 1)


def _screenDrawMarker(turn, color, counter, screen):
  width = _PIANO_ROLL_VOICE_WIDTH - _PIANO_ROLL_MARKER_WIDTH
  trueX =  abs((counter % width) * 2 - width)
  screen.hLine( _PIANO_ROLL_VOICES_START[turn] + trueX, 0, _PIANO_ROLL_MARKER_WIDTH, color)


def _screenDrawSeparators(counter, screens):
  for position in _PIANO_ROLL_SEPARATOR_POSITIONS:
    for y in range(_SCREEN_HEIGHT):
      screens.pixel(position, y, 0 if ( y + counter ) % 7 else 1 )


def _screenPianoRollEvent(pitches, tracking, separatorCounter, screens):
  minNotes, maxNotes = _unpack(tracking.extrema)

  for t, pitch in enumerate(pitches):
    _screenDrawNote(t, pitch, minNotes[t], maxNotes[t], screens)

  for t, screen in enumerate(screens):
    _screenDrawMarker(t, 1, separatorCounter, screen)
      
  screens.show()

  for t, screen in enumerate(screens):
    _screenDrawMarker(t, 0, separatorCounter, screen)
    _screenDrawNote(t, pitches[t], minNotes[t], maxNotes[t], screen)
  
  screens.scroll(dx=0, dy=1).hLine(0, 0, _SCREEN_WIDTH, 0)
  _screenDrawSeparators(separatorCounter, screens)


def _getExtrema(voice):
  minNote = sys.maxsize
  maxNote = 0

  for note in voice:
    pitch = note[0]
    if pitch:
      minNote = min(minNote, pitch)
      maxNote = max(maxNote, pitch)
    
  return _Extremum(minNote = minNote, maxNote = maxNote)


def _getPacedNotes(tracking):
  elapsed = 0
  pacedNotes = []

  voices = copy.deepcopy(tracking.voices)

  while len(voices[0]) and len(voices[1]) and len(voices[2]):
    pitches = (voices[0][0][0], voices[1][0][0], voices[2][0][0])
    start = elapsed < _FAST_SCROLL_HEIGHT * _REGULAR_SCROLL_DELAY
    pacedNotes.append((pitches, _START_SCROLL_DELAY if start else _REGULAR_SCROLL_DELAY))
    for voice in voices:
      voice[0][1] -= _REGULAR_SCROLL_DELAY
      while len(voice) and voice[0][1] <= 0:
        if len(voice) > 2:
          voice[1][1] += voice[0][1]
        del voice[0]
    elapsed += _REGULAR_SCROLL_DELAY

  for _ in range(_PIANO_ROLL_HEIGHT):
    pacedNotes.append(((0,) * len(tracking.voices), _START_SCROLL_DELAY if start else _REGULAR_SCROLL_DELAY))

  return pacedNotes


def _screenActiveNotesEvent(pitches, tracking, screens):
  minNotes, maxNotes = _unpack(tracking.extrema)

  for start in _PIANO_ROLL_VOICES_START:
    screens.rect(start, _PIANO_ROLL_HEIGHT, _PIANO_ROLL_VOICE_WIDTH, _SCREEN_HEIGHT - _PIANO_ROLL_HEIGHT, 0, True )

  for t, pitch in enumerate(pitches):
    if pitch:
      pos = _screenComputeNotePos(t, pitch, minNotes[t], maxNotes[t])

      screens\
        .rect(pos - 1, _PIANO_ROLL_HEIGHT, 3, 4, 0, True)\
        .vLine(pos - 1, _PIANO_ROLL_HEIGHT, 2, 1)\
        .vLine(pos + 1, _PIANO_ROLL_HEIGHT, 2, 1)\
        .vLine(pos, _PIANO_ROLL_HEIGHT + 2, 2, 1)


def _screenEvents(pacedNotes, tracking, screens):
  for i in range(len(pacedNotes)):
    if i >= _PIANO_ROLL_HEIGHT:
      _screenActiveNotesEvent(pacedNotes[i-_PIANO_ROLL_HEIGHT][0], tracking, screens)
    _screenPianoRollEvent(pacedNotes[i][0], tracking, i, screens)

    yield pacedNotes[i][1] - ( _SCREEN_ANTICIPATION if i == 0 else 0 )


def _panelActiveNotesEvent(monitoring, panels):
  notes = ['-' if flag is None else chr( 7 - flag ) for flag in (monitoring.flags)]

  for t, panel in enumerate(panels):
    peak = monitoring.peaks[t]

    if peak is None:
      peakString = panel.getEmptyPeak(_PANEL_PEAK_WIDTH)
    else:
      peakString = panel.getForwardPeak(peak, _PANEL_PEAK_WIDTH)

    panel\
      .moveTo(0, 1)\
      .putString("".join([*notes[:t], peakString, *notes[t+1:]]))


def _panelActiveNotesEvents(voice, turn, extremum, monitoring, panels):
  ambitus = extremum.maxNote - extremum.minNote

  yield _START_DELAY - .02

  for note in voice:
    pitch = note[0]

    monitoring.flags[turn] = None if pitch == 0 else not monitoring.flags[turn]
    monitoring.peaks[turn] = None if pitch == 0 else ( _PANEL_PEAK_WIDTH - 1 ) * ( pitch - extremum.minNote ) // ambitus

    _panelActiveNotesEvent( monitoring, panels)

    yield note[1]


def _ringsRainbowEvent(counter, rings):
  for r, ring in enumerate(rings):
    color = shared.getRainbowColor(counter + r * len(shared.RAINBOW) // _KIT_COUNT)
    for spot in _RING_SPOTS[3]:
      ring.setValue(spot, color)

  rings.write()


def _ringsRainbowEvents(duration, rings):
  yield _START_DELAY
  
  elapsed = counter = 0
  
  while elapsed < duration:
    _ringsRainbowEvent(counter, rings)

    yield _RING_RAINBOW_DELAY

    elapsed += _RING_RAINBOW_DELAY
    counter += 1


def _getTitleRibbon(title):
  yield from _PANEL_STRIP_WIDTH // 8 * "\06\07\06 \07\06\07 "

  paddedTitle = title + "  \06\07\06 \07\06\07 \06\07\06  "

  counter = 0

  while True:
    yield paddedTitle[counter % len(paddedTitle)]
    counter += 1


def _panelTitleEvents(title, panels):
  panelStrip = ucuq.PanelStrip(panels)

  titleRibbonGenerator = _getTitleRibbon(title)
  stripText = "".join(next(titleRibbonGenerator) for _ in range(_PANEL_STRIP_WIDTH))
  
  while True:
    panelStrip.moveTo(0, 0).putString(stripText)
    stripText = stripText[1:] + next(titleRibbonGenerator)

    yield _PANEL_TITLE_DELAY


def _panelDurationEvent(counter, panels):
  if ( fast:= counter % 15 ) == 0:
    x = _PANEL_DURATION_POSITION
    text = panels[0].getForwardPeak(_PANEL_SLOW_DURATION_WIDTH * 5 - counter // 15 - 1, _PANEL_SLOW_DURATION_WIDTH * 5)
  else:
    x = _PANEL_DURATION_POSITION + _PANEL_SLOW_DURATION_WIDTH
    text = ""

  panels\
    .moveTo(x, 1)\
    .putString(text + (panels[0].getForwardPeak(fast, 15)))


def _panelDurationEvents(duration, panels):
  yield _START_DELAY

  delay = duration / ( _PANEL_SLOW_DURATION_WIDTH * _PANEL_FAST_DURATION_WIDTH * 5 * 5)

  for counter in range(_PANEL_SLOW_DURATION_WIDTH * _PANEL_FAST_DURATION_WIDTH * 5 * 5):
    _panelDurationEvent(counter, panels)
    yield delay


def set(dom):
  html = ""

  for scoreId in _SCORE_LIST:
    selected = scoreId == "Bartok" if _isDebug() else False
    html += f'<option value="{scoreId}"{" selected" if selected else ""}>{scoreId}</option>'

  dom.inner("ShowTrios", html)

  if _isDebug():
    dom.removeAttribute("ShowCountdown", "checked")


def _sleepCallback(report, tracking, startTimestamp):
  if not _sleepUntil(startTimestamp + report.cumul, _COMMIT_DELAY):
    return False

  if _isDebug() and report.cumul > _DEBUG_DURATION:
    return False

  return any(stop == False for stop in tracking.stops)


def _getDuration(voice):
  duration = 0

  for note in voice:
    duration += note[1]

  return duration


def launch(scoreId, timestamp, parts):
  stops = [False] * _KIT_COUNT

  tracking = _Tracking(
    voices = [],
    extrema = [],
    monitoring = _Monitoring(
      flags = [None] * _KIT_COUNT,
      peaks = [None] * _KIT_COUNT
    )
  )

  parts.panels\
    .uploadHPeakChars()\
    .createChar(6, _NOTE_UP_CHARMAP)\
    .createChar(7, _NOTE_DOWN_CHARMAP)

  timestamp = timestamp + 1
  _sleepUntil(timestamp, 0)

  maxDuration = 0

  for turn, voice in enumerate(_SCORES[scoreId][1]):
    tracking.voices.append(_parseVoice(_decompressVoiceString(voice)))
    tracking.extrema.append(_getExtrema(tracking.voices[turn]))

  pacedNotes = _getPacedNotes(tracking)

  for voice in tracking.voices:
    maxDuration = max(maxDuration, _getDuration(voice))

  tracking.maxDuration = maxDuration

  cb = ucuq.getCommitBehavior()

  if _COMMIT_DELAY != 0:
    #    eventList.append(getCommitEvents_(maxDuration + START_DELAY_))
    cb = ucuq.setCommitBehavior(ucuq.CB_MANUAL)

  parts.panels.backlightOn()

  for turn in range(_KIT_COUNT):
    for spot in _RING_SPOTS[0]:
      parts.rings[turn].setValue(spot, _VOICES_MAIN_COLORS[turn])

  parts.rings.write()

  _panelActiveNotesEvent(tracking.monitoring, parts.panels)
  _panelDurationEvent(0, parts.panels)

  # ucuq.gcDisable()

  # ucuq.bleOff()

  timestamp += ucuq.dispatchEvents(
    (
      *(element for turn, voice in enumerate(tracking.voices) for element in (
          _ringsActiveNotesEvents(voice, turn, parts.rings),
          _panelActiveNotesEvents(voice, turn, tracking.extrema[turn], tracking.monitoring, parts.panels),
          _buzzerEvents(voice, turn, parts.buzzers[turn], stops),
        )
      ),
      _screenEvents(pacedNotes, tracking, parts.screens),
      _panelTitleEvents(_SCORES[scoreId][0], parts.panels),
      _panelDurationEvents(maxDuration, parts.panels),
      _ringsRainbowEvents(maxDuration, parts.rings)
    ),
    lambda report, tracking: _sleepCallback(report, tracking, timestamp),
    stops = stops
  )

  # ucuq.gcEnable()

  # ucuq.bleOn()

  ucuq.setCommitBehavior(cb)

  parts.buzzers.play(0)
  parts.screens.fill(0).show()
  parts.panels.clear().backlightOff()
  parts.rings.fill((0, 0, 0)).write()


_SCORE_LIST = tuple(sorted((
    "Titelouze", "BWV 528a", "BWV 528b", "BWV 528c", "Ano. Lobt Gott",
    "BWV 848b", "BWV 847b", "Gimo 359a", "Gimo 359c", "Bartok",
    "Brahms", "Elgar", "Plaisir d'amour", "Rachmaninov", "BVW 530",
    "RV63", "Hob. XI:10", "Sheba", "Beethoven 87-4", "Beethoven 3-1",
    "Beethoven 3-2", "Beethoven 3-3", "Beethoven 3-4", "Beethoven 3-5", "Beethoven 3-6")))

print(_SCORE_LIST)

_SCORE_LIST  = _SCORE_LIST + ("Test",)

with open("scores.json", "r", encoding="utf-8") as j:
  _SCORES = json.load(j)

_PICTURE = shared.unpack("eJytkmEOwyAIha8EtSvsPETvf4Q9EWz1z7Jkpm366ROeCJGPQuv4mXVj27hu3HRj23gVgJcI3FYB1hdB5xb/kqy3VZ7MnpjfYLtPxkrBF6VKnHWy72SaTDa3Dz7xHhtfD6ZvfGxcZjyyOEpZ1m1ejMUsa5arF6iGSS8WZk5P0C/D9VJ7Dm54vJiHKAJIr0X1KD0NfsuoTfGAvvzg2jjZwGxee0ub8CzzLrAXtzNZmvsJPftsDfN5YYMrvV6nhxh8d0/demMwrfxoNun5IOdoH1iCxbs/vJO5BxgK/0puxWgaRY7aowoXPdYh0Ew9BOEuM+LY7me6OmUcNy3q0s7Zcv8ZH/vm6ME=")

_VOICES_MAIN_COLORS = (
  (10,0,0),
  (0,10,0),
  (0,0,10)
)

_VOICES_REPEATER_COLORS = (
  (5,1,1),
  (1,5,1),
  (1,1,5)
)

_RING_SPOTS = (
  (1,2),
  (0,3),
  (7,4),
  (5,6)
)
