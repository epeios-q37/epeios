/*
MIT License

Copyright (c) 2018 Claude SIMON (https://q37.info/s/rmnmqd49)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
*/

var atlas;

if (process.env.Q37_EPEIOS) {
	let epeiosPath = "";

	if (process.platform === 'win32')
		epeiosPath = "h:/hg/epeios/";
	else
		epeiosPath = process.env.Q37_EPEIOS;

	atlas = require(epeiosPath + "tools/xdhq/Atlas/NJS/Atlas.js");
} else {
	atlas = require('atlastk');
}

const DOM = atlas.DOM;

const viewModeElements = ["Pattern", "CreateButton", "DescriptionToggling", "ViewNotes"];

class Notes extends DOM {
	constructor() {
		super();
		this.timestamp = new Date();
		this.pattern = "";
		this.hideDescriptions = false;
		this.id = 0;
		this.notes = [
			// First one must be empty; it is used as buffer for new entries.
			{
				title: '',
				description: ''
			}, {
				title: 'Improve design',
				description: "Tastes and colors… (aka «CSS aren't my cup of tea…»)"
			}, {
				title: 'Fixing bugs',
				description: 'There are bugs ? Really ?'
			}, {
				title: 'Implement new functionalities',
				description: "Although it's almost perfect…, isn't it ?"
			}
		];
	}
}

function newSession() {
	return new Notes();
}

function push(note, id, xml) {
	xml.pushTag('Note');
	xml.putAttribute('id', id);
	for (var prop in note) {
		xml.putTagAndValue(prop, note[prop]);
	}

	xml.popTag();

	return xml;
}

function handleDescriptions(dom) {
	if (dom.hideDescriptions)
		dom.disableElement("ViewDescriptions");
	else
		dom.enableElement("ViewDescriptions");
}

function displayList(dom) {
	var xml = atlas.createXML('XDHTML');
	var i = 1;	// 0 skipped, as it serves as buffer for the new ones.
	var contents = {};

	xml.pushTag("Notes");

	while (i < dom.notes.length) {
		if (dom.notes[i]['title'].toLowerCase().startsWith(dom.pattern)) {

			xml = push(dom.notes[i], i, xml);
			contents["Description." + i] = dom.notes[i]['description'];
		}
		i++;
	}

	xml.popTag();

	dom.inner("Notes", xml, xsl,
		() => dom.setValues(contents,
			() => dom.enableElements(viewModeElements,
				() => handleDescriptions(dom)
			)
		)
	);
}

function acConnect(dom, id) {
	dom.inner("", body,
		() => dom.enableElement("XDHFullWidth",
			() => displayList(dom)
		)
	);
}

function acSearch(dom, id) {
	dom.getValue("Pattern",
		(result) => {
			dom.pattern = result.toLowerCase();
			displayList(dom);
		}
	);
}

function acToggleDescriptions(dom, id) {
	dom.getValue(id,
		(result) => {
			dom.hideDescriptions = result === "true";
			handleDescriptions(dom);
		}
	);
}

function view(dom) {
	dom.enableElements(
		viewModeElements,
		() => {
			dom.setValue("Edit." + dom.id, "");
			dom.id = -1;
		}
	);
}

function edit(dom, id) {
	dom.id = parseInt(id);
	dom.inner("Edit." + id, note,
		() => dom.setValues(
			{
				"Title": dom.notes[dom.id]['title'],
				"Description": dom.notes[dom.id]['description']
			},
			() => dom.disableElements(
				viewModeElements,
				() => dom.focus("Title")
				)
			)
	);
}

function acEdit(dom, id) {
	dom.getMark(id,
		(result) => edit(dom, result)
	);
}

function acDelete(dom, id) {
	dom.confirm("Are you sure you want to delete this entry ?",
		(response) => {
			if (response) dom.getMark(id,
				(result) => {
					dom.notes.splice(parseInt(result), 1);
					displayList(dom);
				}
			);
		}
	);
}

