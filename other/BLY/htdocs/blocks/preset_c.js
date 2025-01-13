python.pythonGenerator.forBlock['preset'] = function (block, generator) {
  const value_id = generator.valueToCode(block, 'ID', python.Order.ATOMIC);
  const value_token = generator.valueToCode(block, 'TOKEN', python.Order.ATOMIC);

  const code = `ucuq.setDevice(${value_id},token = ${value_token})\n`;
  return code;
}


python.pythonGenerator.forBlock['preset_id'] = function (block) {
  const value_id = block.getFieldValue('ID');

  const code = `"${value_id}"`;

  return [code, javascript.Order.ATOMIC];
}

python.pythonGenerator.forBlock['preset_token'] = function (block) {
  const value_id = block.getFieldValue('TOKEN');

  const code = `"${value_id}"`;

  return [code, javascript.Order.ATOMIC];
}