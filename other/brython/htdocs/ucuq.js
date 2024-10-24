proto = require("./protocol.js")

var handler = undefined;

const location = window.location;
const WS_URL_ = (location.protocol === "http:" ? "ws" : "wss") + "://" + location.hostname + "/ucuq/";

function log(Message) {
  console.log(Message);
}

function exit_(message) {
  alert(message);
  throw new Error(message);
}

const PROTOCOL_LABEL = "c37cc83e-079f-448a-9541-5c63ce00d960";
const PROTOCOL_VERSION = "0";

var wsUCUq = undefined;
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
  return handler.getUInt();
}

function protoGetSInt() {
  return handler.getSInt();
}

function protoGetString() {
  return handler.getString();
}

function protoGetStrings() {
  return handler.getStrings();
}

function protoHandleData(feeder) {
  if ( handler.handleData(feeder) )
    cont = true;
}

function protoPush(op) {
  return handler.push(op);
}

function protoPushUInt() {
  return handler.pushUInt();  
}

function protoPushSInt() {
  return handler.pushSInt();  
}

function protoPushString() {
  return handler.pushString();  
}

function protoPushStrings() {
  return handler.pushStrings();  
}

function protoPop() {
  cont = true;
  return handler.pop();
}

function protoTop() {
  return handler.top();
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
        executeCallback(protoGetSInt(), protoGetString())
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

function ignition(feeder) {
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

        wsUCUq.send(addString(handleString(deviceToken), deviceId))
        protoPop();
        break;
      default:
        if ( protoTop() >= 0 )
          exit_("UCUQ Unknown handshake operation!" + protoTop());
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

function onRead(data, deviceToken, deviceId) {
  // console.log(">>>>> DATA:", data.length);

  let feeder = proto.getFeeder(data);

  while (!feeder.isEmpty()) {
    switch (phase) {
      case p.HANDSHAKES:
        if (!handshakes(feeder, deviceToken, deviceId)) phase = p.IGNITION;
        break;
      case p.IGNITION:
        if (!ignition(feeder)) {
          phase = p.STEERING;
          wsUCUq.ignited = true;
        }
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

function launch_(deviceToken, deviceId, libraryVersion) {
  handler = proto.getHandler();

  phase = p.HANDSHAKES;

  log("Connecting to '" + WS_URL_ + "'…");

  if (wsUCUq !== undefined) wsUCUq.close();

  wsUCUq = new WebSocket(WS_URL_);

  wsUCUq.ignited = false;

  wsUCUq.onerror = function (err) {
    log("Unable to connect to '" + WS_URL_ + "'!");
  };

  wsUCUq.onopen = function () {
    log("Connected to '" + WS_URL_ + "'.");
    protoPush(h.HANDSHAKES);
    protoPush(h.ERROR);
    protoPushString();
    wsUCUq.send(
      addString(
       addString(
          addString(handleString(PROTOCOL_LABEL), PROTOCOL_VERSION),
          "Remote"),
        "BRY " + libraryVersion,
      ),
    );
  };
  wsUCUq.onclose = function () {
    log("Disconnected!");
  };
  wsUCUq.onmessage = function (event) {
    blob2Buffer(event.data, function (err, buffer) {
      onRead(buffer, deviceToken, deviceId);
    });
  };
}

var executeCallback = undefined;

function subExecute(script, expression) {
  if ( !wsUCUq.ignited )
    setTimeout(() => subExecute(script, expression));
  else {
    protoPush(s.EXECUTE);
    protoPush(s.ANSWER);
    protoPushSInt();
    
    wsUCUq.send(
      addString(
        addString(
          handleString("Execute_1"),
          script),
      expression)
    );
  }
}

function execute_(script, expression, callback) {
  executeCallback = callback;

  subExecute(script, expression);
}

module.exports.launch = launch_;
module.exports.execute = execute_;
