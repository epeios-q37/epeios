Blockly.defineBlocksWithJsonArray([
  {
    "type": "preset",
    "tooltip": "",
    "helpUrl": "",
    "message0": "Preset %1 Id %2 Token %3",
    "args0": [
      {
        "type": "input_dummy",
        "name": "",
        "align": "CENTRE"
      },
      {
        "type": "input_value",
        "name": "ID",
        "align": "RIGHT"
      },
      {
        "type": "input_value",
        "name": "TOKEN",
        "align": "RIGHT"
      }
    ],
    "colour": 225,
    "previousStatement": null,
    "nextStatement": null,
  },
  {
    "type": "preset_id",
    "message0": "%1",
    "args0": [
      {
        "type": "field_input",
        "name": "ID"
      }
    ],
    "output": null
  },
  {
    "type": "preset_token",
    "message0": "%1",
    "args0": [
      {
        "type": "field_input",
        "name": "TOKEN"
      }
    ],
    "output": null
  }
]);
