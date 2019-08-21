# coding: utf-8
"""
MIT License

Copyright (c) 2019 Claude SIMON (https://q37.info/s/rmnmqd49)

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

import os
import threading
import sys
import inspect
import traceback

# When set to true, execptions behave normally again
# instead of being displayed in a alert box.
regularException = False

# Detecting 'Repl.it' environment.
if ('HOME' in os.environ) and (os.environ['HOME'] == '/home/runner'):
  os.environ["ATK"] = "REPLit"

sys.path.append("./Atlas.python.zip")
sys.path.append("../Atlas.python.zip")

import atlastk as Atlas

_HEAD_COMMON = """
<link rel="icon" type="image/png" href="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAgBAMAAACBVGfHAAAAMFBMVEUEAvyEhsxERuS8urQsKuycnsRkYtzc2qwUFvRUVtysrrx0ctTs6qTMyrSUksQ0NuyciPBdAAABHklEQVR42mNgwAa8zlxjDd2A4POfOXPmzZkFCAH2M8fNzyALzDlzg2ENssCbMwkMOsgCa858YOjBKxBzRoHhD7LAHiBH5swCT9HQ6A9ggZ4zp7YCrV0DdM6pBpAAG5Blc2aBDZA68wCsZPuZU0BDH07xvHOmAGKKvgMP2NA/Zw7ADIYJXGDgLQeBBSCBFu0aoAPYQUadMQAJAE29zwAVWMCWpgB08ZnDQGsbGhpsgCqBQHNfzRkDEIPlzFmo0T5nzoMovjPHoAK8Zw5BnA5yDosDSAVYQOYMKIDZzkoDzagAsjhqzjRAfXTmzAQgi/vMQZA6pjtAvhEk0E+ATWRRm6YBZuScCUCNN5szH1D4TGdOoSrggtiNAH3vBBjwAQCglIrSZkf1MQAAAABJRU5ErkJggg==" />
"""

_S_ROOT = "_storage"
_S_GLOBAL = "global"
_S_DOM = "dom"
_S_CORE = "core"
_S_USER_ITEMS = "userItems"

globals()[_S_ROOT] = {}

globals()[_S_ROOT][_S_GLOBAL] = {}


def _threadId():
  return threading.currentThread().ident


def _store(set, key, value, g):
  g[_S_ROOT][set][key] = value


def _recall(set, key, g):
  return g[_S_ROOT][set][key]


def store(key, value, g = globals()):
  try:
    _store(_threadId(), key, value,g)
  except KeyError:
    #    print('KE store ' + key)
    _store(_S_GLOBAL, key, value, g)


def recall(key,g=globals()):
  try:
    return _recall(_threadId(), key, g)
  except KeyError:
    #    print('KE recall ' + key)
    return _recall(_S_GLOBAL, key, g)


def dom():
  return recall(_S_DOM)


def core():
  return recall(_S_CORE)


class Core:
  def __init__(self, dom, userObject=None):
    globals()[_S_ROOT][_threadId()] = {}
    store(_S_DOM, dom)
    store(_S_CORE, self)
    self.userObject = userObject


def _read(path):
  return open(path).read()


def _translate(text, i18n):
  if i18n == None:
    return text

  for key in i18n:
    text = text.replace("$" + key + "$", i18n[key])

  return text


def read(fileName, i18n=None):
  return _translate(_read(fileName), i18n)


def readHTML(path, affix, i18n=None):
  return read(os.path.join('workshop', 'assets', path, affix + ".html"), i18n)


def readBody(path, i18n=None):
  return readHTML(path, "Body", i18n)


def setUserItems(ids, items, labels):
  links = {}

  for id in ids:
    label = labels[id]

    if not label in items:
      raise NameError("Missing '{}' item.".format(label))

    links[id] = items[label]

  store(_S_USER_ITEMS, links)


def defineUserItem(g,prefix,name):
  g[prefix + name] = lambda : recall(_S_USER_ITEMS,g)[name]


def _readHead(path, title, i18n=None):
  return "<title>" + title + "</title>\n" + _HEAD_COMMON + readHTML(path, "Head", i18n)


# Should be the almost identical as in 'Atlas.py'
def _call(func, userObject, dom, id, action):
	amount = len(inspect.getargspec(func).args)
	args = []

	if (not(userObject)):
		amount += 1

	if (amount == 4):
		args.insert(0, action)

	if(amount >= 3):
		args.insert(0, id)

	if(amount >= 2):
		args.insert(0, dom)

	if(userObject and (amount >= 1)):
		args.insert(0, userObject)

	try:
		return func(*args)
	except Exception as e:
		if regularException:
			raise e
		else:
			dom.alert("PYTHON EXCEPTION:\n\n" + traceback.format_exc())

def _patchWithCoreObject(userCallbacks):
  callbacks = {}

  for action in userCallbacks:
    callbacks[action] = lambda core, dom, id, action: _call(
        userCallbacks[action], core, dom, id, action)

  return callbacks


def _patchWithoutCoreObject(userCallbacks):
  callbacks = {}

  for action in userCallbacks:
    callbacks[action] = lambda dom, id, action: _call(
        userCallbacks[action], None, dom, id, action)

  return callbacks


def main(path, callback, callbacks, title):
  Atlas.launch(_patchWithCoreObject(callbacks) if callback else _patchWithoutCoreObject(
      callbacks), callback, _readHead(path, title))
