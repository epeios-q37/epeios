"""
MIT License

Copyright (c) 2020 Claude SIMON (https://q37.info/s/rmnmqd49)

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
"""

import html
import sys
import threading
import time

sys.path.append("./atlastk.zip")
sys.path.append("../atlastk.zip")

import atlastk as Atlas

head = """
<title>'term2web' for Python</title>
<link rel="icon" type="image/png" href="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAgBAMAAACBVGfHAAAAMFBMVEUEAvyEhsxERuS8urQsKuycnsRkYtzc2qwUFvRUVtysrrx0ctTs6qTMyrSUksQ0NuyciPBdAAABHklEQVR42mNgwAa8zlxjDd2A4POfOXPmzZkFCAH2M8fNzyALzDlzg2ENssCbMwkMOsgCa858YOjBKxBzRoHhD7LAHiBH5swCT9HQ6A9ggZ4zp7YCrV0DdM6pBpAAG5Blc2aBDZA68wCsZPuZU0BDH07xvHOmAGKKvgMP2NA/Zw7ADIYJXGDgLQeBBSCBFu0aoAPYQUadMQAJAE29zwAVWMCWpgB08ZnDQGsbGhpsgCqBQHNfzRkDEIPlzFmo0T5nzoMovjPHoAK8Zw5BnA5yDosDSAVYQOYMKIDZzkoDzagAsjhqzjRAfXTmzAQgi/vMQZA6pjtAvhEk0E+ATWRRm6YBZuScCUCNN5szH1D4TGdOoSrggtiNAH3vBBjwAQCglIrSZkf1MQAAAABJRU5ErkJggg==" />
<style type="text/css">
  input[type="text"] {
    border: none;
  }

  input[type="text"]:disabled {
    background-color: transparent;
    color: inherit;
  }

  fieldset {
    font-family: monospace;
    font-size: larger;
  }
</style>
"""

body = """
    <fieldset id="Output" data-xdh-onevent="Focus"/>
"""

print_ = ""
printBuffer_ = "<span>"
printReadLock_ = threading.Lock()
printReadLock_.acquire()
printWriteLock = threading.Lock()
printWriteLock.acquire()

flushLock = threading.Lock()
autoFlush_ = False

input_ = ""
inputRead_ = threading.Lock()
inputRead_.acquire()
inputWrite_ = threading.Lock()
inputWrite_.acquire()

properties_ = {}


def getStyle_():
  style = ""

  for name in properties_: 
    style += name + ": " + properties_[name] + "; "

  return style


def openingTag_():
  return "<span style='" + getStyle_() + "'>"


def closingTag_():
  return "</span>"


def reset_properties():
  global properties_, printBuffer_

  properties_ = {}

  printBuffer_ += closingTag_()
  printBuffer_ += openingTag_()


def set_property(name, value):
  properties_[name] = value

  printBuffer_ += closingTag_()
  printBuffer_ += openingTag_()
  

def set_properties(properties):
  global printBuffer_

  for name in properties:
    properties_[name] = properties[name]

  printBuffer_ += closingTag_()
  printBuffer_ += openingTag_()
  

def handleSpecialChars_(text):
  return text.replace('\n', "<br/>").replace(" ","&nbsp;")


def flush_():
  global print_, printBuffer_, autoFlush_

  if printBuffer_:
    flushLock.acquire()
    printWriteLock.acquire()
    print_ = printBuffer_ + closingTag_()
    printBuffer_ = openingTag_()
    printReadLock_.release()
    flushLock.release()

  autoFlush_ = False


def addToBuffer_(text):
  global printBuffer_

  text= str(text)

  printBuffer_ += handleSpecialChars_(html.escape(text))


def print(*args, sep=" ", end="\n"):
  global autoFlush_

  first = True

  for arg in args:
    if first:
      first = False
    else:
      addToBuffer_(sep)

    addToBuffer_(arg)

  addToBuffer_(end)

  autoFlush_ = True


def input(prompt=""):
  global input_, autoFlush_

  autoFlush_ = False

  if prompt:
    print(prompt,end="")
    flush_()

  result = ""
  printWriteLock.acquire()
  printReadLock_.release()
  inputRead_.acquire()
  result = input_
  input_ = ""
  inputWrite_.release()

  return result


def scrollToBottom_(dom):
  dom.execute_void("window.scrollTo(0,document.getElementById('Output').scrollHeight);")


def loop_(dom):
  global print_, autoFlush_
  
  cont = True
  
  autoFlush_ = True

  while cont:
    printReadLock_.acquire()

    if print_:
      dom.appendLayout("Output", "<span>" + print_ + "</span>")
      scrollToBottom_(dom)
      print_ = ""
    else:
      cont = False

    printWriteLock.release()

  dom.appendLayout("Output","<span><input type='text' id='Input' data-xdh-onevent='Submit'/><br/></span>")
  scrollToBottom_(dom)
  dom.focus("Input")


def acConnect(dom):
  dom.setLayout("", body)
  printWriteLock.release()
  inputWrite_.release()
  loop_(dom)


def acSubmit(dom, id):
  global input_

  inputWrite_.acquire()
  input_ = dom.getContent("Input")
  dom.disableElement("Input")
  dom.removeAttribute("Input","data-xdh-onevent")
  dom.removeAttribute("Input","id")
  inputRead_.release()
  loop_(dom)


def acFocus(dom):
  dom.focus("Input")


callbacks = {
  "": acConnect,
  "Submit": acSubmit,
  "Focus": acFocus,
}


class Atlas_(threading.Thread):
  def __init__(self):
    threading.Thread.__init__(self)

  def run(self):
    Atlas.launch(callbacks, None, head)


atlasThread_ = Atlas_()
# _atlasThread.daemon = True
atlasThread_.start()


class Flush_(threading.Thread):
  def __init__(self):
    threading.Thread.__init__(self)

  def run(self):
    while True:
      time.sleep(.1)
      if autoFlush_:
        flush_()


flushThread_ = Flush_()
# _flushThread.daemon = True
flushThread_.start()

