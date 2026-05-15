import math

WIDTH_ = 128
HEIGHT_ = 64

buffer_ = [[0]*WIDTH_ for _ in range(HEIGHT_)]

def setPixel_(x, y):
  if 0 <= x < WIDTH_ and 0 <= y < HEIGHT_:
    buffer_[y][x] = 1


def drawLine_(x0, y0, x1, y1):
  dx = abs(x1 - x0)
  dy = -abs(y1 - y0)
  sx = 1 if x0 < x1 else -1
  sy = 1 if y0 < y1 else -1
  err = dx + dy

  while True:
    setPixel_(x0, y0)
    if x0 == x1 and y0 == y1:
      break
    e2 = 2 * err
    if e2 >= dy:
      err += dy
      x0 += sx
    if e2 <= dx:
      err += dx
      y0 += sy


def rotatePoint_(x, y, z, pitch, roll, yaw):
  p = math.radians(pitch)
  r = math.radians(roll)
  w = math.radians(yaw)

  # Pitch (X)
  y2 = y * math.cos(p) - z * math.sin(p)
  z2 = y * math.sin(p) + z * math.cos(p)

  # Yaw (Y)
  x3 = x * math.cos(w) + z2 * math.sin(w)
  z3 = -x * math.sin(w) + z2 * math.cos(w)

  # Roll (Z)
  x4 = x3 * math.cos(r) - y2 * math.sin(r)
  y4 = x3 * math.sin(r) + y2 * math.cos(r)

  return x4, y4, z3


def project_(x, y, z, scale=40):
  distance = 3
  factor = scale / (z + distance)
  xp = int(WIDTH_/2 + x * factor)
  yp = int(HEIGHT_/2 - y * factor)
  return xp, yp

cubeVertices_ = [
  (-1,-1,-1), (1,-1,-1), (1,1,-1), (-1,1,-1),
  (-1,-1, 1), (1,-1, 1), (1,1, 1), (-1,1, 1)
]

cubeEdges_ = [
  (0,1),(1,2),(2,3),(3,0),
  (4,5),(5,6),(6,7),(7,4),
  (0,4),(1,5),(2,6),(3,7)
]


def clearBuffer_():
  for y in range(HEIGHT_):
    for x in range(WIDTH_):
      buffer_[y][x] = 0


def bufferToHex_():
  hex_string = []
  for y in range(HEIGHT_):
    for x in range(0, WIDTH_, 4):
      nibble = (
        (buffer_[y][x]   << 3) |
        (buffer_[y][x+1] << 2) |
        (buffer_[y][x+2] << 1) |
        (buffer_[y][x+3] << 0)
      )
      hex_string.append(f"{nibble:X}")
  return "".join(hex_string)


def draw3DCube(x, y, z):
  """
  x = alpha (0–360°)  → yaw
  y = beta  (-180–180°) → pitch
  z = gamma (-90–90°) → roll
  """
  yaw   = -x
  pitch = -y
  roll  = -z

  clearBuffer_()

  projected = []
  for (vx, vy, vz) in cubeVertices_:
    xr, yr, zr = rotatePoint_(vx, vy, vz, pitch, roll, yaw)
    xp, yp = project_(xr, yr, zr)
    projected.append((xp, yp))

  for a, b in cubeEdges_:
    x0, y0 = projected[a]
    x1, y1 = projected[b]
    drawLine_(x0, y0, x1, y1)
    
  return bufferToHex_()

