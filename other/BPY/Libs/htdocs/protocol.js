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

class Handler {
  constructor() {
    this.UInt = 0;
    this.SInt = 0;
    this.Length = 0;
    this.Buffer = Buffer.alloc(0);
    this.String = "";
    this.Amount = 0;
    this.Strings = [];
    this.stack = new Array();
    }

  handleUInt(feeder) {
      if (feeder.isEmpty()) return false;
    
      let byte = feeder.get(1)[0];
      this.UInt = (this.UInt << 7) + (byte & 0x7f);
    
      return !(byte & 0x80);
    }
  
  handleContent(feeder) {
    if (this.Length === 0) return true;
    else if (feeder.isEmpty()) return false;
    else this.Buffer = Buffer.concat([this.Buffer, feeder.get(this.Length - this.Buffer.length)]);
  
    return this.Length === this.Buffer.length;
  }
  

  handleData(feeder) {
    switch (this.top()) {
      case d.UINT: // a, loop.
        if (this.handleUInt(feeder))
          this.pop();
        else
          return false;
        break
      case d.SINT:
        this.SInt = this.UInt & 1 ? -((this.UInt >> 1) + 1) : this.UInt >> 1;
        this.pop();
        // console.log("sInt: ", sInt);
        break;
      case d.LENGTH: // c.
        this.Length = this.UInt;
        this.pop();
        this.push(d.CONTENT);
        // console.log("length: ", length);
        break;
      case d.CONTENT: // d, loop.
        if (this.handleContent(feeder))
          this.pop();
        else
          return false;
        break;
      case d.STRING: // e.
        this.String = this.Buffer.toString("utf-8");
        this.pop();
        break;
      case d.AMOUNT:
        this.pop();
        this.Amount = this.UInt;
        this.push(d.STRING);
        break;
      case d.STRINGS:
        this.Strings.push(this.String);
        // console.log("S:", amount, strings);

        if (this.Strings.length < this.Amount)
          this.push(d.STRING);
        else
        this.pop();
        break;
      default:
        if (this.top() < 0)
          exit_("Unknown data operation!");
        else
          exit_("Bad data operation!")
        break;
    }

    return true;
  }

  push(op) {
    this.stack.push(op);

    switch (op) {
      case d.STRINGS:
        this.Strings = [];
        this.push(d.AMOUNT);
        break;
      case d.AMOUNT:
        this.Amount = 0;
        this.push(d.UINT);
        break;
      case d.STRING:
        this.Buffer = Buffer.alloc(0);
        this.push(d.LENGTH);
        break;
      case d.LENGTH:
        this.Length = 0;
        this.push(d.UINT);
        break;
      case d.SINT:
        this.SInt = 0;
        this.push(d.UINT);
      case d.UINT:
        this.UInt = 0;
        break;
    }
  }

  pop() {
    return this.stack.pop();
  }

  top() {
  //  console.log(stack);
    return this.stack[this.stack.length - 1];
  }

  getUInt() {
    return this.UInt;
  }

  getSInt() {
    return this.SInt;
  }

  getString() {
    return this.String;
  }

  getStrings() {
    return this.Strings;
  }

  pushUInt() {
    this.push(d.UINT);
  }

  pushSInt() {
    this.push(d.SINT);
  }

  pushString() {
    this.push(d.STRING);
  }

  pushStrings() {
    this.push(d.STRINGS);
  }
}

function getHandler() {
  return new Handler();
}


module.exports = {
  getFeeder,
  getHandler,
  convertUInt,
  convertSInt,
  addString,
  addStrings,
  handleString,
}
