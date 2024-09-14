# MicroController Remove Server (runs on the µcontroller)

import Q37
import socket, sys, _thread, uos

PROTOCOL_LABEL_ = "2b45ad37-2dcd-437c-9185-6ffbfcedfbbf"
PROTOCOL_VERSION_ = "0"

_writeLock = _thread.allocate_lock()


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
  send_( bString)


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
  

def exit_(message):
  print(message, file=sys.stderr)
  sys.exit(-1)


def init_():
  global socket_

  pAddr = "192.168.1.87"
  pPort = 12345

  socket_ = socket.socket()
  
  print("Connection to '" + str(pAddr) + ":" + str(pPort) + "'…")

  try:
    socket_.connect((pAddr,pPort))
  except:
    exit_("Unable to connect to '" + str(pAddr) + ":" + str(pPort) + "'!")
  else:
    print("Connected to '" + str(pAddr) + ":" + str(pPort) + "'.")
  

def handshake_():
  with _writeLock:
    writeString_(PROTOCOL_LABEL_)
    writeString_(PROTOCOL_VERSION_)
    writeString_(uos.uname().sysname)

  error = getString_()

  if error:
    sys.exit(error)

  notification = getString_()

  if notification:
    print(notification)


def ignition_():
  print("Token handling to come…")


def serve_():
  while True:
    command = getString_()

    print("Command: ", command)

    exec(command)


def main():
  WLAN = Q37.HOME

  Q37.connect(WLAN)

  init_()

  handshake_()

  ignition_()

  serve_()

main()