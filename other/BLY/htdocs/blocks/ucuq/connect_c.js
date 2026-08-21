python.pythonGenerator.forBlock['ucuq_connect'] = function (block, generator) {
  const value_token_id = generator.valueToCode(block, 'TOKEN_ID', python.Order.ATOMIC);

  const code = `\
ucuq.setDevice(tokenId=${value_token_id})

ring = ucuq.ravel.Ring()
lcd = ucuq.ravel.LCD()

`;
  return code;
}

python.pythonGenerator.forBlock['ucuq_connect_token_id'] = function (block) {
  const value_token_id = block.getFieldValue('TOKEN_ID');

  const code = `"${value_token_id}"`;

  return [code, javascript.Order.ATOMIC];
}
