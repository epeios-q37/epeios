import socket
import ssl

import Q37

HOST           =  "zelbinium.q37.info"       #input the remote server
PORT           =   443            #input the remote PORT

Q37.connect(Q37.HOME)

s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
print(HOST, PORT)
s.connect(socket.getaddrinfo(HOST,PORT)[0][-1])
s=ssl.wrap_socket(s)
print("Ap.")
print("TCP Connected to:", HOST, ":", PORT)
s.write('GET /\n\r')
while True:
    data = s.read(1024)
    if(len(data) == 0):
      print("Close socket")
      s.close()
      break
    print(data)
    ret=s.write(data)
