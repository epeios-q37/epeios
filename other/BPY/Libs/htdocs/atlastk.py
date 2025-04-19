import javascript, inspect, types
from collections import OrderedDict
from browser import aio

LIB_VERSION = "0.14.1"

javascript.import_js("atlastk.js", "atlastkjs")

# Options entries
O_CALLBACKS_PREFIX_ = "CallbacksPrefix"
O_CONNECT_ACTION_AFFIX_ = "ConnectActionName"
O_PREPROCESS_ACTION_NAME_ = "PreprocessActionName"
O_POSTPROCESS_ACTION_NAME_ = "PostprocessActionName"

DEFAULT_CALLBACK_PREFIX = "atk"

options_ = {
  # Prefix of the name of a callback corresponding to an action
  # if absent from callbacks dict.
  # If 'None' or '', callbacks for the actions must be in callbacks dict.
  O_CALLBACKS_PREFIX_: DEFAULT_CALLBACK_PREFIX,
  # The affix for the connect action.
  O_CONNECT_ACTION_AFFIX_: "",
  # NOTA: there is no default callback name for below 2 actions.
  # They must be specifically defined in the callbacks dict.
  # Name of the preprocessing action.
  O_PREPROCESS_ACTION_NAME_: "_Preprocess",
  # Name of the postprocessing action.
  O_POSTPROCESS_ACTION_NAME_: "_Postprocess"
}

_VOID = 0
_STRING = 1
_STRINGS = 2

def _split(keysAndValues):
  keys = []
  values = []

  for key in keysAndValues:
    value = keysAndValues[key]
    if isinstance(value, list):
      for subValue in value:
        keys.append(str(key))
        values.append(str(subValue))
    else:
      keys.append(str(key))
      values.append(str(value))

  return [keys,values]

def _unsplit(keys,values):
  i = 0
  # With 'OrderedDict', the order of the items is kept under Python 2.
  # This facilitates the retrieving of values by using 'values()' method.
  # Dicts are ordered by default under Python 3.
  keysAndValues = OrderedDict()
  length = len(keys)

  while i < length:
    keysAndValues[keys[i]] = values[i]
    i += 1

  return keysAndValues

removePattern_ = lambda string, pattern: string[len(pattern):] if string.startswith(pattern) else string

def broadcastAction(action, id = ""):
	assert isinstance(action, (str, types.FunctionType))

	if isinstance(action, types.FunctionType):
		action = removePattern_(action.__name__, options_[O_CALLBACKS_PREFIX_])

	return atlastkjs.broadcastAction(action, id)  

def call_(instance, command, type, callback, *args):
  atlastkjs.call(instance, command, type, callback, *args)
  
def voidCallback_(lock):
  lock.release()

def stringCallback_(jsString, lock, wrapper):
  wrapper[0] = jsString
  lock.release()

def stringsCallback_(jsStrings, lock, wrapper):
  wrapper[0] = jsStrings
  lock.release()

class Lock:
  def __init__(self):
    self.locked_ = False

  async def acquire(self):
    while self.locked_:
      await aio.sleep(0)
    self.locked_ = True

  def release(self):
    self.locked_ = False

