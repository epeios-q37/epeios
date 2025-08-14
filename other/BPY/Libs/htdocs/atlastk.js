proto = require("./protocol.js")

handler = undefined;

const location = window.location;
const WS_URL_ = (location.protocol === "http:" ? "ws" : "wss") + "://" + location.hostname + "/faas/";

function log(Message) {
  console.log(Message);
}

function exit_(message) {
  throw new Error(message);
}

const MAIN_PROTOCOL_LABEL = "22bb5d73-924f-473f-a68a-14f41d8bfa83";
const MAIN_PROTOCOL_VERSION = "0";

const FAAS_PROTOCOL_LABEL = "4c837d30-2eb5-41af-9b3d-6c8bf01d8dbf";
const FAAS_PROTOCOL_VERSION = "1";
const SCRIPT_VERSION = "0";

var ws = undefined;
var instances = {};
var app_url_ = undefined;

const types = {
  VOID: 0,
  STRING: 1,
  STRINGS: 2,
  UNDEFINED: 3, // Always the highest value.
};

function getEnv() {
  return "";
}

var token = getEnv("ATK_TOKEN");

if (token !== "") token = "&" + token;

function isTokenEmpty() {
  return token === "" || token.charAt(0) === "&";
}

// var protoStack = {}
var id_ = ""; // Buffers the action related id.
var cont = true;

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


/*********/
/* SERVE */
/*********/

var instance_ = undefined;

const s = {
  SERVE: 401,
  COMMAND: 402,
  CREATION: 403,
  CLOSING: 404,
  ERROR: 405,
  LANGUAGE: 406,
  LAUNCH: 407,
  ID: 408,
  ACTION: 409,
  RESPONSE: 410,
};

// Special ids.
const commandIds = {
  FORBIDDEN: -1,
  CREATION: -2,
  CLOSING: -3,
  HEAD: -4,
};

const responseIds = {
  BROADCAST: -3,
  HEAD: -4,
};

function handleCommand(command, head) {
  let IsCommand = true;

  // console.log(command);

  switch (command) {
    case commandIds.FORBIDDEN:
      exit_("Received unexpected undefined command id!");
      break;
    case commandIds.CREATION:
      protoPush(s.CREATION);
      protoPushSInt();
      break;
    case commandIds.CLOSING:
      protoPush(s.CLOSING);
      protoPushSInt();
      break;
    case commandIds.HEAD:
      ws.send(addString(convertSInt(responseIds.HEAD), head));
      break;
    default:
      if (command < 0) exit_("Unknown command of id '" + command + "'!");
      else IsCommand = false;
      break;
  }

  return IsCommand;
}

function fillXDH(xdh, id) {
  xdh.id = id;
  xdh.isFAAS = true;
  xdh.type = types.UNDEFINED;
  xdh.language = undefined;
  xdh.queued = [];
}

function report_(message) {
  ws.send(addString(addString(convertSInt(-1), "#Inform_1"), message));
}

function dismiss_(id) {
  ws.send(addString(convertSInt(id), "#Dismiss_1"));
}

function handleCreation(id, createCallback) {
  if (id in instances)
    report_("Instance of id  '" + id + "' exists but should not !");

  let instance = createCallback();

  instance._xdh = new Object();

  fillXDH(instance._xdh, id);

  instances[id] = instance;
}

function handleClosing(id) {
  if (!(id in instances))
    report_("Instance of id '" + id + "' not available for destruction!");

  delete instances[id];
}

function standBy(instance) {
  ws.send(addString(convertSInt(instance._xdh.id), "#StandBy_1"));
  instance._xdh.inProgress = false;
  //	console.log("Standby!!!");
}

const receiveCallbacksQueue = [],
  receiveDataQueue = [];

function handleLaunch(instance, id, action) {
  if (instance === undefined) exit_("No instance set!");

  instance._xdh.inProgress = true;

  bundle = { instance: instance, id: id, action: action };

  if (receiveCallbacksQueue.length !== 0) {
    // Somebody is waiting to receive this message.
    receiveCallbacksQueue.shift().resolve(bundle);
    return;
  }

  // Enqueue.
  receiveDataQueue.push(bundle);
}

function getCallbackBundle() {
  if (receiveDataQueue.length !== 0) {
    // We have a message ready.
    bundle = receiveDataQueue.shift();

    return Promise.resolve(bundle);
  }

  // Wait for the next incoming message and receive it.
  const receivePromise = new Promise((resolve, reject) => {
    receiveCallbacksQueue.push({ resolve, reject });
  });

  return receivePromise;
}

