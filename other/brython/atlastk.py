import javascript, sys, threading
from collections import OrderedDict
from browser import timer

javascript.import_js("atlastkbry.js", alias="atlastkjs")

_VOID = 0
_STRING = 1
_STRINGS = 2

def _split(keysAndValues):
	keys = []
	values = []

	for key in keysAndValues:
		keys.append(str(key))
		values.append(str(keysAndValues[key]))

	return [keys,values]

def _unsplit(keys,values):
	i = 0
	# With 'OrderedDict', the order of the items is keeped under Python 2.
	# This facilitates the retrieving of values by using 'values()' method.
	# Dicts are ordered by default under Python 3.
	keysAndValues = OrderedDict()
	length = len(keys)

	while i < length:
		keysAndValues[keys[i]] = values[i]
		i += 1

	return keysAndValues

def call_(instance, command, type, callback, *args):
  timer.set_timeout(atlastkjs.call, 0, instance, command, type, callback, *args)
#  atlastkjs.call(instance, command, type, callback, *args)
  
def voidCallback_(lock):
  print("voidCallback")
  lock.release()

def stringCallback_(jsString, lock, string):
  print("stringCallback")
  string = jsString
  lock.release()

def stringsCallback_(jsStrings, lock, strings):
  print("stringsCallback")
  strings = jsStrings
  print("R Before")
  lock.release()
  print("R After")

class Lock:
  def __init__(self):
    self.locked_ = False
    self.lock_ = threading.Lock()

  def acquire(self):
    print("A In")
    self.lock_.acquire()
    while self.locked_:
      pass
    self.locked_ = True
    print("A Out")

  def release(self):
    print("R In")
    self.lock_.release()
    self.locked_ = False
    print("R Out")

