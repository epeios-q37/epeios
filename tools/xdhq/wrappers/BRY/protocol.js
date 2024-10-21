var protoUInt = 0;
var protoSInt = 0;
var protoLength = 0;
var protoBuffer = Buffer.alloc(0);
var protoString = "";
var protoAmount = 0;
var protoStrings = [];
var stack = new Array();

class Feeder {
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

function exit_(message) {
  throw new Error(message);
}

function getFeeder(data) {
  return new Feeder(data);
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

function handleUInt(feeder) {
  if (feeder.isEmpty()) return false;

  let byte = feeder.get(1)[0];
  protoUInt = (protoUInt << 7) + (byte & 0x7f);

  return !(byte & 0x80);
}

function handleContent(feeder) {
  if (protoLength === 0) return true;
  else if (feeder.isEmpty()) return false;
  else protoBuffer = Buffer.concat([protoBuffer, feeder.get(protoLength - protoBuffer.length)]);

  return protoLength === protoBuffer.length;
}

function handleData(feeder) {
  switch (top()) {
    case d.UINT: // a, loop.
      if (handleUInt(feeder))
        pop();
      else
        return false;
      break
    case d.SINT:
      protoSInt = protoUInt & 1 ? -((protoUInt >> 1) + 1) : protoUInt >> 1;
      pop();
      // console.log("sInt: ", sInt);
      break;
    case d.LENGTH: // c.
      protoLength = protoUInt;
      pop();
      push(d.CONTENT);
      // console.log("length: ", length);
      break;
    case d.CONTENT: // d, loop.
      if (handleContent(feeder))
        pop();
      else
        return false;
      break;
    case d.STRING: // e.
      protoString = protoBuffer.toString("utf-8");
      pop();
      break;
    case d.AMOUNT:
      pop();
      protoAmount = protoUInt;
      push(d.STRING);
      break;
    case d.STRINGS:
      protoStrings.push(protoString);
      // console.log("S:", amount, strings);

      if (protoStrings.length < protoAmount)
        push(d.STRING);
      else
        pop();
      break;
    default:
      if (top() < 0)
        exit_("Unknown data operation!");
      else
        exit_("Bad data operation!")
      break;
  }

  return true;
}

function push(op) {
  stack.push(op);

  switch (op) {
    case d.STRINGS:
      protoStrings = [];
      push(d.AMOUNT);
      break;
    case d.AMOUNT:
      protoAmount = 0;
      push(d.UINT);
      break;
    case d.STRING:
      protoBuffer = Buffer.alloc(0);
      push(d.LENGTH);
      break;
    case d.LENGTH:
      protoLength = 0;
      push(d.UINT);
      break;
    case d.SINT:
      protoSInt = 0;
      push(d.UINT);
    case d.UINT:
      protoUInt = 0;
      break;
  }
}

function pop() {
  return stack.pop();
}

function top() {
//  console.log(stack);
  return stack[stack.length - 1];
}

function getUInt() {
  return protoUInt;
}

function getSInt() {
  return protoSInt;
}

function getString() {
  return protoString;
}

function getStrings() {
  return protoStrings;
}

function pushUInt() {
  push(d.DINT);
}

function pushSInt() {
  push(d.SINT);
}

function pushString() {
  push(d.STRING);
}

function pushStrings() {
  push(d.STRINGS);
}


module.exports = {
  getFeeder,
  handleData,
  push,
  pop,
  top,
  pushUInt,
  getUInt,
  pushSInt,
  getSInt,
  pushString,
  getString,
  pushStrings,
  getStrings,
  convertUInt,
  convertSInt,
  addString,
  addStrings,
  handleString,
  init,
}