class DOM:
  def __init__(self, userCallback):
    if ( userCallback is not None ):
      args=[]

      if ( not(inspect.isclass(userCallback)) and len(inspect.getfullargspec(userCallback).args) == 1 ):
        args.append(self)

      self.userObject = userCallback(*args)
    else:
      self.userObject = None


  async def call_(self, command, type, *args):
    lock = Lock()

    await lock.acquire()

    if type == _STRING:
      wrapper = [""]
      call_(self, command, type, lambda result : stringCallback_(result, lock, wrapper), *args )
      await lock.acquire()
      return wrapper[0]
    elif type == _STRINGS:
      wrapper = [[]]
      call_(self, command, type, lambda result : stringsCallback_(result, lock, wrapper), *args )
      await lock.acquire()
      return wrapper[0]
    elif type == _VOID:
      call_(self, command, type, lambda : voidCallback_(lock), *args )
      await lock.acquire()
    else:
      raise Exception("Unknown return type !!!")  

    lock.release() 
    
  def get_action(self):
    return self._dom.getAction()

  getAction = get_action

  def isQuitting(self):
    return self._dom.isQuitting()

  async def _execute(self,type,script):
    return await self.call_("Execute_1",type,script)

  # Last statement of 'script' MUST be 'undefined', or the thread will be killed.
  async def executeVoid(self,script):
    return await self._execute(_VOID,script)

  execute_void = executeVoid

  async def executeString(self,script):
    return await self._execute(_STRING,script)

  execute_string = executeString

  async def executeStrings(self,script):
    return await self._execute(_STRINGS,script)

  execute_strings = executeStrings

  async def _raw_send(self,type,data):
    return await self.call_("RawSend_1",type,data)

  # Last statement of 'data' MUST be 'undefined', or the thread will be killed.
  async def rawSendVoid(self,data):
    return await self._raw_send(_VOID,data)

  raw_send_void = rawSendVoid

  async def rawSendString(self,data):
    return await self._raw_send(_STRING,data)

  raw_send_string = rawSendString

  async def rawSendStrings(self,data):
    return await self._raw_send(_STRINGS,data)

  raw_send_strings = rawSendStrings	

  async def flush(self):	# Returns when all the pending commands were executed.
    await self.call_("Flush_1",_STRING)

  async def alert(self,message):
    await self.call_( "Alert_1",_STRING,str(message) )
    # For the return value being 'STRING' instead of 'VOID',
    # see the 'alert' primitive in 'XDHqXDH'.

  async def confirm(self,message):
    return await self.call_( "Confirm_1",_STRING,message ) == "true"

  async def _handleLayout(self,variant,id,xml,xsl):
    #	If 'xslFilename' is empty, 'xml' contents HTML.
    # If 'xml' is HTML and uses the compressed form, if it has a root tag, only the children will be used.
    # The corresponding primitive returns a value, which is only used internally, hence the lack of 'return'.
    # It also serves to do some synchronisation.
    await self.call_("HandleLayout_1",_STRING,variant,id,xml if isinstance(xml,str) else xml.toString(),xsl)

  async def prependLayout(self,id,html):	# Deprecated!
    await self._handleLayout("Prepend",id,html,"")

  prepend_layout = prependLayout	# Deprecated!

  async def setLayout(self,id,html):	# Deprecated!
    await self._handleLayout("Set",id,html,"")

  set_layout = setLayout	# Deprecated!

  async def appendLayout(self,id,html):	# Deprecated!
    await self._handleLayout("Append",id,html,"")

  append_layout = appendLayout	# Deprecated!

  async def _handleLayoutXSL(self,variant,id,xml,xsl):	# Deprecated!
    xslURL = xsl

    if True:	# Testing if 'SlfH' or 'FaaS' mode when available.
      xslURL = "data:text/xml;charset=utf-8," + _encode(_readXSLAsset(xsl))

    await self._handleLayout(variant,id,xml,xslURL )

  async def prependLayoutXSL(self,id,xml,xsl):	# Deprecated!
    await self._handleLayoutXSL("Prepend",id,xml,xsl)

  prepend_layout_XSL = prependLayoutXSL	# Deprecated!

  async def setLayoutXSL(self,id,xml,xsl):	# Deprecated!
    await self._handleLayoutXSL("Set",id,xml,xsl)

  set_layout_XSL = setLayoutXSL	# Deprecated!

  async def appendLayoutXSL(self,id,xml,xsl):	# Deprecated!
    await self._handleLayoutXSL("Append",id,xml,xsl)

  append_layout_XSL = appendLayoutXSL	# Deprecated!

  async def _layout(self,variant,id,xml,xsl):
    if xsl:
      xsl = "data:text/xml;charset=utf-8," + _encode(_readXSLAsset(xsl))

    await self.call_("HandleLayout_1",_STRING,variant,id,xml if isinstance(xml,str) else xml.toString(),xsl)

  async def before(self,id,xml,xsl=""):
    await self._layout("beforebegin",id,xml,xsl)

  async def begin(self,id,xml,xsl=""):
    await self._layout("afterbegin",id,xml,xsl)

  async def inner(self,id,xml,xsl=""):
    await self._layout("inner",id,xml,xsl)

  async def end(self,id,xml,xsl=""):
    await self._layout("beforeend",id,xml,xsl)

  async def after(self,id,xml,xsl=""):
    await self._layout("afterend",id,xml,xsl)

  # Deprecated
  async def getContents(self,ids):
    return _unsplit(ids,await self.call_("GetContents_1",_STRINGS,ids))

  # Deprecated
  get_contents = getContents

  # Deprecated
  async def getContent( self,id):
    return await self.getContents([id])[id]

  # Deprecated
  get_content = getContent

  async def getValues(self,ids):
    return _unsplit(ids,await self.call_("GetValues_1",_STRINGS,ids))

  get_values = getValues

  async def getValue( self,id):
    return (await self.get_values([id]))[id]

  get_value =  getValue

  async def getMarks(self,ids):
    return _unsplit(ids,await self.call_("GetMarks_1",_STRINGS,ids))

  get_marks = getMarks

  async def getMark( self,id):
    return (await self.get_marks([id]))[id]

  get_mark = getMark

  # Deprecated
  async def setContents(self,ids_and_contents):
    [ids,contents] = _split(ids_and_contents)

    await self.call_("SetContents_1",_VOID,ids,contents)

  # Deprecated
  set_contents = setContents

  # Deprecated
  async def setContent(self,id,content):
    await self.set_contents({id: content})

  # Deprecated
  set_content = setContent

  async def setValues(self,ids_and_values):
    [ids,values] = _split(ids_and_values)

    await self.call_("SetValues_1",_VOID,ids,values)

  set_values = setValues

  async def setValue(self,id,value):
    await self.set_values({id: value})

  set_value = setValue

  async def setMarks(self,ids_and_marks):
    [ids,marks] = _split(ids_and_marks)

    await self.call_("SetMarks_1",_VOID,ids,marks)

  set_marks = setMarks

  async def setMark(self,id,mark):
    await self.set_marks({id: mark})

  set_mark = setMark

  async def _handleClasses(self,variant,idsAndClasses):
    [ids,classes] = _split(idsAndClasses)

    await self.call_("HandleClasses_1",_VOID,variant,ids,classes)

  async def addClasses(self,ids_and_classes):
    await self._handleClasses("Add",ids_and_classes)

  add_classes = addClasses

  async def removeClasses(self,ids_and_classes):
    await self._handleClasses("Remove",ids_and_classes)

  remove_classes = removeClasses		

  async def toggleClasses(self,ids_and_classes):
    await self._handleClasses("Toggle",ids_and_classes)

  toggle_classes = toggleClasses

  async def addClass(self,id,clas ):
    await self.addClasses({id: clas})

  add_class = addClass

  async def removeClass(self,id,class_ ):
    await self.removeClasses({id: class_})

  remove_class	= removeClass

  async def toggleClass(self,id,clas ):
    await self.toggleClasses({id: clas})

  toggle_class = toggleClass

  async def enableElements(self,ids):
    await self.call_("EnableElements_1",_VOID,ids )

  enable_elements = enableElements		

  async def enableElement(self,id):
    await self.enableElements([id] )

  enable_element = enableElement		

  async def disableElements(self,ids):
    await self.call_("DisableElements_1",_VOID,ids )

  disable_elements = disableElements		

  async def disableElement(self,id):
    await self.disableElements([id])

  disable_element = disableElement

  async def setAttribute(self,id,name,value ):
    await self.call_("SetAttribute_1",_VOID,id,name,str(value) )

  set_attribute = setAttribute		

  async def getAttribute(self,id,name):
    return await self.call_("GetAttribute_1",_STRING,id,name )

  get_attribute = getAttribute		

  async def removeAttribute(self,id,name ):
    await self.call_("RemoveAttribute_1",_VOID,id,name )

  remove_attribute = removeAttribute

  async def setProperty(self,id,name,value ):
    await self.call_("SetProperty_1",_VOID,id,name,value )

  set_property = setProperty		

  async def getProperty(self,id,name ):
    return await self.call_("GetProperty_1",_STRING,id,name )

  get_property = getProperty		

  async def focus(self,id):
    await self.call_("Focus_1",_VOID,id)

  async def parent(self,id):
    return await self.call_("Parent_1",_STRING,id)

  async def firstChild(self,id):
    return await self.call_("FirstChild_1",_STRING,id)

  first_child = firstChild

  async def lastChild(self,id):
    return await self.call_("LastChild_1",_STRING,id)

  last_child = lastChild

  async def previousSibling(self,id):
    return await self.call_("PreviousSibling_1",_STRING,id)

  previous_sibling = previousSibling		

  async def nextSibling(self,id):
    return await self.call_("NextSibling_1",_STRING,id)

  next_sibling = nextSibling

  async def scrollTo(self,id):
    await self.call_("ScrollTo_1",_VOID,id)

  scroll_to = scrollTo

  async def debugLog(self,switch=True):
    await self.call_("DebugLog_1",_VOID,"true" if switch else "false")

  async def log(self,message):
    await self.call_("Log_1",_VOID,message)

