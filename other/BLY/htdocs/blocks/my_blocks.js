const test_JSON = {
  "type": "test",
  "message0": "move by %1 pixels",
  "args0": [
    {
      "type": "input_value",
      "name": "PIXELS"
    }
  ],
  "inputsInline": true,
  "previousStatement": null,
  "nextStatement": null
}
                    
const test = {
  init: function() {
    this.jsonInit(test_JSON);
  }
};

const test_shadow_JSON = {
  "type": "test_shadow",
  "message0": "%1",
  "args0": [
    {
      "type": "field_number",
      "name": "NUMBER",
      "min": 1,
      "precision": 1
    }
  ],
  "output": "Number"
};

const test_shadow = {
  init: function() {
    this.jsonInit(test_shadow_JSON);
  }
}

const ws2812_init_JSON = {
  "type": "ws2812_init",
  "tooltip": "",
  "helpUrl": "",
  "message0": "%1 %2 %3 %4 %5 %6 %7 %8",
  "args0": [
    {
      "type": "field_label_serializable",
      "text": "WS2812 init",
      "name": "BLOCK_LABEL"
    },
    {
      "type": "field_label_serializable",
      "text": "label",
      "name": "NAME_LABEL"
    },
    {
      "type": "field_input",
      "name": "NAME",
      "text": "WS2812"
    },
    {
      "type": "field_label_serializable",
      "text": "pin",
      "name": "PIN_LABEL"
    },
    {
      "type": "field_input",
      "name": "PIN",
      "text": ""
    },
    {
      "type": "field_label_serializable",
      "text": "count",
      "name": "COUNT_LABEL"
    },
    {
      "type": "field_number",
      "name": "COUNT",
      "value": 0,
      "min": 1
    },
    {
      "type": "input_dummy",
      "name": "NAME"
    }
  ],
  "previousStatement": null,
  "nextStatement": null,
  "colour": 225
};
                    
const ws2812_init = {
  init: function() {
    this.jsonInit(ws2812_init_JSON);
    this.setTooltip('');
    this.setHelpUrl('');
    this.setColour(225);
  }
};

const ws2812_fill_JSON = {
  "type": "ws2812_fill",
  "tooltip": "",
  "helpUrl": "",
  "message0": "%1 %2 %3 %4 %5 %6 %7 %8 %9 %10",
  "args0": [
    {
      "type": "field_label_serializable",
      "text": "WS2812 fill",
      "name": "BLOCK_LABEL"
    },
    {
      "type": "field_label_serializable",
      "text": "label",
      "name": "NAME_LABEL"
    },
    {
      "type": "field_input",
      "name": "NAME",
      "text": "WS2812"
    },
    {
      "type": "field_label_serializable",
      "text": "R",
      "name": "R_LABEL"
    },
    {
      "type": "field_variable",
      "name": "R",
      "variable": "R"
    },
    {
      "type": "field_label_serializable",
      "text": "G",
      "name": "G_LABEL"
    },
    {
      "type": "field_variable",
      "name": "G",
      "variable": "G"
    },
    {
      "type": "field_label_serializable",
      "text": "B",
      "name": "B_LABEL"
    },
    {
      "type": "field_variable",
      "name": "B",
      "variable": "B"
    },
    {
      "type": "input_dummy",
      "name": "NAME"
    }
  ],
  "previousStatement": null,
  "nextStatement": null,
  "colour": 225
};

const ws2812_fill = {
  init: function() {
    this.jsonInit(ws2812_fill_JSON);
    this.setTooltip('');
    this.setHelpUrl('');
    this.setColour(225);
  }
};

const ws2812_value_JSON = {
  "type": "ws2812_value",
  "tooltip": "",
  "helpUrl": "",
  "message0": "%1 %2 %3 %4 %5 %6 %7 %8 %9 %10 %11 %12 %13 %14",
  "args0": [
    {
      "type": "field_label_serializable",
      "text": "WS2812 value",
      "name": ""
    },
    {
      "type": "input_dummy",
      "name": "",
      "align": "CENTRE"
    },
    {
      "type": "field_input",
      "name": "NAME",
      "text": "WS2812"
    },
    {
      "type": "input_dummy",
      "name": "",
      "align": "RIGHT"
    },
    {
      "type": "field_label_serializable",
      "text": "index",
      "name": "INDEX_LABEL"
    },
    {
      "type": "field_variable",
      "name": "INDEX",
      "variable": "index"
    },
    {
      "type": "input_dummy",
      "name": ""
    },
    {
      "type": "field_label_serializable",
      "text": "R",
      "name": "R_LABEL"
    },
    {
      "type": "field_variable",
      "name": "R",
      "variable": "R"
    },
    {
      "type": "field_label_serializable",
      "text": "G",
      "name": "G_LABEL"
    },
    {
      "type": "field_variable",
      "name": "G",
      "variable": "G"
    },
    {
      "type": "field_label_serializable",
      "text": "B",
      "name": "B_LABEL"
    },
    {
      "type": "field_variable",
      "name": "B",
      "variable": "B"
    },
    {
      "type": "input_dummy",
      "name": ""
    }
  ],
  "previousStatement": null,
  "nextStatement": null,
  "colour": 225
}

const ws2812_value = {
  init: function() {
    this.jsonInit(ws2812_value_JSON);
    this.setTooltip('');
    this.setHelpUrl('');
    this.setColour(225);
  }
};

