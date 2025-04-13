proto = require("./protocol.js")

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

/************/
/* STEERING */
/************/

const s = {
  STEERING: 301,
  EXECUTE: 302,
  EXECUTE_ANSWER: 303,
  RESULT: 304
}

function steering(handler) {
  while (!handler.feeder.isEmpty() || handler.feeder.cont) {
    handler.feeder.cont = false;

    switch (handler.top()) {
      case s.STEERING:
        break;
      case s.EXECUTE:
        handler.pop(handler.feeder);
        handler.feeder.cont = true;
        handler.callback(handler.getSInt(), handler.getString())
        handler.callback = undefined;
        break;
      case s.EXECUTE_ANSWER:
        handler.pop(handler.feeder);
        handler.feeder.cont = true;
        handler.push(s.RESULT);
        handler.pushString();
        break;
      case s.RESULT:
        handler.pop(handler.feeder);
        handler.feeder.cont = true;
        break;
      default:
        if ( handler.top() >= 0 )
          exit_("Unknown steering operation!");
        else
        if ( handler.handleData(handler.feeder) )
          handler.feeder.cont = true;
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

function ignition(handler) {
  while (!handler.feeder.isEmpty() || handler.feeder.cont) {
    handler.feeder.cont = false;
    switch (handler.top()) {
      case i.IGNITION:
        handler.pop(handler.feeder);
        handler.feeder.cont = true;
        handler.push(s.STEERING);
        return false;
        break;
      case i.REPORT:
        answer = handler.callback(handler.getString());

        if ( answer.length )
          exit_(answer);

        handler.callback = undefined;
        handler.pop(handler.feeder);
        handler.feeder.cont = true;
        break;
      default:
        if ( handler.top() >= 0 )
          exit_("Unknown ignition operation!");
        else
        if ( handler.handleData(handler.feeder) )
          handler.feeder.cont = true;
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

function handshakes(handler, deviceToken, deviceId) {
  while (!handler.feeder.isEmpty() || handler.feeder.cont) {
    handler.feeder.cont = false;
    switch (handler.top()) {
      case h.HANDSHAKES:
        handler.pop(handler.feeder);
        handler.feeder.cont = true;
        handler.push(i.IGNITION);
        handler.push(i.REPORT);
        handler.pushString();
        return false;
        break;
      case h.ERROR:
        if (handler.getString().length) exit_(handler.getString());

        handler.pop(handler.feeder);
        handler.feeder.cont = true;
        handler.push(h.NOTIFICATION);
        handler.pushString();
        break;
      case h.NOTIFICATION:
        if (handler.getString().length) console.log(handler.getString() + "\n");

        handler.ws.send(proto.addString(proto.handleString(deviceToken), deviceId))
        handler.pop(handler.feeder);
        handler.feeder.cont = true;
        break;
      default:
        if ( handler.top() >= 0 )
          exit_("UCUQ Unknown handshake operation!" + handler.top());
        else
        if ( handler.handleData(handler.feeder) )
          handler.feeder.cont = true;
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

function onRead(handler, data, deviceToken, deviceId) {
  handler.feeder = proto.getFeeder(data);
  handler.feeder.cont = true;

  while (!handler.feeder.isEmpty()) {
    switch (handler.phase) {
      case p.HANDSHAKES:
        if (!handshakes(handler, deviceToken, deviceId))
          handler.phase = p.IGNITION;
        break;
      case p.IGNITION:
        if (!ignition(handler))
          handler.phase = p.STEERING;
        break;
      case p.STEERING:
        steering(handler);
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

function launch(deviceToken, deviceId, libraryVersion, callback) {
  let handler = proto.getHandler();

  handler.callback = callback;
  handler.phase = p.HANDSHAKES;
  handler.funcStack = [];

  log("Connecting to '" + WS_URL_ + "'…");

  handler.ws = new WebSocket(WS_URL_);

  handler.ws.onerror = function (err) {
    log("Unable to connect to '" + WS_URL_ + "'!");
  };

  handler.ws.onopen = function () {
    log("Connected to '" + WS_URL_ + "'.");
    handler.push(h.HANDSHAKES);
    handler.push(h.ERROR);
    handler.pushString();
    handler.ws.send(
      proto.addString(
        proto.addString(
          proto.addString(proto.handleString(PROTOCOL_LABEL), PROTOCOL_VERSION),
          "Remote"),
        "BRY " + libraryVersion,
      ),
    );
  };
  handler.ws.onclose = function () {
    log("Disconnected!");
  };
  handler.ws.onmessage = function (event) {
    blob2Buffer(event.data, function (err, buffer) {
      onRead(handler, buffer, deviceToken, deviceId);
    });
  };

  return handler;
}

function subOperate_(handler) {
  if ( handler.callback !== undefined ) {
    if ( handler.funcStack.length )
      setTimeout(() => subOperate_(handler));
  } else if ( handler.funcStack.length ) {
    let item = handler.funcStack.shift();
    handler.callback = item[2];
    item[0](handler, ...item[1]);
    subOperate_(handler);
  }
}

function operate_(handler, func, args, callback) {
  handler.funcStack.push([func, args, callback]);

  if ( handler.funcStack.length === 1 )
    subOperate_(handler);
}

function subUpload_(handler, modules) {
  handler.ws.send(
    proto.addStrings(
      proto.handleString("Upload_1"),
      modules
    )
  )
}

function upload(handler, modules, callback) {
  operate_(handler, subUpload_, [modules], undefined);
}


function subExecute_(handler, script, expression) {
  if ( expression !== "" ) {
    handler.push(s.EXECUTE);
    handler.push(s.EXECUTE_ANSWER);
    handler.pushSInt();
  }
    
  handler.ws.send(
    proto.addString(
      proto.addString(
        proto.handleString("Execute_1"),
        script),
    expression)
  );
}

function execute(handler, script, expression, callback) {
  operate_(handler, subExecute_, [script, expression], expression !== "" ? callback : undefined);
}

// Workaround to the brython 'unicodedata.normalize()' bug.
function toASCII(text) {
  return text.normalize('NFD').replace(/[\u0300-\u036f]/g, '');
}

// ATTENTION: si modification, mettre script 'Build' à jour !!!
module.exports = {
launch,
upload,
execute,
toASCII,
}
