```python
import atlastk
 
BODY = """
<fieldset>
 <input id="Input" xdh:onevent="Submit" value="World"/>
 <button xdh:onevent="Submit">Hello</button>
 <hr/>
 <fieldset>
  <output id="Output">Greetings displayed here!</output>
 </fieldset>
</fieldset>
"""
 
def atk(dom): # Callback called on new connections.
  dom.inner("", BODY)
  dom.focus("Input")
 
def atkSubmit(dom): # Callback for the 'Submit' action, hence the name.
  name = dom.getValue("Input")
  dom.begin("Output", f"<div>Hello, {name}!</div>")
  dom.setValue("Input", "")
  dom.focus("Input")
 
atlastk.launch(globals=globals())
```