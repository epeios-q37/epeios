# Microcontrolers unleashed

Python library for easy prototyping of assemblies based on microcontrollers such as *ESP32*, *ESP8266*, *Raspberry Pico (2) W*…

> Online demonstration available at https://zelbinium.q37.info/en/ucuq/.

## How to use it

### On the microcontroller

1. Install *Micropython* on the microcontroller;
2. create an *ucuq.json* file with below given content;
3. rename *ucuq_device.py* as *main.py*;
4. put *ucuq.json* and *main.py* on the microcontroller;
5. restart the microcontroller.

Content of the *ucuq.json* file:

```json
{
  "Identification": ["<device_token>","<device_id>"],
  "WLAN": {
    "<wlan_name>": ["<wlan_ssid>", "<wlan_key>"]
  },
  "OnBoardLed": [<led_pin>, <led_logic>],
}
```

- *&lt;device_token>*: token of the device ; choose one which can not be easily guessed; a token can be shared between several devices;
- *&lt;device_id>*: id of the device, must be unique among devices with same token;
- *&lt;wlan_name>*: name of the wlan (whatever value you want);
- *&lt;wlan_ssid>*: SSID of the wlan;
- *&lt;wlan_key>*: secret key of the wlan;
- *&lt;led_pin>*: the pin of the onboard led from the microcontroller (usually an integer, but can be a string, as with the *RPI pico (2) W*);
- *&lt;led_logic>*: `true` when the led lights up when the pin level is high, `false` otherwise.

The `OnBoardLed` entry can be omitted.

You can put more then one entry under the `WLAN`; the microcontroller will automatically connect to the available one. For example the first may be the smartphone's access point, the second your home's Wi-Fi.

### On you computer

1. Retrieve this repository;
2. launch the *Config* app (in the demos folder);
3. fill the field accordingly to the content of the *usuq.json* file described above (`Identification`/`device_token` and `Identification`/`device_id`);
4. click on *Save* and quit the app.

As an example, to light up a LED connected to your device, create a file with below code and adapt it to your microcrocontroller:

```python
import ucuq

ucuq.GPIO(<led_pin>).high()

ucuq.commit()
```

Replace `<led_pin>` with the number corresponding of the onboard led pin number or string (or of whichever led connected to your microcontroller). With some controller, the led lights up when the corresponding pin is at low level, so you have to replace `high` with `low`. Launch this program with *python3*.
