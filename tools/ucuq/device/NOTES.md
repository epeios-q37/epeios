# Notes à l'usage du développeur

## Publication

Est publié dans le dépôt *ucuq-python*. LE *README* n'est donc pas utilisé.

## *Micropython*

### Installation

Utiliser les scripts `UCQD_FlashErase` et `UCQD_FlashWrite <firmware>`.

### Extension *CSCode*

L'extension *VSCode* *MicroPython* permet de lancer l'exécution d'un fichier *Python* sur un *Raspberry Pico (W)*, mais fonctionne aussi avec quelques *ESP32* bien que cette extension est censé être dédiés au *Raspberry Pico (W)*

## Connection au WiFi

Le code suivant peut être utilisé pour la fonction *init_* de quelques *ESP32*, mais pas avec un *Raspberry Pi Pico W*, pour lequel `poller.poll()` rend la main de suite malgré le *timeout*. L'objet *socket* contient alors un membre *status* dont la valeur diffère selon que la connection a réussi ou non (à investiguer).

Code inspiré par <https://github.com/micropython/micropython/issues/8326#issuecomment-1629036122>.

```python
def init_(address, port, callback):
  global socket_
  cont = True
  tries = 0

  socket_ = socket.socket()

  while cont:
    socket_.setblocking(False)
    poller = select.poll()
    poller.register(socket_)

    try:
      socket_.connect(socket.getaddrinfo(address, port)[0][-1])
    except OSError as e:
      if e.errno != errno.EINPROGRESS:
        callback(S_FAILURE_, 0)
        raise(e)
    
    cont = callback(S_UCUQ_, tries)

    while cont:
      res = poller.poll(1000)

      if res:
        break
      else:
        tries += 1
        cont = callback(S_UCUQ_, tries)

    if cont:
      if res[0][1] == select.POLLOUT | select.POLLIN: # Connection failed !
        tries += 1
        poller.unregister(socket_)
        socket_ = socket.socket()
      elif res[0][1] == select.POLLOUT:  # Connection succeed !
        break

  poller.unregister(socket_)
  socket_.setblocking(True)

  return cont
```
