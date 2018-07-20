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

const fs = require('fs');

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
const Tree = atlas.Tree;
const DOM = atlas.DOM;

const readAsset = atlas.readAsset;

class MyData extends DOM {
	constructor() {
		super();
		this.timestamp = new Date();
	}
}

function newSession() {
	console.log("New session detected !");

	return new MyData();
}

function acConnect(dom, id) {
	dom.headUp( readAsset( "Head.html"), () => dom.setLayout("", readAsset( "Main.html")));
}

function acSubmit(dom, id) {
	dom.getContent("Pattern",
		(result) => dom.setContent("Pattern", result.toUpperCase())
	);
}

function acHideInput(dom, id) {
	dom.addClass("Input", "hidden");
}

function acShowInput(dom, id) {
	dom.removeClass("Input", "hidden");
}

function main() {
	const callbacks = (
		{
			"Connect": acConnect,
			"Submit": acSubmit,
			"HideInput": acHideInput,
			"ShowInput": acShowInput,
		}
	);

	atlas.launch(newSession, "Connect", callbacks );
}

main();