const ws2812_write_JSON = {
  "type": "ws2812_write",
  "tooltip": "",
  "helpUrl": "",
  "message0": "%1 %2 %3 %4",
  "args0": [
    {
      "type": "field_label_serializable",
      "text": "WS2812 write",
      "name": ""
    },
    {
      "type": "input_dummy",
      "name": "",
      "align": "CENTRE"
    },
    {
      "type": "field_input",
      "name": "NAME",
      "text": "WS2812"
    },
    {
      "type": "input_dummy",
      "name": "",
      "align": "RIGHT"
    }
  ],
  "previousStatement": null,
  "nextStatement": null,
  "colour": 225
}; 

const ws2812_write = {
  init: function() {
    this.jsonInit(ws2812_write_JSON);
    this.setTooltip('');
    this.setHelpUrl('');
    this.setColour(225);
  }
};

const sleep_var_JSON = {
  "type": "sleep_var",
  "tooltip": "",
  "helpUrl": "",
  "message0": "sleep %1 secs %2 %3",
  "args0": [
    {
      "type": "input_dummy",
      "name": "",
      "align": "CENTRE"
    },
    {
      "type": "field_variable",
      "name": "SECS",
      "variable": "secs"
    },
    {
      "type": "input_dummy",
      "name": "NAME"
    }
  ],
  "colour": 225,
  "previousStatement": null,
  "nextStatement": null,
};                   

const sleep_var = {
  init: function() {
    this.jsonInit(sleep_var_JSON);
    this.setTooltip('');
    this.setHelpUrl('');
    this.setColour(225);
  }
};


Blockly.common.defineBlocks({
  test: test,
  test_shadow: test_shadow,
  ws2812_init: ws2812_init,
  ws2812_fill: ws2812_fill,
  ws2812_value: ws2812_value,
  ws2812_write: ws2812_write,
  sleep_var: sleep_var,
});
                    
python.pythonGenerator.forBlock['ws2812_init'] = function(block) {
  const text_name = block.getFieldValue('NAME');
  const text_pin = block.getFieldValue('PIN');
  const number_count = block.getFieldValue('COUNT');

  const int_pin = parseInt(text_pin, 10);

  const normalized_pin = isNaN(int_pin) ? `"${text_pin}"` : int_pin;

  const code = `object["WS2812"]["${text_name}"] = ucuq.WS2812(${normalized_pin}, ${number_count})\n`;
  return code;
}

python.pythonGenerator.forBlock['ws2812_fill'] = function(block, generator) {
  const text_name = block.getFieldValue('NAME');
  const variable_r = generator.getVariableName(block.getFieldValue('R'));
  const variable_g = generator.getVariableName(block.getFieldValue('G'));
  const variable_b = generator.getVariableName(block.getFieldValue('B'));

  // TODO: Assemble python into the code variable.
  const code = `object["WS2812"]["${text_name}"].fill([${variable_r},${variable_g},${variable_b}])\n`;
  
  return code;
}

python.pythonGenerator.forBlock['ws2812_value'] = function(block, generator) {
  const text_name = block.getFieldValue('NAME');

  const variable_index = generator.getVariableName(block.getFieldValue('INDEX'));

  const variable_r = generator.getVariableName(block.getFieldValue('R'));
  const variable_g = generator.getVariableName(block.getFieldValue('G'));
  const variable_b = generator.getVariableName(block.getFieldValue('B'));

  // TODO: Assemble python into the code variable.
  const code = `object["WS2812"]["${text_name}"].setValue(${variable_index}, [${variable_r},${variable_g},${variable_b}])\n`;
  return code;
}

python.pythonGenerator.forBlock['ws2812_write'] = function(block) {
  const text_name = block.getFieldValue('NAME');

  // TODO: Assemble python into the code variable.
  const code = `object["WS2812"]["${text_name}"].write()\n`
  return code;
}

python.pythonGenerator.forBlock['sleep_var'] = function(block, generator) {
  const variable_secs = generator.getVariableName(block.getFieldValue('SECS'));

  // TODO: Assemble python into the code variable.
  const code = `ucuq.sleep(${variable_secs})\n`;
  return code;
}

function init() {
  const workspace = Blockly.getMainWorkspace();

  console.log("WS: ", Code.workspace);

  // Fonction pour gérer l'événement `block_change`
  function onBlockCreate(event) {
    if (event.type === Blockly.Events.BLOCK_CREATE) {
        const blockId = event.blockId;
        const block = workspace.getBlockById(event.blockId);
        if (block) {
          console.log(`Un nouveau bloc a été créé avec l'ID: ${blockId}`);
          console.log(`Type de bloc: ${block.type}`);
        }

        if ( block.type === "gpio_high") {
          const dropdownField = block.getField('NAME');
          console.log(dropdownField);
          /*
          dropdownField.menuGenerator_ = [["a", "b"],["c", "d"]]
          dropdownField.updateDropdown();
          */
        }
    }
  }

  workspace.addChangeListener(onBlockCreate);

  document.getElementById('runButton').addEventListener('click', function() {

    // Générer le code Python  
    var code = Blockly.Python.workspaceToCode(workspace);
    // Afficher le code dans la zone de sortie  

    code = `
import ucuq
# ucuq.setDevice("Blockly", token="Wokwi")

object = {
  "GPIO": {},
  "WS2812": {}
}

` + code + "\nucuq.commit()";
    console.log(code);

    launchCode(code);
  });    

}
