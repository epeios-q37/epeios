Blockly.defineBlocksWithJsonArray([
  {
    "type": "ws2812_fill",
    "tooltip": "",
    "helpUrl": "",
    "message0": "WS2812 fill %1 %2 %3 R %4 G %5 B %6",
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
        "name": "R",
        "align": "RIGHT",
        "check": "Number"
      },
      {
        "type": "input_value",
        "name": "G",
        "align": "RIGHT",
        "check": "Number"
      },
      {
        "type": "input_value",
        "name": "B",
        "align": "RIGHT",
        "check": "Number"
      }
    ],
    "previousStatement": null,
    "nextStatement": null,
    "colour": 225
  },
  {
    "type": "ws2812_fill_r",
    "message0": "%1",
    "args0": [
      {
        "type": "field_number",
        "name": "R",
        "value": 0,
        "min": 0,
        "max": 255
      }
    ],
    "output": null
  },
  {
    "type": "ws2812_fill_g",
    "message0": "%1",
    "args0": [
      {
        "type": "field_number",
        "name": "G",
        "value": 0,
        "min": 0,
        "max": 255
      }
    ],
    "output": null
  },
  {
    "type": "ws2812_fill_b",
    "message0": "%1",
    "args0": [
      {
        "type": "field_number",
        "name": "B",
        "value": 0,
        "min": 0,
        "max": 255
      }
    ],
    "output": null
  },
])  
