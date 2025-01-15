Blockly.defineBlocksWithJsonArray([
  {
    "type": "lcd_init",
    "tooltip": "",
    "helpUrl": "",
    "message0": "LCD init %1 %2 %3 Soft %4 SDA %5 SCL %6 Cols %7 Rows %8",
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
        "name": "SOFT",
        "align": "RIGHT",
        "check": "Boolean"
      },
      {
        "type": "input_value",
        "name": "SDA",
        "align": "RIGHT",
        "check": "Number"
      },
      {
        "type": "input_value",
        "name": "SCL",
        "align": "RIGHT",
        "check": "Number"
      },
      {
        "type": "input_value",
        "name": "COLS",
        "align": "RIGHT",
        "check": "Number"
      },
      {
        "type": "input_value",
        "name": "ROWS",
        "align": "RIGHT",
        "check": "Number"
      }
    ],
    "previousStatement": null,
    "nextStatement": null,
    "colour": 225
  },
  {
    "type": "lcd_init_soft",
    "message0": "%1",
    "args0": [
      {
        "type": "field_checkbox",
        "name": "SOFT"
      }
    ],
    "output": null
  },
  {
    "type": "lcd_init_sda",
    "message0": "%1",
    "args0": [
      {
        "type": "field_number",
        "name": "SDA",
        "min": 0
      }
    ],
    "output": null
  },
  {
    "type": "lcd_init_scl",
    "message0": "%1",
    "args0": [
      {
        "type": "field_number",
        "name": "SCL",
        "min": 0
      }
    ],
    "output": null
  },
  {
    "type": "lcd_init_cols",
    "message0": "%1",
    "args0": [
      {
        "type": "field_number",
        "name": "COLS",
        "min": 16
      }
    ],
    "output": null
  },
  {
    "type": "lcd_init_rows",
    "message0": "%1",
    "args0": [
      {
        "type": "field_number",
        "name": "ROWS",
        "min": 2
      }
    ],
    "output": null
  },
])  
