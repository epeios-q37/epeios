proto = require("./protocol.js")

const location = window.location;
const WS_URL_ = (location.protocol === "http:" ? "ws" : "wss") + "://" + location.hostname + "/ucuq/";

function log(Message) {
  console.log(Message);
}

function exit_(message) {
  throw new Error(message);
}

const PROTOCOL_LABEL = "c37cc83e-079f-448a-9541-5c63ce00d960";
const PROTOCOL_VERSION = "0";

var ws = undefined;
var cont = true

function convertUInt(value)
{
  return proto.convertUInt(value);
}

function convertSInt(value)
{
  return proto.convertSInt(value);
}

function handleString(string)
{
  return proto.handleString(string);
}

function addString(data, string) {
  return proto.addString(data, string);
}

function addStrings(data, strings) {
  return proto.addStrings(data, strings);
}

function protoGetUInt() {
  return proto.getUInt();
}

function protoGetSInt() {
  return proto.getSInt();
}

function protoGetString() {
  return proto.getString();
}

function protoGetStrings() {
  return proto.getStrings();
}

function protoInit() {
  proto.init();
}

function protoGetFeeder(data) {
  return proto.getFeeder(data);
}

function protoHandleData(feeder) {
  if ( proto.handleData(feeder) )
    cont = true;
}

function protoPush(op) {
  return proto.push(op);
}

function protoPushUInt() {
  return proto.pushUInt();  
}

function protoPushSInt() {
  return proto.pushSInt();  
}

function protoPushString() {
  return proto.pushString();  
}

function protoPushStrings() {
  return proto.pushStrings();  
}

function protoPop() {
  cont = true;
  return proto.pop();
}

function protoTop() {
  return proto.top();
}

/************/
/* STEERING */
/************/

const s = {
  STEERING: 301,
  EXECUTE: 302,
  ANSWER: 303,
  RESULT: 304
}

function steering(feeder) {
  while (!feeder.isEmpty() || cont) {
    cont = false;

    // console.log(stack)

    switch (protoTop()) {
      case s.STEERING:
        break;
      case s.EXECUTE:
        protoPop();
        executeCallback(protoGetUInt(), protoGetString())
        break;
      case s.ANSWER:
        protoPop();
        protoPush(s.RESULT);
        protoPushString();
        break;
      case s.RESULT:
        protoPop();
        break;
      default:
        if ( protoTop() >= 0 )
          exit_("Unknown steering operation!");
        else
          protoHandleData(feeder);
        break;
    }
  }
}

/************/
/* IGNITION */
/************/

const i = {
  IGNITION: 201,
  REPORT: 202,
};

function ignition(feeder, callback) {
  while (!feeder.isEmpty() || cont) {
    cont = false;
    switch (protoTop()) {
      case i.IGNITION:
        protoPop();
        protoPush(s.STEERING);
        return false;
        break;
      case i.REPORT:
        if (protoGetString().length) exit_(protoGetString());
        callback();
        protoPop();
        break;
      default:
        if ( protoTop() >= 0 )
          exit_("Unknown ignition operation!");
        else
          protoHandleData(feeder);
        break;
    }
  }

  return true;
}


/**************/
/* HANDSHAKES */
/**************/

const h = {
  HANDSHAKES: 101,
  ERROR: 102,
  NOTIFICATION: 103,
};

function handshakes(feeder, deviceToken, deviceId) {
  while (!feeder.isEmpty() || cont) {
    cont = false;
    switch (protoTop()) {
      case h.HANDSHAKES:
        protoPop();
        protoPush(i.IGNITION);
        protoPush(i.REPORT);
        protoPushString();
        return false;
        break;
      case h.ERROR:
        if (protoGetString().length) exit_(protoGetString());

        protoPop();
        protoPush(h.NOTIFICATION);
        protoPushString();
        break;
      case h.NOTIFICATION:
        if (protoGetString().length) console.log(protoGetString() + "\n");

        ws.send(addString(handleString(deviceToken), deviceId))
        protoPop();
        break;
      default:
        if ( protoTop() >= 0 )
          exit_("Unknown handshake operation!");
        else
          protoHandleData(feeder);
        break;
    }
  }

  return true;
}

/**********/
/* PHASES */
/**********/

const p = {
  HANDSHAKES: 1,
  IGNITION: 2,
  STEERING: 3,
};

var phase = p.HANDSHAKES;

function onRead(data, deviceToken, deviceId, callback) {
  // console.log(">>>>> DATA:", data.length);

  let feeder = protoGetFeeder(data);

  while (!feeder.isEmpty()) {
    switch (phase) {
      case p.HANDSHAKES:
        if (!handshakes(feeder, deviceToken, deviceId)) phase = p.IGNITION;
        break;
      case p.IGNITION:
        if (!ignition(feeder, callback)) phase = p.STEERING;
        break;
      case p.STEERING:
        steering(feeder);
        break;
      default:
        exit_("Unknown phase of value '" + step + "'!");
        break;
    }
  }
}

function blob2Buffer(blob, cb) {
  const reader = new FileReader()

  function onLoadEnd(e) {
    reader.removeEventListener('loadend', onLoadEnd, false)
    if (e.error) cb(e.error)
    else cb(null, Buffer.from(reader.result))
  }

  reader.addEventListener('loadend', onLoadEnd, false)
  reader.readAsArrayBuffer(blob)
}

function launch_(deviceToken, deviceId, libraryVersion, callback) {
  protoInit();

  phase = p.HANDSHAKES;

  log("Connecting to '" + WS_URL_ + "'…");

  if (ws !== undefined) ws.close();

  ws = new WebSocket(WS_URL_);

  ws.onerror = function (err) {
    log("Unable to connect to '" + WS_URL_ + "'!");
  };

  ws.onopen = function () {
    log("Connected to '" + WS_URL_ + "'.");
    protoPush(h.HANDSHAKES);
    protoPush(h.ERROR);
    protoPushString();
    ws.send(
      addString(
       addString(
          addString(handleString(PROTOCOL_LABEL), PROTOCOL_VERSION),
          "Remote"),
        "BRY " + libraryVersion,
      ),
    );
  };
  ws.onclose = function () {
    log("Disconnected!");
  };
  ws.onmessage = function (event) {
    blob2Buffer(event.data, function (err, buffer) {
      onRead(buffer, deviceToken, deviceId, callback);
    });
  };
}

var executeCallback = undefined;

function execute_(script, expression, callback) {
  executeCallback = callback;

  protoPush(s.EXECUTE);
  protoPush(s.ANSWER);
  protoPushUInt();
  
  ws.send(
    addString(
      addString(
        handleString("Execute_1"),
        script),
    expression)
  )
}

  module.exports.launch = launch_;
  module.exports.execute = execute_;
