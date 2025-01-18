python.pythonGenerator.forBlock['hd44780_moveTo'] = function (block, generator) {
  const text_label = block.getFieldValue('LABEL');
  const value_x = generator.valueToCode(block, 'X', python.Order.ATOMIC);
  const value_y = generator.valueToCode(block, 'Y', python.Order.ATOMIC);

  const code = `${string2Id(text_label)}.moveTo(${value_x},${value_y})\n`;

  return code;
}

python.pythonGenerator.forBlock['hd44780_moveTo_x'] = function (block) {
  const value_x = block.getFieldValue('X');

  const code = `${value_x}`;

  return [code, javascript.Order.ATOMIC];
}

python.pythonGenerator.forBlock['hd44780_moveTo_y'] = function (block) {
  const value_y = block.getFieldValue('Y');

  const code = `${value_y}`;

  return [code, javascript.Order.ATOMIC];
}
