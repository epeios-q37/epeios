Blockly.defineBlocksWithJsonArray([
  {
    "type": "ws2812_setValue",
    "tooltip": "",
    "helpUrl": "",
    "message0": "WS2812 setValue %1 %2 %3 Index %4 R %5 G %6 B %7",
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
        "name": "INDEX",
        "align": "RIGHT",
        "check": "Number"
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
    "type": "ws2812_setValue_index",
    "message0": "%1",
    "args0": [
      {
        "type": "field_number",
        "name": "INDEX",
        "value": 0,
        "min": 0
      }
    ],
    "output": null
  },
  {
    "type": "ws2812_setValue_r",
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
    "type": "ws2812_setValue_g",
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
    "type": "ws2812_setValue_b",
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
