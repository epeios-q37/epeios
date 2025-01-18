python.pythonGenerator.forBlock['hd44780_clear'] = function (block, generator) {
  const text_label = block.getFieldValue('LABEL');

  const code = `${string2Id(text_label)}.clear()\n`;

  return code;
}
