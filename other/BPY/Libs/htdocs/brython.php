<?php
$sourceCode = str_replace("</script>", "_BrythonWorkaroundForClosingScriptTag_", $_REQUEST['code']);

// Si modifié, adapter '/themes/hugo-book/layouts/_default/baseof.html' de atlastk.org et zelbinium.q37.info.
const BRYTHON_VERSION = "3.13.1";
const ERUDA_VERSION = "3.4.1";

$brython_version = $_REQUEST['brython'] ?? BRYTHON_VERSION;
$eruda_version = $_REQUEST['eruda'] ?? ERUDA_VERSION;
$use_ucuq_demo_devices = isset($_REQUEST["useUCUqDemoDevices"]) ? "true" : "false";

if ( $brython_version == "dev") {
 $brython = <<< EOS
 <script src="https://raw.githack.com/brython-dev/brython/master/www/src/brython.js"
 crossorigin="anonymous">
</script>
<script src="https://raw.githack.com/brython-dev/brython/master/www/src/brython_stdlib.js"
   crossorigin="anonymous">
</script>
EOS;
} else {
  $brython = <<< EOS
  <script type="text/javascript" src="https://cdn.jsdelivr.net/npm/brython@$brython_version/brython.js"></script>
  <script type="text/javascript" src="https://cdn.jsdelivr.net/npm/brython@$brython_version/brython_stdlib.js"></script>
EOS;
}

echo <<< EOD
<head>
  <meta charset="utf-8">
  $brython
  <script src="https://cdn.jsdelivr.net/npm/eruda@$eruda_version/eruda.min.js"></script>
  <script type="text/javascript">
    var useUCUqDemoDevices_ = $use_ucuq_demo_devices;

    function launchApp(url) {
      app = document.getElementById("App");
      app.src = url;
      app.style["display"] = "";
    }

    function onLoad() {
      eruda.init();
      console.log("Brython version: $brython_version; eruda version: $eruda_version");
      brython();
    }
  </script>
  <script type="text/javascript">
    console.error = function(text){alert(text)};
  </script>
</head>
<body onload="onLoad()" style="margin: 0;">
  <script type="text/python">
$sourceCode
  </script>
<iframe id="App" style="width: 100%; display: none; height: 100%; border: none;">
</iframe>
EOD
?>