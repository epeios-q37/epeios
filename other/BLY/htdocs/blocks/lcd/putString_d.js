Blockly.defineBlocksWithJsonArray([
  {
    "type": "lcd_putString",
    "tooltip": "",
    "helpUrl": "",
    "message0": "LCD putString %1 %2 %3 String %4",
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
        "name": "STRING",
        "align": "RIGHT",
        "check": "String"
      }
    ],
    "previousStatement": null,
    "nextStatement": null,
    "colour": 225
  },
  {
    "type": "lcd_putString_string",
    "message0": "%1",
    "args0": [
      {
        "type": "field_input",
        "name": "STRING"
      }
    ],
    "output": null
  },
])  
