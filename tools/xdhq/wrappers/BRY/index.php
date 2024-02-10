<?php

$demo = $_REQUEST["demo"];

echo <<<BODY
<html>
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/ace/1.32.2/ace.min.js" type="text/javascript"
      charset="utf-8"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/ace/1.32.2/mode-python.min.js"
      integrity="sha512-DUdq0nHbbCHQMqQNALNivk5tAdpFWOpm3mplXDwBqIpXD6/vfgXp8fESbfsnePQT3jZKVI3mCbEQumz/S4IHPA=="
      crossorigin="anonymous" referrerpolicy="no-referrer"></script>
    <script type="text/javascript">
      function go() {
        document.getElementById("Source").parentNode.previousElementSibling.removeAttribute("open");
        document.getElementById("Brython").style["display"] = "";
        document.getElementById("Code").value = editor.getValue();
        document.forms['Brython'].submit();
      }
    </script>
    <script type="text/javascript">
      function getSourceCode(demo) {
        document.getElementById("Brython").style["display"] = "none";
        fetch('https://raw.githubusercontent.com/epeios-q37/brython/main/' + demo + '.py').then(function (response) {
          return response.text();
        }).then(function (data) {
          editor.session.setValue(data)
          document.getElementById("Source").parentNode.previousElementSibling.setAttribute("open", 'true');
        }).catch(function (err) {
          console.warn('Something went wrong.', err);
        });
      }  
    </script>
    <script type="text/javascript">
      var editor = undefined;
      function dress() {
        fillExamples();
        editor = ace.edit("Source", { showLineNumbers: true, newLineMode: "auto" });
        editor.setTheme("ace/theme/monokai");
        editor.session.setMode("ace/mode/python");
        editor.setFontSize(14);
        editor.setShowPrintMargin(false);
      }
    </script>
    <script type="text/javascript">
      function fillExamples() {
        fetch('https://raw.githubusercontent.com/epeios-q37/brython/main/List.json').then(function (response) {
          return response.text();
        }).then(function (list) {
          entries = JSON.parse(list).entries;

          examples = document.getElementById("Examples");

          for (let i = 0; i < entries.length; i++) {
            entry = entries[i];
            option = document.createElement("option");
            option.innerText = entry;
            option.value = entry;
            examples.appendChild(option);
          }

          if ( "{$demo}" != "" ) {
            examples.value = "{$demo}";
            examples.dispatchEvent(new Event('change'));
          }
        }).catch(function (err) {
        console.warn('Unable to retrieve example list: ', err);
      });
      }
    </script>
    <!-- Will be filled on run. -->
    <script type="text/python" id="script"></script>
    <style type="text/css" media="screen">
      #Source {
        height: 100%;
        width: 100%;
      }

      details.source {
        overflow: hidden;
        width: fit-content;
        /* Keep this line to prevent an odd blue outline around the element in Safari. */
      }

      summary.source::-webkit-details-marker {
        display: none;
      }

      span.source {
        position: relative;
        display: flex;
        align-items: center;
        height:40px;
      }

      span.source:hover {
        cursor: pointer;
      }

      span.source::before {
        content: "►";
        font-size: 1rem;
        display: flex;
        align-items: center;
        margin-right: 0.5rem;
        transition: rotate 200ms 400ms ease-out;
      }

      div.source {
        box-sizing: border-box;
        max-height: 0;
        overflow: hidden;
        padding: 0 10px;
        transition: max-height 400ms ease-out, border 0ms 400ms linear;
      }

      details.source[open]+div.source {
        max-height: 100%;
        transition: max-height 400ms ease-out, border 0ms linear;
      }

      details.source[open] span.source::before {
        rotate: 90deg;
        transition: rotate 200ms ease-out;
      }
    </style>
  </head>

  <body style="margin: 0 5px 0 5px;" onload="dress()">
    <details class="source" open="true">
      <summary class="source" style="display: flex; ; align-items: center;">
        <span role="term" class="source" aria-details="pure-css">Code</span>
        <span style="width: 10px;"></span>
        <!-- Filled with the content of the 'List.json' file in the 'brython' GitHub repo.-->
        <select id="Examples" onchange="getSourceCode(this.value)">
          <option disabled="true" selected="true" value="">Select an example</option>
        </select>
        <span style="width: 5px;"></span>
        <span style="width: 5px;"></span>
        <button onclick="go();">Run</button>
      </summary>
    </details>
    <div role="definition" id="pure-css" class="source" style="display: flex; flex-flow: column; height: 100%; padding: 0;">
      <div id="Source"># Type your code here or select an example above,