def _callback(userCallback):
  return DOM(userCallback)

def buildArgs(callback, bundle):
  amount = len(inspect.getfullargspec(callback).args)
  args = []

  instance = bundle.instance 
  userObject = instance.userObject

  if not userObject:
    amount += 1

  if amount == 4:
    args.insert(0, bundle.action)

  if amount >= 3:
    args.insert(0, bundle.id)

  if amount >= 2:
    args.insert(0, instance)

  if userObject and ( amount >= 1 ):
    args.insert(0, userObject)

  return args

async def callCallback_(callback, bundle):
  return await callback(*buildArgs(callback, bundle))

async def handleCallbackBundle(userCallbacks, callingGlobals, bundle):
  action = bundle.action

  if action == "":
    bundle.instance.language = bundle.id[:bundle.id.find(';')]
    bundle.id =  bundle.id[bundle.id.find(';') + 1:]

  if action == ""\
    or not options_[O_PREPROCESS_ACTION_NAME_] in userCallbacks\
    or await callCallback_(userCallbacks[options_[O_PREPROCESS_ACTION_NAME_]], bundle) in [None, True]:

    callback = None

    if action in userCallbacks:
      callback = userCallbacks[action]
    elif options_[O_CALLBACKS_PREFIX_]:
      callbackName = options_[O_CALLBACKS_PREFIX_] + ( options_[O_CONNECT_ACTION_AFFIX_] if action == "" else action )

      if callbackName in callingGlobals:
        callback = callingGlobals[callbackName]

    if callback:
      bundle.instance.callbackReturnValue = await callCallback_(callback, bundle)

      if options_[O_POSTPROCESS_ACTION_NAME_] in userCallbacks:
        await callCallback_(userCallbacks[options_[O_POSTPROCESS_ACTION_NAME_]],bundle)

      atlastkjs.standBy(bundle.instance)
    else:
      await bundle.instance.alert(("\tDEV ERROR: missing callback for '" + action + "' action!"))

