python.pythonGenerator.forBlock['gpio_low'] = function (block, generator) {
  const text_label = block.getFieldValue('LABEL');

  const code = `object["GPIO"]["${text_label}"].low()\n`;
  return code;
}