function acSubmit(dom, id) {
	dom.getValues(["Title", "Description"],
		(result) => {
			var title = result['Title'].trim();
			var description = result['Description'];

			if (title !== '') {
				dom.notes[dom.id]['title'] = title;
				dom.notes[dom.id]['description'] = description;
				if (dom.id === 0) {
					dom.notes.unshift({ title: '', description: '' });
					displayList(dom);
				} else {
					let contents = {};
					contents["Title." + dom.id] = title;
					contents["Description." + dom.id] = description;
					dom.setValues(contents,
						() => view(dom)
					);
				}
			} else
				dom.alert("Title can not be empty !",
					() => dom.focus("Title") );
		}
	);
}

function acCancel(dom, id) {
	dom.getValues(["Title", "Description"],
		(result) => {
			if (dom.notes[dom.id]['title'] !== result['Title'] || dom.notes[dom.id]['description'] !== result['Description'])
				dom.confirm("Are you sure you want to cancel your modifications ?",
					(response) => {
						if (response === true) view(dom);
					}
				);
			else
				view(dom);
		}
	);
}

function main() {
	const callbacks = {
		"": acConnect,
		"ToggleDescriptions": acToggleDescriptions,
		"Search": acSearch,
		"Edit": acEdit,
		"Delete": acDelete,
		"Submit": acSubmit,
		"Cancel": acCancel
	};

	atlas.launch(newSession, callbacks, head);
}

