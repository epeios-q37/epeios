Blockly.defineBlocksWithJsonArray([
  {
    "type": "ws2812_init",
    "tooltip": "",
    "helpUrl": "",
    "message0": "WS2812 init %1 %2 %3 Pin %4 Count %5",
    "args0": [
      {
        "type": "input_dummy",
        "name": ""
      },
      {
        "type": "field_input",
        "name": "LABEL",
        "text": "RGBs"
      },
      {
        "type": "input_dummy",
        "name": "",
        "align": "CENTRE"
      },
      {
        "type": "input_value",
        "name": "PIN",
        "align": "RIGHT",
        "check": "String"
      },
      {
        "type": "input_value",
        "name": "COUNT",
        "align": "RIGHT",
        "check": "Number"
      }
    ],
    "previousStatement": null,
    "nextStatement": null,
    "colour": 225
  },
  {
    "type": "ws2812_init_pin",
    "message0": "%1",
    "args0": [
      {
        "type": "field_input",
        "name": "PIN"
      }
    ],
    "output": null
  },
  {
    "type": "ws2812_init_count",
    "message0": "%1",
    "args0": [
      {
        "type": "field_number",
        "name": "COUNT",
        "value": 1,
        "min": 1
      }
    ],
    "output": null
  },
])  