async def handleCallbackBundles(callbacks, callingGlobals):
  if callingGlobals == None:
    callingGlobals = {}

  if callbacks == None:
    callbacks = {}

  while True:
    bundle = await atlastkjs.getCallbackBundle()
    aio.run(handleCallbackBundle(callbacks, callingGlobals, bundle))

def retrieve_(var, id, globals):
  if ( var == None ) and ( id in globals ):
    return globals[id]
  
  return var

def launch(callbacks = None, *, userCallback = None, globals = None, headContent = None):

  if globals != None:
    callbacks = retrieve_(callbacks, "ATK_CALLBACKS", globals)
    userCallback = retrieve_(userCallback, "ATK_USER", globals)
    headContent = retrieve_(headContent, "ATK_HEAD", globals)

  if headContent == None:
    headContent = ""

  atlastkjs.launch(lambda : _callback(userCallback), headContent.replace("_BrythonWorkaroundForClosingScriptTag_","</script>"), LIB_VERSION)

  aio.run(handleCallbackBundles(callbacks, globals))

class XML:
  def _write(self,value):
    self._xml += str(value) + "\0"

  def __init__(self,rootTag):
    self._xml = ""
    self._write("dummy")
    self._write(rootTag)

  def pushTag(self,tag):
    self._xml += ">"
    self._write(tag)

  push_tag = pushTag

  def popTag(self):
    self._xml += "<"

  pop_tag = popTag
  
  def putAttribute(self,name,value):
    self._xml += "A"
    self._write(name)
    self._write(str(value))

  put_attribute = putAttribute
  
  def putValue(self,value):
    self._xml += "V"
    self._write(str(value))

  put_value = putValue		

  def putTagAndValue(self,tag,value):
    self.pushTag(tag)
    self.putValue(value)
    self.popTag()

  put_tag_and_value = putTagAndValue

  def toString(self):
    return self._xml

  to_string = toString		

def createXML(root_tag):
  return XML(root_tag)

def createHTML(root_tag=""):	# If 'root_tag' is empty, there will be no root tag in the tree.
  return XML(root_tag)

async def sleep(time):
  await aio.sleep(time)

def getAppURL(id=""):
  return atlastkjs.getAppURL() + ("&_id=" + str(id) if id else "")

def options(options = None):
  if options != None:
    global options_

    for key in options:
      if not key in options_:
        raise Exception(f"Unknown option '{key}'!")
      else:
        options_[key] = options[key]

  return options_

def isDev():
  return False  # No dev environment in Brython.
