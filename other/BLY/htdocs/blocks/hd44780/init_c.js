python.pythonGenerator.forBlock['hd44780_init'] = function (block, generator) {
  const text_label = block.getFieldValue('LABEL');
  const value_soft = generator.valueToCode(block, 'SOFT', python.Order.ATOMIC);
  const value_sda = generator.valueToCode(block, 'SDA', python.Order.ATOMIC);
  const value_scl = generator.valueToCode(block, 'SCL', python.Order.ATOMIC);
  const value_cols = generator.valueToCode(block, 'COLS', python.Order.ATOMIC);
  const value_rows = generator.valueToCode(block, 'ROWS', python.Order.ATOMIC);

  const code = `${string2Id(text_label)} = ucuq.HD44780_I2C(ucuq.I2C(${value_sda},${value_scl},soft=${value_soft == "TRUE" ? "True" : "False"}),${value_rows},${value_cols})\n`;

  return code;
}

python.pythonGenerator.forBlock['hd44780_init_soft'] = function (block) {
  const value_soft = block.getFieldValue('SOFT');

  const code = `${value_soft == "TRUE" ? "True" : "False"}`;

  return [code, javascript.Order.ATOMIC];
}

python.pythonGenerator.forBlock['hd44780_init_sda'] = function (block) {
  const value_sda = block.getFieldValue('SDA');

  const code = `${value_sda}`;

  return [code, javascript.Order.ATOMIC];
}

python.pythonGenerator.forBlock['hd44780_init_scl'] = function (block) {
  const value_scl = block.getFieldValue('SCL');

  const code = `${value_scl}`;

  return [code, javascript.Order.ATOMIC];
}

python.pythonGenerator.forBlock['hd44780_init_cols'] = function (block) {
  const value_cols = block.getFieldValue('COLS');

  const code = `${value_cols}`;

  return [code, javascript.Order.ATOMIC];
}

python.pythonGenerator.forBlock['hd44780_init_rows'] = function (block) {
  const value_rows = block.getFieldValue('ROWS');

  const code = `${value_rows}`;

  return [code, javascript.Order.ATOMIC];
}
