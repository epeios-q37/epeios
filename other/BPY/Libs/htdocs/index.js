
function go() {
  if (collapse)
    document.getElementById("Source").parentNode.previousElementSibling.removeAttribute("open");
  document.getElementById("Brython").style["display"] = "";
  document.getElementById("Code").value = editor.getValue();
  document.forms['Brython'].submit();
  run = false;
}

function fetchCodeFromURL(url, callback) {
  fetch(url).then(function (response) {
    return response.text();
  }).then(function (data) {
    callback(data);
  }).catch(function (err) {
    console.warn(`Unable to fetch '${url}'`, err);
  });
}

function execute(code) {
  editor.session.setValue(code)
  old = code;
  document.getElementById("Source").parentNode.previousElementSibling.setAttribute("open", 'true');
  if (run)
    go();
}

// Called in 'index.php'.
function fetchDemoCode(demo) {
  collapse = true;
  document.getElementById("Brython").style["display"] = "none";
  fetchCodeFromURL(`https://raw.githubusercontent.com/epeios-q37/brython/main/${demo}.py`, execute)
}

function unpack(packedCode) {
  const binaryString = atob(decodeURIComponent(packedCode));
  
  const len = binaryString.length;
  const bytes = new Uint8Array(len);

  for (let i = 0; i < len; i++) {
      bytes[i] = binaryString.charCodeAt(i);
  }

  return pako.inflate(bytes, { to: 'string' });
}

function fillDemosList() {
  fetch('https://raw.githubusercontent.com/epeios-q37/brython/main/Demos.json').then(function (response) {
    return response.text();
  }).then(function (demos) {
    demoGroups = JSON.parse(demos);
    
    keys = Object.keys(demoGroups);

    select = document.getElementById("Demos");

    for ( var i in keys ) {
      optgroup = document.createElement("optgroup");
      optgroup.label = keys[i];
      
      demos = demoGroups[keys[i]]
      
      for ( j in demos ) {
        entry = demos[j];
        option = document.createElement("option");
        option.innerText = entry;
        option.value = entry;
        optgroup.appendChild(option);
      }
      
      select.append(optgroup);
    }

    let code = packedCode ? unpack(packedCode) : "";
    
    if ( code !== "" ) {
      select.value="None"
      code = code.replaceAll('_BrythonWorkaroundForBackQuote_', '`').replaceAll('_BrythonWorkaroundForSingleQuote_', "'")
      editor.session.setValue(code);

      old = code

      if ( cursor !== "" ) {
        editor.moveCursorTo(...cursor.split(",").map(Number));
        editor.focus();
      }

      if (run)
        go();
    } else if ( demo !== "" ) {
      select.value = demo;
      select.dispatchEvent(new Event('change'));
    } else if ( url !== "" ) {
      select.value = "None";
      fetchCodeFromURL(url, execute);
    } else if ( localStorage.getItem("brython-buffer" ) != null ) {
      editor.setValue(localStorage.getItem("brython-buffer"));
      if (run)
        go();
    }
  }).catch(function (err) {
    console.warn('Unable to retrieve demos list: ', err);
});
}

var code = '';
var old = '';

function sendCode() {
  if ( code !== editor.getValue() ) {
    code = editor.getValue();
    window.parent.postMessage([`${id}`, code], '*');
  }

  if ( old !== editor.getValue() ) {
    old = editor.getValue();
    if ( old !== "" ) 
      localStorage.setItem("brython-buffer", old);
    else
      localStorage.removeItem("brython-buffer");
  }

  window.setTimeout(sendCode, 150);
}


function dress() {
  fillDemosList();
  editor = ace.edit("Source", {
    showLineNumbers: true,
    newLineMode: "auto",
    tabSize: 2,
    wrap: true,
    theme: "ace/theme/monokai",
    mode: "ace/mode/python",
    fontSize: 14,
    showPrintMargin: false,
  });

  old = editor.getValue();

  sendCode();
}
