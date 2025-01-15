python.pythonGenerator.forBlock['lcd_putString'] = function (block, generator) {
  const text_label = block.getFieldValue('LABEL');
  const value_string = generator.valueToCode(block, 'STRING', python.Order.ATOMIC);

  const code = `${string2Id(text_label)}.putString(${value_string})\n`;

  return code;
}

python.pythonGenerator.forBlock['lcd_putString_string'] = function (block) {
  const value_string = block.getFieldValue('STRING');

  const code = `"${value_string.replace('"','\\"')}"`;

  return [code, javascript.Order.ATOMIC];

}
