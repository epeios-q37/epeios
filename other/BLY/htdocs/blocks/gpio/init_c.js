python.pythonGenerator.forBlock['gpio_init'] = function (block, generator) {
  const text_label = block.getFieldValue('LABEL');
  const value_pin = generator.valueToCode(block, 'PIN', python.Order.ATOMIC);

  const code = `${string2Id(text_label)} = ucuq.GPIO(${value_pin})\n`;
  return code;
}


python.pythonGenerator.forBlock['gpio_init_pin'] = function (block) {
  const value_pin = block.getFieldValue('PIN');

  const code = `${stringOrInt(value_pin)}`;

  return [code, javascript.Order.ATOMIC];
}
