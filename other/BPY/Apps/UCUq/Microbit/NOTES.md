# Notes à propos du contenu de ce répertoire

Application permettant de piloter un Micro:Bit (v1&2) branché sur un ESP32-C3 super-mini grâce à la classe *ucuq.microbit*.

Code *micropython* à télécharger sur le Micro:Bit :

```python
from microbit import uart, display, sleep, running_time
import microbit

# --- Protocole framing ---
START = 0x7E
END = 0x7F

uart.init(baudrate=115200, tx=microbit.pin0, rx=microbit.pin1)

def checksum(data):
    return sum(data) & 0xFF

def find_byte(buf, value, start=0):
    for i in range(start, len(buf)):
        if buf[i] == value:
            return i
    return -1

def bytes_to_str(buf):
    return ''.join(chr(b) for b in buf)

def send_frame(payload_str):
    data = bytes(ord(c) for c in payload_str)
    frame = bytes([START, len(data)]) + data + bytes([checksum(data), END])
    uart.write(frame)

def read_frame():
    if uart.any() == 0:
        return None

    buf = uart.read()
    if not buf:
        return None

    s = find_byte(buf, START)
    if s < 0:
        return None

    e = find_byte(buf, END, s + 1)
    if e < 0:
        return None

    frame = buf[s:e+1]

    if len(frame) < 4:
        return None

    length = frame[1]
    if len(frame) < 3 + length + 1:
        return None

    payload = frame[2:2+length]
    cks = frame[2+length]

    if checksum(payload) != cks:
        return None

    return bytes_to_str(payload)

last_seq = None

anim_frames = []
anim_delay = 0
anim_loop = False
anim_index = 0
anim_next_time = 0
anim_running = False

def handle_message(msg):
    global last_seq
    global anim_frames, anim_delay, anim_loop
    global anim_index, anim_next_time, anim_running

    parts = msg.split(":", 1)
    if len(parts) != 2:
        return

    seq_str, content = parts
    if not seq_str.isdigit():
        return

    seq = int(seq_str)

    # --- SYNC ---
    if content == "SYNC":
        last_seq = None
        sleep(10)
        send_frame("ACK:%d" % seq)
        return

    # --- Doublon ---
    if last_seq is not None and seq == last_seq:
        sleep(10)
        send_frame("ACK:%d" % seq)
        return

    # --- Commandes ---
    if content == "CLR":
        display.clear()

    elif content.startswith("TXT:"):
        txt = content[4:]
        display.show(txt, wait=False)

    elif content.startswith("PIX:"):
        try:
            x, y, b = map(int, content[4:].split(","))
            display.set_pixel(x, y, b)
        except:
            pass

    elif content.startswith("IMG:"):
        data = content[4:]
        if len(data) == 25 and data.isdigit():
            for y in range(5):
                for x in range(5):
                    display.set_pixel(x, y, int(data[y*5 + x]))

    elif content.startswith("SCR:"):
        try:
            _, delay, text = content.split(":", 2)
            display.scroll(text, delay=int(delay), wait=False)
        except:
            pass

    elif content.startswith("GET:"):
        try:
            x, y = map(int, content[4:].split(","))
            b = display.get_pixel(x, y)
            sleep(5)
            send_frame("VAL:%d" % b)
        except:
            pass

    elif content == "OFF":
        display.off()

    elif content == "ON":
        display.on()

    elif content == "ISON":
        val = 1 if display.is_on() else 0
        sleep(5)
        send_frame("ION:%d" % val)

    elif content == "LUX":
        try:
            val = display.read_light_level()
            sleep(5)
            send_frame("LIG:%d" % val)
        except:
            pass

    # --- Animation non bloquante ---
    elif content.startswith("ANM:"):
        try:
            parts = content.split(":", 3)
            anim_delay = int(parts[1])
            anim_loop = bool(int(parts[2]))
            anim_frames = parts[3].split("|")

            anim_index = 0
            anim_running = True
            anim_next_time = running_time()
        except:
            pass

    elif content == "STOP":
        anim_running = False

    last_seq = seq

    # --- ACK ---
    sleep(10)
    send_frame("ACK:%d" % seq)


while True:
    msg = read_frame()
    if msg:
        handle_message(msg)

    if anim_running and running_time() >= anim_next_time:
        frame = anim_frames[anim_index]

        if len(frame) == 25 and frame.isdigit():
            for y in range(5):
                for x in range(5):
                    display.set_pixel(x, y, int(frame[y*5 + x]))

        anim_index += 1
        if anim_index >= len(anim_frames):
            if anim_loop:
                anim_index = 0
            else:
                anim_running = False

        anim_next_time = running_time() + anim_delay

    sleep(10)
```
