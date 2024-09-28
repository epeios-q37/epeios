# MicroController Remove Server (runs on the µcontroller)

UCUQ_ADDRESS_ = "ucuq.q37.info"
UCUQ_ADDRESS_ = "192.168.1.87" # dev
UCUQ_PORT_ = 53800

import socket, sys, threading

PROTOCOL_LABEL_ = "c37cc83e-079f-448a-9541-5c63ce00d960"
PROTOCOL_VERSION_ = "0"

_writeLock = threading.Lock()


def recv_(size):
  global socket_

  buffer = bytes()
  l = 0

  while l != size:
    buffer += socket_.recv(size-l)
    l = len(buffer)

  return buffer


def send_(value):
  global socket_

  totalAmount = len(value)
  amountSent = 0

  while amountSent < totalAmount:
    amountSent += socket_.send(value[amountSent:])	


def writeUInt_(value):
  result = bytes([value & 0x7f])
  value >>= 7

  while value != 0:
    result = bytes([(value & 0x7f) | 0x80]) + result
    value >>= 7

  send_(result)


def writeString_(string):
  bString = bytes(string, "utf-8")
  writeUInt_(len(bString))
  send_(bString)


def readByte_():
  return ord(recv_(1))


def readUInt_():
  byte = readByte_()
  value = byte & 0x7f

  while byte & 0x80:
    byte = readByte_()
    value = (value << 7) + (byte & 0x7f)

  return value


def getString_():
  size = readUInt_()

  if size:
    return recv_(size).decode("utf-8")
  else:
    return ""
  

def exit_(message=None):
  if message:
    print(message, file=sys.stderr)
  sys.exit(-1)


def init_():
  global socket_

  socket_ = socket.socket()
  
  print("Connection to UCUq server…", end="", flush=True)

  try:
    socket_.connect(socket.getaddrinfo(UCUQ_ADDRESS_, UCUQ_PORT_)[0][-1])
  except:
    exit_("FAILURE!!!")
  else:
    print("\r                                         \r",end="")
  

def handshake_():
  with _writeLock:
    writeString_(PROTOCOL_LABEL_)
    writeString_(PROTOCOL_VERSION_)
    writeString_("Frontend")
    writeString_("PYH")

  error = getString_()

  if error:
    sys.exit(error)

  notification = getString_()

  if notification:
    print(notification)


def ignition_():
  writeString_("DummtToken")

  error = getString_()

  if error:
    exit_(error)


def connect():
  init_()
  handshake_()
  ignition_()


def execute(Command):
  writeString_(Command)
