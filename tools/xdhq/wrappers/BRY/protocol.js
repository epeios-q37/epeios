var Feeder = class Feeder {
  constructor(data) {
    this.data_ = data;
  }
  isEmpty() {
    return this.data_.length === 0;
  }
  get(size) {
    if (this.data_.length === 0) exit_("No data available!");

    if (size > this.data_.length) size = this.data_.length;

    if (size === 0) exit_("'size' can not be 0!");

    let data = this.data_.subarray(0, size);

    this.data_ = this.data_.subarray(size);

    return data;
  }
}

function byteLength(str) {
  // returns the byte length of an utf8 string
  let s = str.length;
  for (let i = str.length - 1; i >= 0; i--) {
    let code = str.charCodeAt(i);
    if (code > 0x7f && code <= 0x7ff) s++;
    else if (code > 0x7ff && code <= 0xffff) s += 2;
    if (code >= 0xdc00 && code <= 0xdfff) i--; //trail surrogate
  }
  return s;
}

function convertUInt(value) {
  let result = Buffer.alloc(1, value & 0x7f);
  value >>= 7;

  while (value !== 0) {
    result = Buffer.concat([Buffer.alloc(1, (value & 0x7f) | 0x80), result]);
    value >>= 7;
  }

  return result;
}

function sizeEmbeddedString(string) {
  return Buffer.concat([
    convertUInt(byteLength(string)),
    Buffer.from(string, "utf8"),
  ]);
}

function addString(data, string) {
  return Buffer.concat([data, sizeEmbeddedString(string)]);
}

function convertSInt(value) {
  return convertUInt(value < 0 ? ((-value - 1) << 1) | 1 : value << 1);
}

function addStrings(data, strings) {
  let i = 0;
  data = Buffer.concat([data, convertUInt(strings.length)]);

  while (i < strings.length) data = addString(data, strings[i++]);

  return data;
}

function handleString(string) {
  let data = Buffer.alloc(0);

  data = addString(data, string);

  return data;
}

var stack = new Array();

function init() {
  stack = new Array();
}

const d = {
  UINT: -1,
  SINT: -2,
  LENGTH: -3,
  CONTENT: -4,
  STRING: -5,
  AMOUNT: -6,
  SUBSTRING: -7,
  STRINGS: -8,
};

function push(op) {
  stack.push(op);

  switch (op) {
    case d.STRINGS:
      strings = [];
      push(d.AMOUNT);
      break;
    case d.AMOUNT:
      amount_ = 0;
      push(d.UINT);
      break;
    case d.STRING:
      buffer = Buffer.alloc(0);
      push(d.LENGTH);
      break;
    case d.LENGTH:
      length = 0;
      push(d.UINT);
      break;
    case d.SINT:
      sInt = 0;
      push(d.UINT);
    case d.UINT:
      uInt = 0;
      break;
  }
}


function pop() {
  cont = true;
  return stack.pop();
}

function top() {
  return stack[stack.length - 1];
}

module.exports = {
  Feeder,
  byteLength,
  convertUInt,
  sizeEmbeddedString,
  convertSInt,
  addString,
  addStrings,
  handleString,
  d,
  push,
  init,
  top_: top,
  pop,
}
