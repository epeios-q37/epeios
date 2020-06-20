#!/usr/bin/python3
# coding: utf8

# Si installé avec 'pip install term2web',
# les deux lignes suivanes peuvent être retirée.
import sys, os
sys.path.append("./Atlas.zip")

import os
import atlastk as Atlas

head = "<title>" + os.path.splitext(__file__)[0] + " - Atlas toolkit</title>"

def prettify(body):
    return """
<div style="display: table; margin: 50px auto auto auto;">
 <fieldset>
""" + body + """
 </fieldset>
</div>
"""

# selected="selected"

# End of header.

# Montrer également le ''size="…"'

body = """
<p>Veuillez choisir un dinosaure :</p>
<select id="dinosaure" data-xdh-onevent="Select">
    <optgroup label="Théropodes">
        <option value="tyrannosaure">Tyrannosaure</option>
        <option value="vélociraptor">Vélociraptor</option>
        <option value="deinonychus">Deinonychus</option>
    </optgroup>
    <optgroup label="Sauropodes">
        <option value="diplodocus">Diplodocus</option>
        <option value="saltasaurus">Saltasaurus</option>
        <option value="apatosaurus">Apatosaurus</option>
    </optgroup>
    <optgroup id="autres" label="Autres"/>
</select>
<fieldset>
  <span>Élément sélectionné : </span><span id="Output"/>
</fieldset>
<div>
  <button data-xdh-onevent="Submit">Envoyer</button>
</div>
<div>
  <input id="input" data-xdh-onevent="Add"/>
  <button data-xdh-onevent="Add">Ajouter</button>
</div>
"""

def ac_connect(dom):
	dom.set_layout("", prettify(body))

def ac_select(dom,id):
  dom.set_content("Output", dom.get_content(id))

def ac_submit(dom):
  dom.alert(dom.get_content("dinosaure"))

def embed(other):
  html = Atlas.create_HTML()

  html.push_tag("option")
  html.put_value(other)
#  html.pop_tag()

  return html

def ac_add(dom):
#  dom.prepend_layout("autres", "<option>" + dom.getContent("input") + "</option>")
  dom.prepend_layout("autres", embed(dom.getContent("input")))
  dom.set_content("input", "")
  dom.focus("input")


callbacks = {
	"": ac_connect,
  "Select": ac_select,
  "Submit": ac_submit,
  "Add": ac_add
}

Atlas.launch(callbacks, None, head)