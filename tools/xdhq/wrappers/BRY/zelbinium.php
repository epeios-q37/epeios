<?php
$demo = "Messages";

echo <<< CONTENT
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
        editor = ace.edit("Source", { showLineNumbers: true, newLineMode: "auto" });
        editor.setTheme("ace/theme/monokai");
        editor.session.setMode("ace/mode/python");
        editor.setFontSize(14);
        editor.setShowPrintMargin(false);
      }
    </script>
    <script type="text/python" id="script"></script>
    <style type="text/css" media="screen">
      #Source {
        height: 100%;
        width: 100%;
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

      .dropdown {
        display: inline-block;
        position: relative;
      }
      .dropdown-content {
        display: none;
        position: absolute;
        width: 100%;
        overflow: auto;
        box-shadow: 0px 10px 10px 0px rgba(0,0,0,0.4);
      }
      .dropdown:hover .dropdown-content {
        display: block;
      }
      .dropdown-content a {
        display: block;
        color: #000000;
        padding: 5px;
        text-decoration: none;
        background-color: white;
      }
      .dropdown-content a:hover {
        color: #FFFFFF;
        background-color: #00A4BD;
      }
    </style>
  </head>

  <body onload="getSourceCode('{$demo}');dress()">
    <details class="source" open="true">
      <summary class="source" style="display: flex; ; align-items: center;">
        <span role="term" class="source" aria-details="pure-css">Source code</span>
        <span style="width: 20px;"></span>
        <div class="dropdown" onclick="document.getElementById('Source').parentNode.previousElementSibling.removeAttribute('open')" style="z-index: 10;">
          <div>Content</div>
          <div class="dropdown-content">
            <button onclick="editor.session.setValue('');">Clear</button>
          </div>
        </div>
        <span style="width: 5px;"></span>
        <button onclick="go();">Run</button>
      </summary>
    </details>
    <div role="definition" id="pure-css" class="source" style="display: flex; flex-flow: column; height: 100%;">
      <div id="Source" style="height: calc(100% - 50px);"># Type your code here or select an example above,
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
CONTENT
?>