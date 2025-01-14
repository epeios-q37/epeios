Blockly.defineBlocksWithJsonArray([
  {
    "type": "ucuq_sleep",
    "tooltip": "",
    "helpUrl": "",
    "message0": "UCUq sleep %1 Seconds %2",
    "args0": [
      {
        "type": "input_dummy",
        "name": ""
      },
      {
        "type": "input_value",
        "name": "SECONDS",
        "align": "RIGHT",
        "check": "Number",
      },
    ],
    "colour": 225,
    "previousStatement": null,
    "nextStatement": null,
  },
  {
    "type": "ucuq_sleep_seconds",
    "message0": "%1",
    "args0": [
      {
        "type": "field_number",
        "name": "SECONDS",
        "min": 0,
      }
    ],
    "output": null
  },
]);
