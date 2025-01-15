python.pythonGenerator.forBlock['ws2812_setValue'] = function (block, generator) {
  const text_label = block.getFieldValue('LABEL');
  const value_index = generator.valueToCode(block, 'INDEX', python.Order.ATOMIC);
  const value_r = generator.valueToCode(block, 'R', python.Order.ATOMIC);
  const value_g = generator.valueToCode(block, 'G', python.Order.ATOMIC);
  const value_b = generator.valueToCode(block, 'B', python.Order.ATOMIC);

  const code = `${string2Id(text_label)}.setValue(${value_index},[${value_r},${value_g},${value_b}])\n`;
  return code;
}

python.pythonGenerator.forBlock['ws2812_setValue_index'] = function (block) {
  const value_index = block.getFieldValue('INDEX');

  const code = `${value_index}`;

  return [code, javascript.Order.ATOMIC];
}

python.pythonGenerator.forBlock['ws2812_setValue_r'] = function (block) {
  const value_r = block.getFieldValue('R');

  const code = `${value_r}`;

  return [code, javascript.Order.ATOMIC];
}

python.pythonGenerator.forBlock['ws2812_setValue_g'] = function (block) {
  const value_g = block.getFieldValue('G');

  const code = `${value_g}`;

  return [code, javascript.Order.ATOMIC];
}

python.pythonGenerator.forBlock['ws2812_setValue_b'] = function (block) {
  const value_b = block.getFieldValue('B');

  const code = `${value_b}`;

  return [code, javascript.Order.ATOMIC];
}
