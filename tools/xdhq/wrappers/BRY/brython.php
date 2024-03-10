<?php
$sourceCode = str_replace("</script>", "_BrythonWorkaroundForClosingScriptTag_", $_REQUEST['code']);

// Si modifié, adapter '/themes/hugo-book/layouts/_default/baseof.html(.ori)' de atlastk.org et zelbinium.q37.info.
$version = "3.11.3";

if (!empty($_REQUEST['version'])) {
  $version = $_REQUEST['version'];
}

if ( $version == "dev") {
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
  <script type="text/javascript" src="https://cdn.jsdelivr.net/npm/brython@$version/brython.js"></script>
  <script type="text/javascript" src="https://cdn.jsdelivr.net/npm/brython@$version/brython_stdlib.js"></script>
EOS;
}

echo <<< EOD
<head>
  <meta charset="utf-8">
  $brython
  <script src="https://cdn.jsdelivr.net/npm/eruda"></script>
  <script type="text/javascript">
    function launchApp(url) {
      app = document.getElementById("App");
      app.src = url;
      app.style["display"] = "";
    }
  </script>
  <script type="text/javascript">
    var console = {};
    console.error = function(text){alert(text)};
  </script>
</head>
<body onload="eruda.init();console.log('Brython version: $version');brython()" style="margin: 0;">
  <script type="text/python">
$sourceCode
  </script>
<iframe id="App" style="width: 100%; display: none; height: 100%;">
</iframe>
EOD
?>