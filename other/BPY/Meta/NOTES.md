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

`convert <source>> -monochrome -depth 1 gray:- | xxd -p -c 100000 | tr -d '\n' | xclip -selection clipboard`
