python.pythonGenerator.forBlock['ws2812_fill'] = function (block, generator) {
  const text_label = block.getFieldValue('LABEL');
  const value_r = generator.valueToCode(block, 'R', python.Order.ATOMIC);
  const value_g = generator.valueToCode(block, 'G', python.Order.ATOMIC);
  const value_b = generator.valueToCode(block, 'B', python.Order.ATOMIC);

  const code = `${string2Id(text_label)}.fill([${value_r},${value_g},${value_b}])\n`;
  return code;
}

python.pythonGenerator.forBlock['ws2812_fill_r'] = function (block) {
  const value_r = block.getFieldValue('R');

  const code = `${value_r}`;

  return [code, javascript.Order.ATOMIC];

}

python.pythonGenerator.forBlock['ws2812_fill_g'] = function (block) {
  const value_g = block.getFieldValue('G');

  const code = `${value_g}`;

  return [code, javascript.Order.ATOMIC];

}

python.pythonGenerator.forBlock['ws2812_fill_b'] = function (block) {
  const value_b = block.getFieldValue('B');

  const code = `${value_b}`;

  return [code, javascript.Order.ATOMIC];

}
