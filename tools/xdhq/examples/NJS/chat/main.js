/*
	Copyright (C) 2018 Claude SIMON (http://q37.info/contact/).

	This file is part of XDHq.

	XDHq is free software: you can redistribute it and/or
	modify it under the terms of the GNU Affero General Public License as
	published by the Free Software Foundation, either version 3 of the
	License, or (at your option) any later version.

	XDHq is distributed in the hope that it will be useful,
	but WITHOUT ANY WARRANTY; without even the implied warranty of
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
	Affero General Public License for more details.

	You should have received a copy of the GNU Affero General Public License
	along with XDHq If not, see <http://www.gnu.org/licenses/>.
*/

"use strict"

var atlasId = "";

if (process.env.EPEIOS_SRC) {
	let epeiosPath = "";

	if (process.platform == 'win32')
		epeiosPath = "h:/hg/epeios/"
	else
		epeiosPath = "~/hg/epeios/"

	atlasId = epeiosPath + "tools/xdhq/Atlas/NJS/Atlas.js";
} else {
	atlasId = 'atlastk';
}

const atlas = require(atlasId);

const fs = require('fs');

const DOM = atlas.DOM;
const readAsset = atlas.readAsset;

var pseudos = [];
var messages = [];

var messageBlockId;

class MyData extends DOM {
	constructor() {
		super();
		this.timestamp = new Date();
		this.pseudo = "";
		this.lastMessage = 0;
		this.blockId = 0;
	}
}

function displayMessages(dom) {
	var tree = require('xmlbuilder').create('XDHTML');
	var i = messages.length - 1;
	let script = `
		var node = document.createElement('span');
		var board = document.getElementById('Board');
		board.insertBefore(node, board.firstChild);
		node.id = "Block.` + dom.blockId + `";"";`;
	var message;

	tree = tree.ele("Messages", { 'pseudo': dom.pseudo } );

	while (i >= dom.lastMessage) {
		message = messages[i];
		tree = tree.ele('Message', { 'id': i, 'pseudo': message["pseudo"] }, message["content"]).up();
		i--;
	}

	dom.lastMessage = messages.length;

	tree = tree.up();

	dom.execute(script, () => dom.setLayoutXSL("Block." + dom.blockId++, tree.end(), "Messages.xsl") );
}


function newSession() {
	return new MyData();
}

function acConnect(dom, id) {
	dom.setLayout("", readAsset("Main.html"),
		() => dom.focus("Pseudo")
	);
}

function handlePseudo( pseudo ) 
{
	if (pseudos.includes(pseudo))
		return false;
	else {
		pseudos.push(pseudo);
		return true;
	}
}

function acSubmitPseudo(dom, id) {
	dom.getContent("Pseudo",
		(result) => {
			result = result.trim();

			if (result.length == 0)
				dom.alert("Pseudonyme vide !");
			else if (handlePseudo(result.toUpperCase())) {
				dom.pseudo = result;
				dom.setContent("Pseudo", result);
				dom.addClass("PseudoButton", "hidden");
				dom.disableElements(["Pseudo", "PseudoButton"]);
				dom.enableElements(["Message", "MessageButton"]);
				dom.focus("Message");
				console.log(">>>> New user: ", result);
			} else
				dom.alert("Pseudonyme pris !");
		}
	);
}

function acSubmitMessage(dom, id) {
	dom.getContent("Message",
		(result) => {
			result = result.trim();
			if (result.length != 0) {
				console.log(dom.pseudo, result);
				messages.push({
					"pseudo": dom.pseudo,
					"content": result
				});
				dom.setContent("Message", "",
					() => dom.focus("Message",
						() => displayMessages(dom)
					)
				);
			}
		});
}

function acUpdate(dom, id) {
	displayMessages(dom)
}


function main() {
	const callbacks = (
		{
			"Connect": acConnect,
			"SubmitPseudo": acSubmitPseudo,
			"SubmitMessage": acSubmitMessage,
			"Update": acUpdate,
		}
	);

	atlas.launch(newSession, "Connect", callbacks, readAsset( "Head.html") );
}

main();