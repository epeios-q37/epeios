python.pythonGenerator.forBlock['ucuq_sleep'] = function (block, generator) {
  const value_seconds = generator.valueToCode(block, 'SECONDS', python.Order.ATOMIC);

  const code = `ucuq.sleep(${value_seconds})\n`;
  return code;
}

python.pythonGenerator.forBlock['ucuq_sleep_seconds'] = function (block) {
  const value_seconds = block.getFieldValue('SECONDS');

  const code = `${value_seconds}`;

  return [code, javascript.Order.ATOMIC];
}
