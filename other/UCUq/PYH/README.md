# Microcontrolers unleashed!

## How to use it

### On the microcontroller

1. Install *Micropython* on your microcontroller;
2. create an *ucuq.json* file with below given content;
3. rename *ucuq.py* as *main.py*;
4. put *ucuq.py* and *main.py* on your microcontroller;
5. restart the microcontroller.

Content of the *ucuq.json* file:

```json
{
  "WLAN": {
    "Known": {
      "<wlan_id>": ["<wlan_ssid>", "<wlan_key>"]
    },
  },
  "Selector": ["<device_token>","<device_id>"],
  "OnBoardLed": {
    "<device_id>": [<led_pin>, <led_logic>],
  }
}
```

- `<wlan_id>`: name given by the user to the wlan (it is not necessarily the SSID);
- `<wlan_ssid>`: SSID of the wlan;
- `<wlan_key>`: secret key of the wlan;
- `<device_token>`: token of the device ; choose one which can not be easily guessed ; a token can be shared between several devices;
- `<device_id>`: id of the device, must be unique among devices with the same token;
- `<led_pin>`: the pin of the onboard led from the microcontroller (usually a number, but can be a string, as with the *RPI pico W*);
- `<led_logic>`: `true` when the led lights up when the pin level is high, `false` otherwise.

The `<device_id>` under `OnBoardLed` section is the same as the one under `Selector`.

You can put more then one entry under the `WLAN`/`Known`; the microcontroller will automatically connect to the available one. For example the first may be the smartphone's access point, the second your home's Wi-Fi.

## on you compter

## with your *Python* *IDE*

1. Retrieve this repository;
2. put the `<path-to>/device` in your `PYTHONPATH` environment variable;
3. launch the *Config* app (in the demos folder);
4. fill the field accordingly with the content of the *usuq.json* file described above (`Selector`/`device_token` and `Selector`/`device_id`);
5. click on *Save* and quit the app;
6. create a file with below code and adapt it to your microcrocontroller,
7. launch this file with *python3*.

```python
import ucuq

ucuq.GPIO(<led_pin>).high()

ucuq.commit()
```

Replace `<led_pin>` with the number corresponding of the onboard led pin number or string (or of whichever led connected to your microcontroller). With some controller, the led lights up when the corresponding pin is at low level, so you have to replace `high` with `low`.

Launching this 



This project, together with the related documentation, including this file, is currently under development.

Prototype your microcontroller project easily by controlling it remotely with *Python*.

Install *MicroPython* on your microcontroller and place the files in the *device* directory there, adapting the contents of the *ucuq.json* file beforehand. You'll then be able to control your microcontroller remotely with *Python*, even from a web browser. No need to transfer dedicated software for each new component connected to your microcontroller.