function setResponse(type) {
  protoPush(s.RESPONSE);

  switch (type) {
    case types.STRING:
      protoPushString();
      break;
    case types.STRINGS:
      protoPushStrings();
      break;
    default:
      exit_("Bad response type!");
      break;
  }
}

function serve(feeder, createCallback, head) {
  while (!feeder.isEmpty() || cont) {
    cont = false;

    // console.log(stack)

    switch (protoTop()) {
      case s.SERVE:
        protoPush(s.COMMAND);
        protoPushSInt();
        break;
      case s.COMMAND:
        protoPop();
        if (!handleCommand(protoGetSInt(), head)) {
          // Makes the required 'push(…)'.
          let id = protoGetSInt();

          if (!(id in instances)) {
            report_("Unknown instance of id '" + id + "'!");
            dismiss_(id);
          } else {
            instance_ = instances[id];

            if (instance_._xdh.language === undefined) {
              protoPush(s.LANGUAGE);
              protoPushString();
            } else if (instance_._xdh.queued.length === 0) {
              protoPush(s.LAUNCH);
              protoPush(s.ID);
              protoPushString();
            } else {
              setResponse(instance_._xdh.queued[0].type);
            }
          }
        }
        break;
      case s.CREATION:
        protoPop();
        handleCreation(protoGetSInt(), createCallback);
        break;
      case s.CLOSING:
        protoPop();
        handleClosing(protoGetSInt());
        break;
      case s.ERROR:
        if (protoGetString() !== "") exit_(protoGetString());

        protoPop();
        protoPush(s.LANGUAGE);
        protoPushString();
        break;
      case s.LANGUAGE:
        instance_._xdh.language = protoGetString();
        protoPop();
        break;
      case s.LAUNCH:
        protoPop();
        // console.log(">>>>> Action:", getString, id);
        handleLaunch(instance_, id_, protoGetString());
        break;
      case s.ID:
        protoPop();
        id_ = protoGetString();
        protoPush(s.ACTION);
        protoPushString();
        break;
      case s.ACTION:
        protoPop();
        cont = true;
        break;
      case s.RESPONSE:
        protoPop();

        let pending = instance_._xdh.queued.shift();
        let type = pending.type;
        let callback = pending.callback;

        if (callback !== undefined) {
          switch (type) {
            case types.UNDEFINED:
              exit_("Undefined type not allowed here!");
              break;
            case types.VOID:
              callback();
              break;
            case types.STRING:
              callback(protoGetString());
              break;
            case types.STRINGS:
              callback(protoGetStrings());
              break;
            default:
              exit_("Unknown type of value '" + type + "'!");
              break;
          }
        } else {
          standBy(instance_);
          // console.log();
        }
        break;
      default:
        if ( protoTop() >= 0 )
          exit_("Unknown serve operation!");
        else
          protoHandleData(feeder);
        break;
    }
  }
  // console.log();
}

/************/
/* IGNITION */
/************/

const i = {
  IGNITION: 201,
  TOKEN: 202,
  ERROR: 203,
  URL: 204,
};

function handleURL(url) {
  app_url_ = url;
  console.log(url + "\n");
  console.log(new Array(url.length + 1).join("^") + "\n");
  console.log(
    "Open above URL in a web browser (click, right click or copy/paste). Enjoy!\n",
  );

  launchApp(url);
}