// Content of 'Head.html'.
const head = `
<title>List of notes</title>
<script src="https://code.jquery.com/jquery-3.2.1.slim.min.js" integrity="sha256-k2WSCIexGzOj3Euiig+TlR8gA0EmPjuc79OEeY5L45g="
        crossorigin="anonymous"></script>
<script src="https://cdn.ckeditor.com/4.8.0/standard/ckeditor.js"></script>
<script src="https://cdn.ckeditor.com/4.8.0/standard/adapters/jquery.js"></script>
<style>
 .q37 {
	background: url("data:image/png;base64,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") no-repeat;
  background-size: contain;
	height: 100px;
	width: 100px;
	top: -50px;
  border-radius: 10%;
}

        .note-view {
	display: none;
}

        p[id^="Description."]{
	display: none;
}
</style>
<style id="ViewDescriptions">
        p[id^="Description."]{
	display: block;
}
</style>
<style id="ViewNotes">
        .note-view {
	display: flex;
}
</style>
<style>
 @import url(https://fonts.googleapis.com/css?family=Lato:300,300italic,400,700,700italic);

 /**
 * Base Elements
 */

 * {
	margin: 0;
	padding: 0;
  box-sizing: border-box;
}

 body,
 h1,
 h2,
 h3,
 h4,
 h5,
 h6,
 p,
 div,
 span,
 a {
  font-family: 'Lato', 'Open Sans', 'Helvetica Neue', 'Segoe UI', Helvetica, Arial, sans-serif;
  line-height: 1.5;
}

 body {
	background: #f3f3f3;
}

 a {
	color: #2185D0;
  text-decoration: none;
}

 p {
  line-height: 1.5;
  margin-bottom: 15px;
}


 /**
 * Button
 */

 .button {
	padding: 12px 30px 13px;
  text-decoration: none;
	color: #fff;
	background: #2185D0;
  border-radius: 5px;
	border: none;
  font-size: 16px;
	opacity: 0.9;
}

  .button: hover {
	opacity: 1;
}


 /**
 * Body Container
 */

 .container {
  max-width: 1024px;
  min-height: 100vh;
	background: #f9f9f9;
	margin: 0 auto;
}


 /**
 * Top Navigation
 */

 .menu {
	height: 4em;
  background-color: #677ae4;
  background-color: #05526A;
  background-color: #e46855;
}

  .menu h1 {
	padding: 7px 0 0 20px;
	color: #f9f9f9;
   font-size: 2.1em;
}

   .menu h1 em {
	position: relative;
	left: -12px;
}

  .menu a,
  .menu.links {
	display: inline-block;
}

  .menu a {
   text-decoration: none;
   line-height: 1;
	padding: 0 15px;
	color: #f9f9f9;
	opacity: 0.85;
}

   .menu a: hover,
   .menu a.active {
	opacity: 1;
}

  .menu.links {
	padding: 0 21px;
}

   .menu.links a {
	position: relative;
	bottom: 5px;
}

 .list-filter input {
	padding: 11px;
  font-size: 18px;
	width: 500px;
	margin: 50px auto;
  background-color: rgba(255, 255, 255, 0.75);
	border: solid 1px lightgray;
	display: block;
}

 .menu input: focus {
  background-color: #f9f9f9;
	outline: none;
}

 .menu button {
  margin-right: 15px;
	position: relative;
	top: -1px;
	left: -5px;
  border-top-left-radius: 0;
  border-bottom-left-radius: 0;
  background-color: #262626;
	cursor: pointer;
	opacity: 1;
}

  .menu button: hover {
   background-color: #111;
	opacity: 1;
}

 .menu.results {
	display: none;
	position: absolute;
	width: 215px;
	top: 54px;
	left: 10px;
  background-color: #f6f6f6;
  border-right: 1px solid rgba(0, 0, 0, 0.05);
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}

 .results li {
  list-style: none;
	padding: 10px 15px;
}

 .menu.results li: hover {
	background: #f3f3f3;
}


 /**
 * Content Area
 */

 .body {
	padding: 15px;
}


 /**
 * Similar to Jumbotron
 */

 .jumbo {
	padding: 50px;
	background: #f6f6f6;
}

  .jumbo: hover {
   background-color: #f3f3f3;
}

  .jumbo h2 {
   font-size: 3.2em;
   margin-top: -25px;
}

  .jumbo p {
   margin-bottom: 25px;
}

  .jumbo img {
	height: 200px;
	position: relative;
	top: -25px;
	right: -20px;
}


 /**
 * Individual Listings
 */

 .listing {
  margin-top: 15px;
  background-color: #f6f6f6;
	padding: 15px 50px;
	position: relative;
}

  .listing: hover {
   background-color: #f3f3f3;
}

  .listing img {
	height: 100px;
	float: left;
   margin-right: 45px;
   border-radius: 5px;
}

  .listing a.image.wide {
   max-width: 100%;
	position: relative;
   z-index: 999;
}

  .listing.wide img {
	height: initial;
	width: 100%;
   margin-bottom: 30px;
}

  .listing.wide small {
	display: none;
}

  .listing a.image {
   max-width: 150px;
	display: block;
	cursor: pointer;
}

  .listing small {
	float: left;
	display: block;
   text-align: center;
	width: 136px;
}

  .listing h3 {
	padding: 0 15px 0 0;
}

   .listing h3 a {
	display: inline;
}

  .listing.map {
	position: absolute;
	bottom: 13px;
	right: 50px;
	height: 120px;
	width: 120px;
   background-size: cover;
   border-radius: 5px;
}

  .listing.detail {
	width: 36%;
	display: inline-block;
	padding: 10px 15px 0 0;
	margin: 0;
   font-weight: 300;
   font-style: italic;
}

   .listing.detail span {
    font-weight: 400;
    font-style: normal;
}

 .show-listing.title {
  margin-bottom: 15px;
}

 .show-listing.detail-section {
	width: 50%;
  padding-left: 30px;
}

 .show-listing.owner {
  margin-top: 10px;
}

 .show-listing.rental-pic {
	width: 50%;
	height: initial;
	position: static;
}


 /**
 * Utilities
 */

 .light {
  font-weight: 300;
}

 .left {
	float: left;
}

 .right {
	float: right;
}

 .hidden {
	display: none;
}

 .relative {
	position: relative;
}

	.xdh_style {
		display: initial;
	}
</style>
`;

