import ucuq, zlib, base64, time

from shared import polyphonicPlay, RAINBOW

ring = None
buzzer = None
oled = None
lcd = None

def connect(device):
  global ring, buzzer, oled, lcd
  ucuq.setDevice(device)
  
  ring = ucuq.Ravel.Ring()
  buzzer = ucuq.Ravel.Buzzer()
  oled = ucuq.Ravel.OLED()
  lcd = ucuq.Ravel.LCD()
  
SONG = "C44 D43 E43 F43 G43 A43 B43 C55"
#                   1234567890123456 
LINE1 = " " * 15 + " Pour l'avenir  "
LINE2 = " " * 15 + "de nos enfants !"

PERSONNES = """000000000000000000000000000000000000180000000000000ffe0000000000001ffe00000000000018c60000002000001807000001fc0000180601f003ff0000380707fc070780003fff0f1e0601c0003fff0c070c00c000180618030c00e000380618030c006000180618038c006000180618039c006000180618031c006000180618031c0060000c0c1803180060000e1c18031800600007381c071f03e00003f00e0e0fffe00001e007fc01fe0000000003f800000000000000e0000000001ffc000007ff0000ffff80000fffe003f007fffc0401f8078001fffc00001c060003e00020000e0c00070001f800060c00060003fc00070c000c00030e00070c000c00030600070c000c00030600070c301c00030e00c70c301c00039c00c70c301c0001f800c70c301c20007000c70c301c70000000c70c301c7000f800c71c301c700fff00c77c301c701fdfc0c77e301c703801c0c7e6301c703000e0c606301c70700060ce06301c70700060fc06300c70700260f806300c70760660c006300e30760660c006300770760660c0063003f0760660c0063001f0760660c006200070360660c0060000703e07e0c0060000701e07c0c0060000700e0700c0060000700606000006000070060600000600007006060000060000700606000000000073c602000000000003c000000000000000000000000000000000000000"""

MAINS = """00000000000000000000f800000000000001fc000000000000038e000000000001f303000000000007fe018000000000060e00c0000000000e070060000000000c030030000000000c018018000000000600c00c00000000060060060000000003003003000000000780180181f800000fc00c00c3fc00001ce00600670600003030030036030000301801801e018000300c00c00e00c000300600600700600038030030030030001c018018018018000e00c00c00c00c000600600000600600030030000030030001c018000018038003c00c00000c01800ff00600000600c00c380380000000e01818018000000060180c000000000070180700000100003018038001e7c000301c018003fefe00180e00e0073c7e00180600600e38e300180300001c71c7000c01800038e386000c00c00071c70f000c006000e38e19800c003001c11c31800c001803803861800c000c070070c3000c00060e002186000c00071c00070c000c0003b8000618000c0001f0000030000c0000f000006000180000600000c000180000600001c000180000600003e000300000600006600030000060000c60006000006000186000e00000600010c001c00000600001c0038000003000030007000000380006000e00000018000c003c0000000e003800f00000000780f807e000000003ffffff8000000000ff0ff800000000000000000000"""


def callback_(helper, events, duration):
  ucuq.sleepStart()
  
  for event in events:
    if event[1] > 0:
      buzzer.play(int(event[1]))

  ucuq.sleepWait(duration)
  
def hex_image_to_bytearray(hex_string, width=128, height=64):
    # 1. Convertir la chaîne hex en liste de bits (ligne par ligne)
    bits = []
    for c in hex_string:
        nibble = int(c, 16)
        bits.append((nibble >> 3) & 1)
        bits.append((nibble >> 2) & 1)
        bits.append((nibble >> 1) & 1)
        bits.append(nibble & 1)

    # 2. Réorganiser en format SSD1306 (pages de 8 lignes)
    pages = height // 8
    out = bytearray(width * pages)

    for page in range(pages):
        for x in range(width):
            byte = 0
            for bit in range(8):
                y = page * 8 + bit
                pixel = bits[y * width + x]
                byte |= (pixel << bit)  # LSB = pixel du haut
            out[page * width + x] = byte

    return out

  
def concat_hex_images(img1: str, img2: str) -> str:
    """
    Concatène horizontalement deux images 64x64 encodées en hexadécimal.
    Chaque image est une chaîne de 1024 caractères hex (64 lignes × 16 chars).
    Retourne une chaîne de 2048 caractères hex représentant une image 128x64.
    """
    if len(img1) != 1024 or len(img2) != 1024:
        raise ValueError("Chaque image doit faire exactement 1024 caractères hexadécimaux.")

    result_lines = []

    # 16 hex chars = 64 pixels
    for row in range(64):
        line1 = img1[row*16 : (row+1)*16]
        line2 = img2[row*16 : (row+1)*16]
        result_lines.append(line1 + line2)

    return "".join(result_lines)
  
  
def compress_to_string(data: bytearray) -> str:
    compressed = zlib.compress(bytes(data), level = 9, wbits = 9)
    return base64.b64encode(compressed).decode("ascii")
  
SCRIPT = """
import ubinascii, io
import deflate  # module interne selon port MicroPython

def decompress_from_string(s: str) -> bytearray:
    print(len(s))
    out = bytearray()
    raw = ubinascii.a2b_base64(s)
    with deflate.DeflateIO(io.BytesIO(raw)) as d:
        decompressed_data = d.read()
        
    return decompressed_data
"""
  
  
def launch():
  ringOffset = int(time.time()) % len(RAINBOW)
  ring.flash()
  lcd.clear().backlightOff()
  oled.powerOff()
  ucuq.sleep(0.5)
  polyphonicPlay((SONG,), 220, None, callback_)
  buzzer.off()
  lcd.backlightOn()
  ucuq.addCommand(SCRIPT)
  oled.powerOn()
  for c in range(64):
    toDraw = concat_hex_images(("0" * 16 * (63 - c) + PERSONNES)[:1024], (MAINS[16 * (63 - c):] + "0" * 1024)[:1024])
#    oled.draw(toDraw, 128)
#    ucuq.addCommand(f'{oled.getObject()}.buffer = bytes.fromhex("{hex_image_to_bytearray(toDraw).hex()}")')
    ucuq.addCommand(f'{oled.getObject()}.buffer = decompress_from_string("{compress_to_string(hex_image_to_bytearray(toDraw))}")')
    oled.show()
    color = RAINBOW[(c + ringOffset) % len(RAINBOW)]
    ring.setValue(c, color).setValue(63 - c, color).write()
  
    l = c // 2
    if l // 16 == 0:
      lcd.moveTo(0,0).putString(LINE1[l % 16:][:16])
    else:
      lcd.moveTo(0,1).putString(LINE2[l % 16:][:16])
      
  for l in range(8):
    ring.setValue(l, RAINBOW[( ringOffset + l * (len(RAINBOW)-1) // 7) % len(RAINBOW)]).write()