class DOM:
  def __init__(self,instance):
    self.instance = instance

  def call_(self, command, type, *args):
    lock = Lock()

    lock.acquire()

    if type == _STRING:
      print("Awaiting string!")
      string = ""
      call_(self, command, type, lambda result : stringCallback_(result, lock, string), *args )
      print("AS Before")
      lock.acquire()
      print("AS After")
      return string
    elif type == _STRINGS:
      print("Awaiting stringS!")
      strings = []
      call_(self, command, type, lambda result : stringsCallback_(result, lock, strings), *args )
      print("ASS Before")
      lock.acquire()
      print("ASS After")
      return strings
    elif type == _VOID:
      call_(self, command, type, lambda : voidCallback_(lock), *args )
      lock.acquire()
    else:
      sys.exit("Unknown return type !!!")  

    lock.release() 
    
  def get_action(self):
    return self._dom.getAction()

  getAction = get_action

  def isQuitting(self):
    return self._dom.isQuitting()

  def _execute(self,type,script):
    return self.call_("Execute_1",type,script)

  # Last statement of 'script' MUST be 'undefined', or the thread will be killed.
  def executeVoid(self,script):
    return self._execute(_VOID,script)

  execute_void = executeVoid

  def executeString(self,script):
    return self._execute(_STRING,script)

  execute_string = executeString

  def executeStrings(self,script):
    return self._execute(_STRINGS,script)

  execute_strings = executeStrings

  def _raw_send(self,type,data):
    return self.call_("RawSend_1",type,data)

  # Last statement of 'data' MUST be 'undefined', or the thread will be killed.
  def rawSendVoid(self,data):
    return self._raw_send(_VOID,data)

  raw_send_void = rawSendVoid

  def rawSendString(self,data):
    return self._raw_send(_STRING,data)

  raw_send_string = rawSendString

  def rawSendStrings(self,data):
    return self._raw_send(_STRINGS,data)

  raw_send_strings = rawSendStrings	

  def flush(self):	# Returns when all the pending commands were executed.
    self.call_("Flush_1",_STRING)

  def alert(self,message):
    self.call_( "Alert_1",_STRING,str(message) )
    # For the return value being 'STRING' instead of 'VOID',
    # see the 'alert' primitive in 'XDHqXDH'.

  def confirm(self,message):
    return self.call_( "Confirm_1",_STRING,message ) == "true"

  def _handleLayout(self,variant,id,xml,xsl):
    #	If 'xslFilename' is empty, 'xml' contents HTML.
    # If 'xml' is HTML and uses the compressed form, if it has a root tag, only the children will be used.
    # The corresponding primitive returns a value, which is only used internally, hence the lack of 'return'.
    # It also serves to do some synchronisation.
    self.call_("HandleLayout_1",_STRING,variant,id,xml if isinstance(xml,str) else xml.toString(),xsl)

  def prependLayout(self,id,html):	# Deprecated!
    self._handleLayout("Prepend",id,html,"")

  prepend_layout = prependLayout	# Deprecated!

  def setLayout(self,id,html):	# Deprecated!
    self._handleLayout("Set",id,html,"")

  set_layout = setLayout	# Deprecated!

  def appendLayout(self,id,html):	# Deprecated!
    self._handleLayout("Append",id,html,"")

  append_layout = appendLayout	# Deprecated!

  def _handleLayoutXSL(self,variant,id,xml,xsl):	# Deprecated!
    xslURL = xsl

    if True:	# Testing if 'SlfH' or 'FaaS' mode when available.
      xslURL = "data:text/xml;charset=utf-8," + _encode(_readXSLAsset(xsl))

    self._handleLayout(variant,id,xml,xslURL )

  def prependLayoutXSL(self,id,xml,xsl):	# Deprecated!
    self._handleLayoutXSL("Prepend",id,xml,xsl)

  prepend_layout_XSL = prependLayoutXSL	# Deprecated!

  def setLayoutXSL(self,id,xml,xsl):	# Deprecated!
    self._handleLayoutXSL("Set",id,xml,xsl)

  set_layout_XSL = setLayoutXSL	# Deprecated!

  def appendLayoutXSL(self,id,xml,xsl):	# Deprecated!
    self._handleLayoutXSL("Append",id,xml,xsl)

  append_layout_XSL = appendLayoutXSL	# Deprecated!

  def _layout(self,variant,id,xml,xsl):
    if xsl:
      xsl = "data:text/xml;charset=utf-8," + _encode(_readXSLAsset(xsl))

    self.call_("HandleLayout_1",_STRING,variant,id,xml if isinstance(xml,str) else xml.toString(),xsl)

  def before(self,id,xml,xsl=""):
    self._layout("beforebegin",id,xml,xsl)

  def begin(self,id,xml,xsl=""):
    self._layout("afterbegin",id,xml,xsl)

  def inner(self,id,xml,xsl=""):
    print("Inner !!!")
    self._layout("inner",id,xml,xsl)

  def end(self,id,xml,xsl=""):
    self._layout("beforeend",id,xml,xsl)

  def after(self,id,xml,xsl=""):
    self._layout("afterend",id,xml,xsl)

  # Deprecated
  def getContents(self,ids):
    return _unsplit(ids,self.call_("GetContents_1",_STRINGS,ids))

  # Deprecated
  get_contents = getContents

  # Deprecated
  def getContent( self,id):
    return self.getContents([id])[id]

  # Deprecated
  get_content = getContent

  def getValues(self,ids):
    return _unsplit(ids,self.call_("GetValues_1",_STRINGS,ids))

  get_values = getValues

  def getValue( self,id):
    return self.get_values([id])[id]

  get_value =  getValue

  def getMarks(self,ids):
    return _unsplit(ids,self.call_("GetMarks_1",_STRINGS,ids))

  get_marks = getMarks

  def getMark( self,id):
    return self.get_marks([id])[id]

  get_mark = getMark

  # Deprecated
  def setContents(self,ids_and_contents):
    [ids,contents] = _split(ids_and_contents)

    self.call_("SetContents_1",_VOID,ids,contents)

  # Deprecated
  set_contents = setContents

  # Deprecated
  def setContent(self,id,content):
    self.set_contents({id: content})

  # Deprecated
  set_content = setContent

  def setValues(self,ids_and_values):
    [ids,values] = _split(ids_and_values)

    self.call_("SetValues_1",_VOID,ids,values)

  set_values = setValues

  def setValue(self,id,value):
    self.set_values({id: value})

  set_value = setValue

  def setMarks(self,ids_and_marks):
    [ids,marks] = _split(ids_and_marks)

    self.call_("SetMarks_1",_VOID,ids,marks)

  set_marks = setMarks

  def setMark(self,id,mark):
    self.set_marks({id: mark})

  set_mark = setMark

  def _handleClasses(self,variant,idsAndClasses):
    [ids,classes] = _split(idsAndClasses)

    self.call_("HandleClasses_1",_VOID,variant,ids,classes)

  def addClasses(self,ids_and_classes):
    self._handleClasses("Add",ids_and_classes)

  add_classes = addClasses

  def removeClasses(self,ids_and_classes):
    self._handleClasses("Remove",ids_and_classes)

  remove_classes = removeClasses		

  def toggleClasses(self,ids_and_classes):
    self._handleClasses("Toggle",ids_and_classes)

  toggle_classes = toggleClasses

  def addClass(self,id,clas ):
    self.addClasses({id: clas})

  add_class = addClass

  def removeClass(self,id,class_ ):
    self.removeClasses({id: class_})

  remove_class	= removeClass

  def toggleClass(self,id,clas ):
    self.toggleClasses({id: clas})

  toggle_class = toggleClass

  def enableElements(self,ids):
    self.call_("EnableElements_1",_VOID,ids )

  enable_elements = enableElements		

  def enableElement(self,id):
    self.enableElements([id] )

  enable_element = enableElement		

  def disableElements(self,ids):
    self.call_("DisableElements_1",_VOID,ids )

  disable_elements = disableElements		

  def disableElement(self,id):
    self.disableElements([id])

  disable_element = disableElement

  def setAttribute(self,id,name,value ):
    self.call_("SetAttribute_1",_VOID,id,name,str(value) )

  set_attribute = setAttribute		

  def getAttribute(self,id,name):
    return self.call_("GetAttribute_1",_STRING,id,name )

  get_attribute = getAttribute		

  def removeAttribute(self,id,name ):
    self.call_("RemoveAttribute_1",_VOID,id,name )

  remove_attribute = removeAttribute

  def setProperty(self,id,name,value ):
    self.call_("SetProperty_1",_VOID,id,name,value )

  set_property = setProperty		

  def getProperty(self,id,name ):
    return self.call_("GetProperty_1",_STRING,id,name )

  get_property = getProperty		

  def focus(self,id):
    self.call_("Focus_1",_VOID,id)

  def parent(self,id):
    return self.call_("Parent_1",_STRING,id)

  def firstChild(self,id):
    return self.call_("FirstChild_1",_STRING,id)

  first_child = firstChild

  def lastChild(self,id):
    return self.call_("LastChild_1",_STRING,id)

  last_child = lastChild

  def previousSibling(self,id):
    return self.call_("PreviousSibling_1",_STRING,id)

  previous_sibling = previousSibling		

  def nextSibling(self,id):
    return self.call_("NextSibling_1",_STRING,id)

  next_sibling = nextSibling

  def scrollTo(self,id):
    self.call_("ScrollTo_1",_VOID,id)

  scroll_to = scrollTo

  def debugLog(self,switch=True):
    self.call_("DebugLog_1",_VOID,"true" if switch else "false")

  def log(self,message):
    self.call_("Log_1",_VOID,message)

def _callback(userCallback):
  return DOM(userCallback())


def launch(callbacks, userCallback = lambda : None, headContent = ""):
  atlastkjs.launch(callbacks, lambda : _callback(userCallback), headContent)

