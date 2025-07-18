python.pythonGenerator.forBlock['ws2812_init'] = function (block, generator) {
  const text_label = block.getFieldValue('LABEL');
  const value_pin = generator.valueToCode(block, 'PIN', python.Order.ATOMIC);
  const value_count = generator.valueToCode(block, 'COUNT', python.Order.ATOMIC);

  // TODO: Assemble python into the code variable.
  code = `${string2Id(text_label)} = ucuq.WS2812(${value_count},${value_pin})\n`
  return code;
}  

python.pythonGenerator.forBlock['ws2812_init_pin'] = function (block) {
  const value_pin = block.getFieldValue('PIN');

  const code = `${stringOrInt(value_pin)}`;

  return [code, javascript.Order.ATOMIC];
}

python.pythonGenerator.forBlock['ws2812_init_count'] = function (block) {
  const value_count = block.getFieldValue('COUNT');

  const code = `${value_count}`;

  return [code, javascript.Order.ATOMIC];
}
