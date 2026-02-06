# À propos de ce répertoire

Contient les applications qui sont communes à *Brython* et *Python*.

Pour lancer la version *Brython* : `BPYB_Launch <app_dir>`.
Pour lancer la version *Python* : `BPYP_Launch <app_dir>`.

## Utilisation des version de développement

### Version Python

Modifier *ucuq.json*.

Si utilisation version *Linux* (par opposition à la VM *Windows*), couper *stunnel*.

### Version *Brython*

Modifier le script *B/Launch*.

## Mise en œuvre de *UCUqXDevice*

*UCUqXDevice* permet d'ajouter un *device*, servant généralement de mirroir.

Pour cela, placer un `xdh:onevent="dblclick|UCUqXDevice"` sur l'élément qui va servir de déclencheur de l'affichage de l'interface permettant de saisir les paramètre du nouveau *device*, et créer la fonction `async def UCUqXDevice(dom, device):` afin de créer, à partir de `device`, les différents composants utilisés.

## Passage du code source en paramètre

À l'instar du code XML pour *Blockly*, le code source passé à *Brython*, via le paramètre *code*, est compressé puis encodé en base 64 et en paramètre d'URL. La (dé)compression se fait à l'aide des scripts *Q_(un)packURI*.

Codes JS équivalent (s'appuie sur [*pako*](https://cdnjs.com/libraries/pako)) :

```js
function pack(originalString) {
    const compressed = pako.deflate(originalString, { to: 'string' });
    
    let binaryString = '';

    for (let i = 0; i < compressed.length; i++) {
        binaryString += String.fromCharCode(compressed[i]);
    }
    
    return encodeURIComponent(btoa(binaryString));
}

function unpack(packedCode) {
  const binaryString = atob(decodeURIComponent(packedCode));
  
  const len = binaryString.length;
  const bytes = new Uint8Array(len);

  for (let i = 0; i < len; i++) {
      bytes[i] = binaryString.charCodeAt(i);
  }

  return pako.inflate(bytes, { to: 'string' });
}
```

## Aide pour générer les macros pour l'application *Servos*

Sélectionner les macros et puis sélectionner *Run Command* à partir du menu contextuel.

Les scripts sont gérés par l'extension *VSCode* *Command runner* et définis dans le *workspace* du projet.

## Publication de la version *Python* sur *Pypi* (*ucuq-python*)

- Mettre à jour, dans `setup.py` :
  - le numéro de version,
  - éventuellement la description.
- mettre à jour le dépôt *Github*.

**Attention** : vérifier que la version de *wheel* (`pip3 show wheel`) est >= 31.0, sinon mettre à jour (`pip3 install --user --upgrade wheel`), faute de quoi la description en *markdown* n'est pas affichée correctement (mettre à jour *twine* et/ou *setuptools* peut aussi être nécessaire).

Dans `RTW/ucuq-python` :

```bash
rm -rf atlastk.zip ucuq_device.py demos
mkdir ucuq;mv * ucuq;mv ucuq/setup.py .
echo -e 'name="ucuq"\nfrom ucuq import *' >ucuq/__init__.py
python3 setup.py sdist bdist_wheel
```

`python3 -m twine upload dist/*` (le *token* se trouve dans le fichier *Comptes.md*).

## *Firmware* d'origine

- lecture `esptool.py read_flash 0x00000 <size> <file>`
- écriture : `esptool.py write_flash 0x00000 <file>`

*<size>* : taille de la flash en hexa (ex. : `0x400000` pour un 4MB, `0x800000` pour une 8 MB…) ;
*<file>* : nom du fichier contenant le *firmware* (généralement avec l'extemsion `.bin`).

## Brochage *ESP32-C3* de *TenStar*

Vu de dessus, USB en-haut.

| G | G | G | D | D | D
|---|---|---|---|---|---
| GPIO5 | A3 | D3 | | 5V
| GPIO6 | SDA | D4 | | GND
| GPIO7 | SCL | D5 | | 3V3
| GPIO8 | SCK | D8 | GPIO4 | A2 | D2
| GPIO9 | MISO | D9 | GPIO3 | A1 | D1
| GPIO10 | MOSI | D10 | GPIO2 | A0 | D0
| GPIO20 | RX | D7 | GPIO1 | ADC1-1
| GPIO21 | TX | D6 | GPIO0 | ADC1-0

## *E-paper*

Driver : <https://github.com/mcauser/micropython-waveshare-epaper>,

### E-paper WeAct 2.13"

Branchement de l'e-paper 2.13" de *WeAct* sur l'*ESP32-C3* mini de *TenStar* :

| e-paper | ESP32-C3  | param.
|---|---|---
| VCC                      | 3.3V
| GND                      | GND
| BUSY                     | GPIO 3                       | busy
| RES (reset)              | GPIO 2                       | rst
| D/C (data/command)       | GPIO 1                       | dc
| CS (chip select)         | GPIO 7                       | cs
| SCL (SPI clock)          | GPIO 4                       | sck
| SDA (SPI data)           | GPIO 6                       | mosi

Driver alternatif : <https://github.com/peterhinch/micropython-nano-gui/blob/master/drivers/epaper/epd29_ssd1680.py>

### CRow 2.19"

Documentation : <https://www.elecrow.com/wiki/CrowPanel_ESP32_E-paper_2.9-inch_HMI_Display.html>

### Outils

## Convertir une image en hexadécimale (pour OLED)

`convert <source> -monochrome -depth 1 gray:- | xxd -p -c 100000 | tr -d '\n' | xclip -selection clipboard`

## *micro:bit*

Pilotage d'un *micro:bit* via un ESP32.

### *IDE* *Python* en ligne

Pour pouvoir téléverser un programme Python à partir de l'IDE en ligne, il faut utiliser *Chrome* (ou apparenté).

Sous *Ubuntu*, il faut procèder aux modifications suivantes (<https://support.microbit.org/support/solutions/articles/19000105428-webusb-troubleshooting>, section *Linux*) :

```bash
# Create rule
sudo cat << EOF >> /etc/udev/rules.d/50-microbit.rules
SUBSYSTEM=="usb", ATTR{idVendor}=="0d28", MODE="0664", GROUP="plugdev"
EOF

# Add current user to plugdev group
sudo usermod -a -G plugdev $USER

# Reload udev rules
sudo udevadm control --reload-rules
```

Débrancher/rebrancher le *micro:bit* et relancer *Chrome*.

### Code facilitant le débogage

Prmet d'afficher le résultat d'un *print* dans une console à l'aide de la commande ` :

```python
def p(*args, **kwargs):
    uart.init(baudrate=115200)
    print(*args, **kwargs)
    uart.init(baudrate=115200, tx=pin0, rx=pin1)
    
    
try:
    # Programme principal
except Exception as e:
    p(e)
```

### Code *micro:bit*

```python
from microbit import *

# --- Protocole framing ---
START = 0x7E
END = 0x7F

uart.init(baudrate=115200, tx=pin0, rx=pin1)

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

# --- Gestion du protocole ---
last_seq = None

# --- Gestion des animations non bloquantes ---
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

    elif content == "LUX":
        try:
            val = display.read_light_level()
            sleep(5)
            send_frame("LIG:%d" % val)
        except:
            pass
            
        
        
    # --- Mise à jour du numéro de séquence ---
    last_seq = seq

    # --- ACK ---
    sleep(10)
    send_frame("ACK:%d" % seq)

    


# --- Boucle principale ---
while True:
    msg = read_frame()
    if msg:
        handle_message(msg)

    # --- Tick d’animation non bloquante ---
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