// Content of 'main.html'.
const body = `
<div class ="menu">
 <a>
  <h1>
   <em>Notes</em>
  </h1>
 </a>
</div>
<div class ="jumbo">
 <a class ="right q37" href="http://q37.info/" ></a>
 <h2>Welcome!</h2>
 <p>
  <span>Let's take some notes with the </span>
  <span style="font-weight: bold;">
   <span style="font-style: oblique">Atlas</span>
   <span> toolkit</span>
  </span>
  <span>!</span>
 </p>
 <a href="http://atlastk.org/" class ="button">
  <span>    About   </span>
 </a>
</div>
<div>
 <span class ="list-filter">
  <input id="Pattern" placeholder="Filter By Title" class ="liset-filter light" type="text" xdh:onevent="Search" />
 </span>
 <div style="margin: auto; display: flex; justify-content: space-around; width: 50%;">
  <span>
   <label>
    <input id="DescriptionToggling" type="checkbox" xdh:onevent="ToggleDescriptions" />
    <span> Hide descriptions </span>
   </label>
  </span>
  <button class ="button" id="CreateButton" xdh:value="0" xdh:onevent="Edit">Create</button>
 </div>
</div>
<div id="Notes" />
`;

// Content of 'Note.html'.
// The escaping char must be escaped too (last argument of the 'xdh:widget' attribute value)!
const note = `
<div>
	<article class ="listing">
		<div>
			<span class ="list-filter">
				<input type="text" id="Title" placeholder="Title"/>
			</span>
			<textarea id="Description" xdh:widget="ckeditor|{entities: false, enterMode : CKEDITOR.ENTER_BR, linkShowTargetTab: false}|val\\(\\)|"></textarea>
		</div>
		<span style="display:inline-block; width: 10px;"></span>
		<div style="display: flex; justify-content: space-around;">
			<button class ="button" xdh:onevent="Submit">Submit</button>
			<span></span>
			<button class ="button" xdh:onevent="Cancel">Cancel</button>
		</div>
	</article>
</div>
`;

// Content of 'Notes.xsl'.
// Note to developer:
// DON'T PASTE TO Visual Studio : it inserts extraneous characters !
// There must be NO characters before the XML declaration !
const xsl = `<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" 
	xmlns="http://www.w3.org/1999/xhtml" 
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
	<xsl:output method="html" encoding="UTF-8"/>
	<xsl:template match="/XDHTML">
		<xsl:apply-templates select="Notes"/>
	</xsl:template>
	<xsl:template match="Notes">
		<ul>
			<li>
				<span id="View.0"></span>
				<span id="Edit.0"></span>
			</li>
			<xsl:apply-templates select="Note"/>
		</ul>
	</xsl:template>
	<xsl:template match="Note">
		<li>
			<span id="View.{@id}">
				<div>
					<article class="listing note-view" style="width:100%; justify-content: space-between;align-items: center;" xdh:mark="{@id}">
						<div>
							<h3 id="Title.{@id}">
								<xsl:value-of select="title"/>
							</h3>
							<p id="Description.{@id}">
								<!-- 'disable-output-escaping' does not work with Firefox (https://bugzilla.mozilla.org/show_bug.cgi?id=98168)	-->
								<!--xsl:value-of select="description" disable-output-escaping="yes"/-->
							</p>
						</div>
						<span id="Buttons.{@id}" style="flex-direction: row;">
							<button class="button" xdh:onevent="Edit" xdh:value="{@id}">Edit</button>
							<span style="display:inline-block; width: 10px;"></span>
							<button class="button" xdh:onevent="Delete" xdh:value="{@id}">Delete</button>
						</span>
					</article>
				</div>
			</span>
			<span id="Edit.{@id}"></span>
		</li>
	</xsl:template>
</xsl:stylesheet>
`;

main();