# Microcontrolers unleashed

Python library for easy prototyping of assemblies based on microcontrollers such as *ESP32*, *ESP8266*, *Raspberry Pico (2) W*…

> Online demonstrations: <https://zelbinium.q37.info/en/ucuq/>.

## How to use it

> Above link gives access to an *ESP32* simulation with *UCUq* installed on it and can be very helpful understanding how to do this on your own microcontroler.

### On the microcontroller

1. Install [*Micropython*](https://micropython.org/) on the microcontroller;
2. create an *ucuq.json* file with below content;
3. rename *ucuq_device.py* as *main.py*;
4. put both *ucuq.json* and *main.py* on the microcontroller;
5. restart the microcontroller.

Content of the *ucuq.json* file to put on the microcontroller:

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
- *&lt;led_pin>*: the pin of the onboard led from the microcontroller (usually an integer, but can be a string, as with the *RPI Pico (2) W*);
- *&lt;led_logic>*: `true` when the led lights up when the pin level is high, `false` otherwise.

The `OnBoardLed` entry is optional.

You can put more then one entry under the `WLAN`; the microcontroller will automatically connect to the first available one. For example, one can be your smartphone's access point, the second your home's WiFi.

### On you computer

1. Retrieve this repository;
2. launch the *Config* app (`python3 Config/` from the *demos* folder);
3. fill the fields accordingly to the content of the *usuq.json* file described above (`Identification`/`device_token` and `Identification`/`device_id`);
4. click on *Save* and quit the app.

As an example, to light up a LED connected to your device, create a file with below code and adapt it to your microcrocontroller:

```python
import ucuq

ucuq.GPIO(<led_pin>).high()
```

Replace `<led_pin>` with the number corresponding of the onboard led pin number or string (or of whichever led connected to your microcontroller). With some controllers, the led lights up when the corresponding pin is at low level, so you have to replace `high()` with `low()`. Launch this program with *python3*.

See the above online demonstrations link for the *API* and examples of use.

## The daemon

To simplify the use of this library, both the microcontroller and the local computer connects to a free public server.

You can use your own server by running the daemon available at: <https://github.com/epeios-q37/ucuq>.

Add also following entry to the *ucuq.json* file of the microcontroller:

```json
{
  …
  "Proxy": {
    "Host": "<address-of-the-server-hosting-the-deamon>",
    "Port": "<port-the-deamon-listens-to>"
  }
  …
}
```

The *Port* entry can be omitted if you use the default port.

You have also to modify the *Proxy* settings in the *Config* app launched on the local computer.
