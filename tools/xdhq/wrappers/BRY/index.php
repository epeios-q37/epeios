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
        document.getElementById("ReadOnly").checked = true;
        document.getElementById("ReadOnly").dispatchEvent(new Event('change'));
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
        editor = ace.edit("Source", { showLineNumbers: true, newLineMode: "auto", readOnly: true });
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
        /* Keep this line to prevent an odd blue outline around the element in Safari. */
      }

      summary.source {
        display: block;
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

  <body onload="dress()">
    <details class="source" open="true">
      <summary class="source" style="display: flex; ; align-items: center;">
        <span role="term" class="source" aria-details="pure-css">Code</span>
        <span style="width: 20px;"></span>
        <!-- Filled with the content of the 'List.json' file in the 'brython' GitHub repo.-->
        <select id="Examples" onchange="getSourceCode(this.value)">
          <option disabled="true" selected="true" value="">Select an example</option>
        </select>
        <span style="width: 5px;"></span>
        <label>
          <input id="ReadOnly" type="checkbox" checked="true" onchange="editor.setReadOnly(this.checked);"/>
          <span>Read-only</span>
        </label>
        <span style="width: 5px;"></span>
        <button onclick="go();">Run</button>
      </summary>
    </details>
    <div role="definition" id="pure-css" class="source" style="display: flex; flex-flow: column; height: 100%;">
      <div id="Source"># Type your code here or select an example above,
# and then click the 'Run' button. Enjoy!</div>
    </div>
    <form action="/brython/brython.php" name="Brython" method="post" target="Brython">
      <input type="hidden" name="code" id="Code" />
    </form>
    <iframe name="Brython" src="" id="Brython" width="100%"
      style="display: none; height: calc(100% - 50px); border: 0px;">
    </iframe>
  </body>
</html>
BODY
?>