Blockly.defineBlocksWithJsonArray([
  {
    "type": "lcd_moveTo",
    "tooltip": "",
    "helpUrl": "",
    "message0": "LCD moveTo %1 %2 %3 X %4 Y %5",
    "args0": [
      {
        "type": "input_dummy",
        "name": ""
      },
      {
        "type": "field_input",
        "name": "LABEL",
        "text": "LCD"
      },
      {
        "type": "input_dummy",
        "name": "",
        "align": "CENTRE"
      },
      {
        "type": "input_value",
        "name": "X",
        "align": "RIGHT",
        "check": "Number"
      },
      {
        "type": "input_value",
        "name": "Y",
        "align": "RIGHT",
        "check": "Number"
      }
    ],
    "previousStatement": null,
    "nextStatement": null,
    "colour": 225
  },
  {
    "type": "lcd_moveTo_x",
    "message0": "%1",
    "args0": [
      {
        "type": "field_number",
        "name": "X",
        "min": 0
      }
    ],
    "output": null
  },
  {
    "type": "lcd_moveTo_y",
    "message0": "%1",
    "args0": [
      {
        "type": "field_number",
        "name": "Y",
        "min": 0
      }
    ],
    "output": null
  },
])  
