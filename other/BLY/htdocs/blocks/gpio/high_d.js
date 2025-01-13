Blockly.defineBlocksWithJsonArray([
  {
    "type": "gpio_high",
    "tooltip": "",
    "helpUrl": "",
    "message0": "GPIO high %1 %2 %3 state %4",
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
        "name": "STATE",
        "align": "RIGHT",
        "check": "Boolean"
      }
    ],
    "colour": 225,
    "previousStatement": null,
    "nextStatement": null,
  },
  {
    "type": "gpio_high_state",
    "message0": "%1",
    "args0": [
      {
        "type": "field_checkbox",
        "name": "STATE",
        "checked": "TRUE"
      }
    ],
    "output": null
  },
])  
