python.pythonGenerator.forBlock['ws2812_write'] = function (block, generator) {
  const text_label = block.getFieldValue('LABEL');

  code = `${string2Id(text_label)}.write()\n`
  return code;
}  