# and then click the 'Run' button. Enjoy!</div>
      <div>
        <details>
          <summary style="list-style: none;">
            <img style="width: 24px; height: 24px;" src="data:image/svg+xml;base64,PD94bWwgdmVyc2lvbj0iMS4wIiA/PjxzdmcgaGVpZ2h0PSIxMDI0IiB3aWR0aD0iMTAyNCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cGF0aCBkPSJNNTE0IDE5MmMzNC0xIDYxLTI4IDYyLTYyIDEtMzctMjktNjctNjYtNjYtMzQgMS02MSAyOC02MiA2Mi0xIDM3IDI5IDY3IDY2IDY2eiBtNDY0IDM4NGgtMThsLTEyNy0yNDZjMTgtMiAzNi05IDUyLTE2IDI0LTExIDI5LTQzIDExLTYybC0xLTFjLTExLTExLTI4LTE1LTQzLTgtMTQgNi0zNCAxMy01MyAxMy01NiAwLTgxLTY0LTI4Ny02NHMtMjMxIDY0LTI4NyA2NGMtMjAgMC0zOS02LTUzLTEzLTE1LTYtMzItMy00MyA4bC0xIDFjLTE4IDE5LTEzIDUwIDExIDYyIDE2IDggMzQgMTQgNTIgMTZsLTEyNyAyNDZoLTE4Yy04IDAtMTQgNy0xMyAxNSAxMSA2NCA5MiAxMTMgMTkxIDExM3MxODAtNDkgMTkxLTExM2MxLTgtNS0xNS0xMy0xNWgtMThsLTEyNy0yNDVjODMtNyAxMjctNDkgMTkxLTQ5djQ4NmMtMzUgMC02NCAyOS02NCA2NGgtNzFjLTI4IDAtNTcgMjktNTcgNjRoNTEyYzAtMzUtMjktNjQtNzEtNjRoLTU3YzAtMzUtMjktNjQtNjQtNjR2LTQ4NmM2NCAwIDEwOCA0MiAxOTEgNDlsLTEyNyAyNDVoLTE4Yy04IDAtMTQgNy0xMyAxNSAxMSA2NCA5MiAxMTMgMTkxIDExM3MxODAtNDkgMTkxLTExM2MxLTgtNS0xNS0xMy0xNXogbS02NTggMGgtMTkybDk2LTE4MCA5NiAxODB6IG0zODQgMGw5Ni0xODAgOTYgMTgwaC0xOTJ6Ii8+PC9zdmc+"/>
          </summary>
          <span>Third-part software components:</span>
            <ul style="margin: 0;">
              <li><a target="_blank" href="https://ace.c9.io/"><em>Ace editor</em></a> (<a href="https://github.com/ajaxorg/ace/blob/master/LICENSE" target="_blank">licence</a>);</li>
              <li><a target="_blank" href="https://atlastk.org"><em>Atlas toolkit</em></a> (<a href="https://github.com/epeios-q37/atlas-python/blob/master/LICENSE" target="_blank">licence</a>);</li>
              <li><a target="_blank" href="https://github.com/feross/blob-to-buffer"><em>blob-to-buffer</em></a> (<a href="https://github.com/feross/blob-to-buffer/blob/master/LICENSE" target="_blank">licence</a>);</li>
              <li><a target="_blank" href="http://brython.info"><em>Brython</em></a> (<a href="https://github.com/brython-dev/brython/blob/master/LICENCE.txt" target="_blank">licence</a>);</li>
              <li><a target="_blank" href="https://github.com/feross/buffer/"><em>buffer</em></a> (<a href="https://github.com/feross/buffer/blob/master/LICENSE" target="_blank">licence</a>);</li>
              <li><a target="_blank" href="https://github.com/liriliri/eruda"><em>eruda</em></a> (<a href="https://github.com/liriliri/eruda/blob/master/LICENSE" target="_blank">license</a>);</li>
              <li><a target="_blank" href="https://github.com/epeios-q37/tortoise-python"><em>tortoise-python</em></a> (<a href="https://github.com/epeios-q37/tortoise-python/blob/master/LICENSE" target="_blank">licence</a>).</li>
            </ul>
        </details>
      </div>
    </div>
    <form style="display: none;" action="/brython/brython.php" name="Brython" method="post" target="Brython">
      <input type="hidden" name="code" id="Code" />
    </form>
    <iframe name="Brython" src="" id="Brython" width="100%"
      style="display: none; height: calc(100% - 50px); border: 0px;">
    </iframe>
  </body>
</html>
BODY
?>