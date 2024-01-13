var ws = undefined;

function log(message) {
	console.log(message);
}

const
	receiveCallbacksQueue = [],
	receiveDataQueue = [];

function promiseConnect(URL) {
	return new Promise(function(resolve, reject) {
		var ws = new WebSocket(URL);
		ws.onopen = function() {
				resolve(ws);
		};
		ws.onerror = function(err) {
				reject(err);
		};
	});
}

function handleMessage(messageEvent) {
	if (receiveCallbacksQueue.length !== 0) {
			// Somebody is waiting to receive this message.
			receiveCallbacksQueue.shift().resolve(messageEvent.data);
			return;
	}

	// Enqueue.
	receiveDataQueue.push(messageEvent.data);
};

function receive() {
	if (receiveDataQueue.length !== 0) {
		// We have a message ready.
		return Promise.resolve(receiveDataQueue.shift());
	}

	// Wait for the next incoming message and receive it.
	const receivePromise = new Promise((resolve, reject) => {
		receiveCallbacksQueue.push({ resolve, reject });
	});

	return receivePromise;
};    

var ws = undefined;

async function c(cb) {
	log("Yo!!!");
	await cb()
	log("YoP!!!");
}


async function launch(URL) {
	log("Before !")
	ws = await promiseConnect(URL);
	log("1")
	ws.onclose = () => log("Close.")
	log("2")
	ws.onmessage = (event) => handleMessage(event);
	log("3")
	log( await receive() )
	log("4")
}

async function call(message) {
	ws.send(message);

	return await receive()
}

function relay(c, aws) {
	return { c: c, aws: aws};
}

var $module = {
	call: call,
	launch: launch,
	relay: relay,
}


