Blockly.defineBlocksWithJsonArray([
  {
    "type": "gpio_init",
    "tooltip": "",
    "helpUrl": "",
    "message0": "GPIO init %1 %2 %3 pin %4",
    "args0": [
      {
        "type": "input_dummy",
        "name": "",
        "align": "CENTRE"
      },
      {
        "type": "field_input",
        "name": "LABEL",
        "text": "GPIO"
      },
      {
        "type": "input_dummy",
        "name": ""
      },
      {
        "type": "input_value",
        "name": "PIN",
        "align": "RIGHT",
        "check": "String"
      }
    ],
    "colour": 225,
    "previousStatement": null,
    "nextStatement": null,
  },
  {
    "type": "gpio_init_pin",
    "message0": "%1",
    "args0": [
      {
        "type": "field_input",
        "name": "PIN"
      }
    ],
    "output": null
  },
])  
