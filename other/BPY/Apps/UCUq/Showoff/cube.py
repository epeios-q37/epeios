import math

WIDTH_ = 128
HEIGHT_ = 64


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


def draw3DCube(oled, x, y, z):
  """
  x = alpha (0–360°)  → yaw
  y = beta  (-180–180°) → pitch
  z = gamma (-90–90°) → roll
  """
  yaw   = -x
  pitch = -y
  roll  = -z

  oled.fill(0)

  projected = []
  for (vx, vy, vz) in cubeVertices_:
    xr, yr, zr = rotatePoint_(vx, vy, vz, pitch, roll, yaw)
    xp, yp = project_(xr, yr, zr)
    projected.append((xp, yp))

  for a, b in cubeEdges_:
    x0, y0 = projected[a]
    x1, y1 = projected[b]
    oled.line(x0, y0, x1, y1, 1)

