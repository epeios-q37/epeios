python.pythonGenerator.forBlock['gpio_high'] = function (block, generator) {
  const text_label = block.getFieldValue('LABEL');
  const state_pin = generator.valueToCode(block, 'STATE', python.Order.ATOMIC);

  const code = `${string2Id(text_label)}.high(${state_pin})\n`;
  return code;
}


python.pythonGenerator.forBlock['gpio_high_state'] = function (block) {
  const value_state = block.getFieldValue('STATE');

  const code = `${value_state == "TRUE" ? "True" : "False"}`;

  return [code, javascript.Order.ATOMIC];
}