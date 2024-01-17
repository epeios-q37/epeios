<?php
echo <<<EOD
<head>
  <meta charset="utf-8">
  <script type="text/javascript" src="https://cdn.jsdelivr.net/npm/brython@3.11.3/brython.js"></script>
  <script type="text/javascript" src="https://cdn.jsdelivr.net/npm/brython@3.11.3/brython_stdlib.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/eruda"></script>
  <script type="text/javascript">
  function launchApp(url) {
    app = document.getElementById("App");
    app.src = url;
    app.style["display"] = "initial";
  }
</script>
</head>
<body onload="eruda.init();brython()">
  <script type="text/python">
EOD . str_replace("</script>", "_BrythonWorkaroundForClosingScriptTag_", $_REQUEST["code"]) . <<<EOD
  </script>
<iframe id="App" style="width: 100%; display: none; height: 100%;">
</iframe>
EOD
?>