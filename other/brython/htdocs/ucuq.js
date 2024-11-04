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

/************/
/* STEERING */
/************/

const s = {
  STEERING: 301,
  UPLOAD: 302,
  UPLOAD_ANSWER: 303,
  EXECUTE: 304,
  EXECUTE_ANSWER: 305,
  RESULT: 306
}

function steering(handler, feeder) {
  console.log("Steering", feeder)
  while (!feeder.isEmpty() || feeder.cont) {
    feeder.cont = false;

    // console.log(stack)

    switch (handler.top()) {
      case s.STEERING:
        break;
      case s.UPLOAD:
        handler.pop(feeder);
        feeder.cont = true;
        handler.uploadCallback(handler.getSInt(), handler.getString())  // result of 'handler.getString()' doesn't matter ir result of 'handler.getSInt()' is == 0.
        break;
      case s.EXECUTE:
        handler.pop(feeder);
        feeder.cont = true;
        executeCallback(handler.getSInt(), handler.getString())
        break;
      case s.UPLOAD_ANSWER:
        handler.pop(feeder);
        feeder.cont = true;
        if ( handler.getSInt() != 0 ) {
          handler.push(s.RESULT);
          handler.pushString();
        }
      case s.EXECUTE_ANSWER:
        handler.pop(feeder);
        feeder.cont = true;
        handler.push(s.RESULT);
        handler.pushString();
        break;
      case s.RESULT:
        handler.pop(feeder);
        feeder.cont = true;
        break;
      default:
        if ( handler.top() >= 0 )
          exit_("Unknown steering operation!");
        else
        if ( handler.handleData(feeder) )
          feeder.cont = true;
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

function ignition(handler, feeder) {
  console.log("Ignition", feeder)
  while (!feeder.isEmpty() || feeder.cont) {
    feeder.cont = false;
    switch (handler.top()) {
      case i.IGNITION:
        handler.pop(feeder);
        feeder.cont = true;
        handler.push(s.STEERING);
        return false;
        break;
      case i.REPORT:
        if (handler.getString().length) exit_(handler.getString());
        handler.pop(feeder);
        feeder.cont = true;
        break;
      default:
        if ( handler.top() >= 0 )
          exit_("Unknown ignition operation!");
        else
        if ( handler.handleData(feeder) )
          feeder.cont = true;
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

function handshakes(handler, feeder, deviceToken, deviceId) {
  while (!feeder.isEmpty() || feeder.cont) {
    console.log("Handshake", feeder)
    feeder.cont = false;
    switch (handler.top()) {
      case h.HANDSHAKES:
        handler.pop(feeder);
        feeder.cont = true;
        handler.push(i.IGNITION);
        handler.push(i.REPORT);
        handler.pushString();
        log("1");
        return false;
        break;
      case h.ERROR:
        log("2");
        if (handler.getString().length) exit_(handler.getString());

        handler.pop(feeder);
        feeder.cont = true;
        handler.push(h.NOTIFICATION);
        handler.pushString();
        break;
      case h.NOTIFICATION:
        log("3");
        if (handler.getString().length) console.log(handler.getString() + "\n");

        handler.ws.send(proto.addString(proto.handleString(deviceToken), deviceId))
        handler.pop(feeder);
        feeder.cont = true;
        break;
      default:
        log("4");
        if ( handler.top() >= 0 )
          exit_("UCUQ Unknown handshake operation!" + handler.top());
        else
        if ( handler.handleData(feeder) )
          feeder.cont = true;
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

function onRead(handler, data, deviceToken, deviceId) {
  console.log(">>>>> DATA:", data.length);

  let feeder = proto.getFeeder(data);
  feeder.cont = true;

  while (!feeder.isEmpty()) {
    switch (phase) {
      case p.HANDSHAKES:
        if (!handshakes(handler, feeder, deviceToken, deviceId)) phase = p.IGNITION;
        console.log("Token: '" + deviceToken + "', Id: '" + deviceId +"'", feeder);
        break;
      case p.IGNITION:
        if (!ignition(handler, feeder)) {
          phase = p.STEERING;
          handler.ignited = true;

        //  if (launchCallback)
            launchCallback();
        }
        break;
      case p.STEERING:
        steering(handler, feeder);
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

launchCallback = undefined

function launch_(deviceToken, deviceId, libraryVersion, callback) {
  launchCallback = callback;

  handler = proto.getHandler();

  phase = p.HANDSHAKES;

  log("Connecting to '" + WS_URL_ + "'…");

  handler.ws = new WebSocket(WS_URL_);

  handler.ignited = false;

  console.log(handler)

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

function subUpload_(handler, modules) {
  if ( !handler.ignited )
    setTimeout(() => subUpload_(handler, modules));
  else {
    handler.push(s.UPLOAD)
    handler.push(s.EXECUTE_ANSWER);
    handler.pushSInt();

    handler.ws.send(
      proto.addStrings(
        proto.handleString("Upload_1"),
        modules
      )
    )
  }
}

function upload_(handler, modules, callback) {
  handler.uploadCallback = callback;

  subUpload_(handler, modules);
}


function subExecute_(handler, script, expression) {
  if ( !handler.ignited )
    setTimeout(() => subExecute_(handler, script, expression));
  else {
    handler.push(s.EXECUTE);
    handler.push(s.EXECUTE_ANSWER);
    handler.pushSInt();
    
    handler.ws.send(
      proto.addString(
        proto.addString(
          proto.handleString("Execute_1"),
          script),
      expression)
    );
  }
}

var executeCallback = undefined;

function execute_(handler, script, expression, callback) {
  executeCallback = callback;

  subExecute_(handler, script, expression);

//  setTimeout(() => subExecute_(script, expression), 2000);
}


function timeout_(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function sleep_(time, fn, ...args) {
  await timeout_(time);
  return fn(...args);
}

module.exports.sleep = sleep_;
module.exports.launch = launch_;
module.exports.upload = upload_;
module.exports.execute = execute_;
