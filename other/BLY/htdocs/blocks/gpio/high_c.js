python.pythonGenerator.forBlock['gpio_high'] = function (block, generator) {
  const text_label = block.getFieldValue('LABEL');
  const state_pin = generator.valueToCode(block, 'STATE', python.Order.ATOMIC);

  const code = `object["GPIO"]["${text_label}"].high(${state_pin})\n`;
  return code;
}


python.pythonGenerator.forBlock['gpio_high_state'] = function (block) {
  const state_pin = block.getFieldValue('STATE');

  const code = `${state_pin == "TRUE" ? "True" : "False"}`;

  return [code, javascript.Order.ATOMIC];
}