function ignition(feeder) {
  while (!feeder.isEmpty() || cont) {
    cont = false;
    switch (protoTop()) {
      case i.IGNITION:
        protoPop();
        protoPush(s.SERVE);
        return false;
        break;
      case i.TOKEN:
        token = protoGetString();
        protoPop();

        if (isTokenEmpty()) protoPush(i.ERROR);
        else protoPush(i.URL);

        protoPushString();
        break;
      case i.ERROR:
        exit_(protoGetString());
        break;
      case i.URL:
        protoPop();
        handleURL(protoGetString());
        break;
      default:
        if ( protoTop >= 0 )
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
  ERROR_FAAS: 102,
  NOTIFICATION_FAAS: 103,
  ERROR_MAIN: 104,
  NOTIFICATION_MAIN: 105,
};

function handshakes(feeder) {
  while (!feeder.isEmpty() || cont) {
    cont = false;
    switch (protoTop()) {
      case h.HANDSHAKES:
        protoPop();
        ws.send(addString(addString(handleString(token), "faas.q37.info"), ""));
        protoPush(i.IGNITION);
        protoPush(i.TOKEN);
        protoPushString();
        return false;
        break;
      case h.ERROR_FAAS:
        if (protoGetString().length) exit_(protoGetString());

        protoPop();
        protoPush(h.NOTIFICATION_FAAS);
        protoPushString();
        break;
      case h.NOTIFICATION_FAAS:
        if (protoGetString().length) console.log(protoGetString() + "\n");

        ws.send(
          addString(
            addString(handleString(MAIN_PROTOCOL_LABEL), MAIN_PROTOCOL_VERSION),
            SCRIPT_VERSION,
          ),
        );
        protoPop();
        protoPush(h.ERROR_MAIN);
        protoPushString();
        break;
      case h.ERROR_MAIN:
        if (protoGetString().length) exit_(protoGetString());

        protoPop();
        protoPush(h.NOTIFICATION_MAIN);
        protoPushString();
        break;
      case h.NOTIFICATION_MAIN:
        if (protoGetString().length) console.log(protoGetString() + "\n");

        protoPop();
        break;
      default:
        if ( protoTop() >= 0 )
          exit_("Unknown handshake operation!" + protoTop());
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
  SERVE: 3,
};

var phase = p.HANDSHAKES;

function onRead(data, createCallback, head) {
  // console.log(">>>>> DATA:", data.length);

  let feeder = proto.getFeeder(data);

  while (!feeder.isEmpty()) {
    switch (phase) {
      case p.HANDSHAKES:
        if (!handshakes(feeder)) phase = p.IGNITION;
        break;
      case p.IGNITION:
        if (!ignition(feeder)) phase = p.SERVE;
        break;
      case p.SERVE:
        serve(feeder, createCallback, head);
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

function launch(createCallback, head, libraryVersion) {
  handler = proto.getHandler();

  phase = p.HANDSHAKES;
  token = "";

  if (ws !== undefined) ws.close();

  log("Connecting to '" + WS_URL_ + "'…");

  ws = new WebSocket(WS_URL_);

  ws.onerror = function (err) {
    log("Unable to connect to '" + WS_URL_ + "'!");
  };

  ws.onopen = function () {
    log("Connected to '" + WS_URL_ + "'.");
    protoPush(h.HANDSHAKES);
    protoPush(h.ERROR_FAAS);
    protoPushString();
    ws.send(
      addString(
        addString(handleString(FAAS_PROTOCOL_LABEL), FAAS_PROTOCOL_VERSION),
        "BRY " + libraryVersion,
      ),
    );
  };
  ws.onclose = function () {
    log("Disconnected!");
  };
  ws.onmessage = function (event) {
    blob2Buffer(event.data, function (err, buffer) {
      onRead(buffer, createCallback, head);
    });
  };
}

function addTagged(data, argument) {
  if (typeof argument === "string") {
    return addString(
      Buffer.concat([data, convertUInt(types.STRING)]),
      argument,
    );
  } else if (typeof argument === "object") {
    return addStrings(
      Buffer.concat([data, convertUInt(types.STRINGS)]),
      argument,
    );
  } else exit_("Unexpected argument type: " + typeof argument);
}

function call(instance, command, type, callback) {
  ///( Date.now(), " Command: ", command, instance._xdh.id);

  if (!instance._xdh.inProgress) exit_("Out of frame function call!");

  let i = 4;
  let data = convertSInt(instance._xdh.id);
  let amount = arguments.length;

  data = Buffer.concat([addString(data, command), convertUInt(type)]);

  while (i < amount) data = addTagged(data, arguments[i++]);

  data = Buffer.concat([data, convertUInt(types.VOID)]); // To report end of argument list.

  ws.send(data);

  if (type === types.VOID) {
    if (callback !== undefined) callback();
    else {
      standBy(instance);
      // console.log();
    }
  } else if (type !== types.UNDEFINED) {
    let pending = new Object();

    pending.type = type;
    pending.callback = callback;

    instance._xdh.queued.push(pending);
  } else exit_("'UNDEFINED' type not allowed here!");
}

function broadcastAction(action, id) {
  if (action === undefined || action === "")
    exit_(
      "There must be an non-empty action parameter for the broadcastAction function!",
    );

  ws.send(
    addString(
      addString(convertSInt(responseIds.BROADCAST), action),
      id === undefined ? "" : id,
    ),
  );
}

function getAppURL() {
  return app_url_;
}

module.exports = {
  launch,
  call,
  standBy,
  getCallbackBundle,
  broadcastAction,
  getAppURL,
}
