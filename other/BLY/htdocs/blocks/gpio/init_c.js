python.pythonGenerator.forBlock['gpio_init'] = function (block, generator) {
  const text_label = block.getFieldValue('LABEL');
  const value_pin = generator.valueToCode(block, 'PIN', python.Order.ATOMIC);

  const code = `object["GPIO"]["${text_label}"] = ucuq.GPIO(${value_pin})\n`;
  return code;
}


python.pythonGenerator.forBlock['gpio_init_pin'] = function (block) {
  const value_pin = block.getFieldValue('PIN');

  const int_pin = parseInt(value_pin, 10);

  const normalized_pin = isNaN(int_pin) ? `"${value_pin}"` : int_pin;
  
  const code = `${normalized_pin}`;

  return [code, javascript.Order.ATOMIC];
}
