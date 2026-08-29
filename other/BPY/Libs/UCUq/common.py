import base64
import copy
import gzip
import inspect
import json
import math
import re
import string
import time
import zlib

import atlastk

ITEMS_ = "i_"

# Keys
K_DEVICE = "Device"
K_DEVICE_TOKEN = "Token"
K_DEVICE_ID = "Id"

DEMO_VTOKEN = "%DEMO_VTOKEN%"

FLASH_DELAY_ = 0

objectCounter_ = 0
device_ = None

####################################################################
##### Begin of reimplementation form MicroPython's framebuffer #####
####################################################################

MONO_VLSB = 0
MONO_HLSB = 1
MONO_HMSB = 2
RGB565 = 3
GS2_HMSB = 4
GS4_HMSB = 5
GS8 = 6

_FONT = bytes([
  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,  # 32=espace
  0x00, 0x00, 0x00, 0x4f, 0x4f, 0x00, 0x00, 0x00,  # 33=!
  0x00, 0x07, 0x07, 0x00, 0x00, 0x07, 0x07, 0x00,  # 34="
  0x14, 0x7f, 0x7f, 0x14, 0x14, 0x7f, 0x7f, 0x14,  # 35=#
  0x00, 0x24, 0x2e, 0x6b, 0x6b, 0x3a, 0x12, 0x00,  # 36=$
  0x00, 0x63, 0x33, 0x18, 0x0c, 0x66, 0x63, 0x00,  # 37=%
  0x00, 0x32, 0x7f, 0x4d, 0x4d, 0x77, 0x72, 0x50,  # 38=&
  0x00, 0x00, 0x00, 0x04, 0x06, 0x03, 0x01, 0x00,  # 39='
  0x00, 0x00, 0x1c, 0x3e, 0x63, 0x41, 0x00, 0x00,  # 40=(
  0x00, 0x00, 0x41, 0x63, 0x3e, 0x1c, 0x00, 0x00,  # 41=)
  0x08, 0x2a, 0x3e, 0x1c, 0x1c, 0x3e, 0x2a, 0x08,  # 42=*
  0x00, 0x08, 0x08, 0x3e, 0x3e, 0x08, 0x08, 0x00,  # 43=+
  0x00, 0x00, 0x80, 0xe0, 0x60, 0x00, 0x00, 0x00,  # 44=,
  0x00, 0x08, 0x08, 0x08, 0x08, 0x08, 0x08, 0x00,  # 45=-
  0x00, 0x00, 0x00, 0x60, 0x60, 0x00, 0x00, 0x00,  # 46=.
  0x00, 0x40, 0x60, 0x30, 0x18, 0x0c, 0x06, 0x02,  # 47=/
  0x00, 0x3e, 0x7f, 0x49, 0x45, 0x7f, 0x3e, 0x00,  # 48=0
  0x00, 0x40, 0x44, 0x7f, 0x7f, 0x40, 0x40, 0x00,  # 49=1
  0x00, 0x62, 0x73, 0x51, 0x49, 0x4f, 0x46, 0x00,  # 50=2
  0x00, 0x22, 0x63, 0x49, 0x49, 0x7f, 0x36, 0x00,  # 51=3
  0x00, 0x18, 0x18, 0x14, 0x16, 0x7f, 0x7f, 0x10,  # 52=4
  0x00, 0x27, 0x67, 0x45, 0x45, 0x7d, 0x39, 0x00,  # 53=5
  0x00, 0x3e, 0x7f, 0x49, 0x49, 0x7b, 0x32, 0x00,  # 54=6
  0x00, 0x03, 0x03, 0x79, 0x7d, 0x07, 0x03, 0x00,  # 55=7
  0x00, 0x36, 0x7f, 0x49, 0x49, 0x7f, 0x36, 0x00,  # 56=8
  0x00, 0x26, 0x6f, 0x49, 0x49, 0x7f, 0x3e, 0x00,  # 57=9
  0x00, 0x00, 0x00, 0x24, 0x24, 0x00, 0x00, 0x00,  # 58=:
  0x00, 0x00, 0x80, 0xe4, 0x64, 0x00, 0x00, 0x00,  # 59=;
  0x00, 0x08, 0x1c, 0x36, 0x63, 0x41, 0x41, 0x00,  # 60=<
  0x00, 0x14, 0x14, 0x14, 0x14, 0x14, 0x14, 0x00,  # 61==
  0x00, 0x41, 0x41, 0x63, 0x36, 0x1c, 0x08, 0x00,  # 62=>
  0x00, 0x02, 0x03, 0x51, 0x59, 0x0f, 0x06, 0x00,  # 63=?
  0x00, 0x3e, 0x7f, 0x41, 0x4d, 0x4f, 0x2e, 0x00,  # 64=@
  0x00, 0x7c, 0x7e, 0x0b, 0x0b, 0x7e, 0x7c, 0x00,  # 65=A
  0x00, 0x7f, 0x7f, 0x49, 0x49, 0x7f, 0x36, 0x00,  # 66=B
  0x00, 0x3e, 0x7f, 0x41, 0x41, 0x63, 0x22, 0x00,  # 67=C
  0x00, 0x7f, 0x7f, 0x41, 0x63, 0x3e, 0x1c, 0x00,  # 68=D
  0x00, 0x7f, 0x7f, 0x49, 0x49, 0x41, 0x41, 0x00,  # 69=E
  0x00, 0x7f, 0x7f, 0x09, 0x09, 0x01, 0x01, 0x00,  # 70=F
  0x00, 0x3e, 0x7f, 0x41, 0x49, 0x7b, 0x3a, 0x00,  # 71=G
  0x00, 0x7f, 0x7f, 0x08, 0x08, 0x7f, 0x7f, 0x00,  # 72=H
  0x00, 0x00, 0x41, 0x7f, 0x7f, 0x41, 0x00, 0x00,  # 73=I
  0x00, 0x20, 0x60, 0x41, 0x7f, 0x3f, 0x01, 0x00,  # 74=J
  0x00, 0x7f, 0x7f, 0x1c, 0x36, 0x63, 0x41, 0x00,  # 75=K
  0x00, 0x7f, 0x7f, 0x40, 0x40, 0x40, 0x40, 0x00,  # 76=L
  0x00, 0x7f, 0x7f, 0x06, 0x0c, 0x06, 0x7f, 0x7f,  # 77=M
  0x00, 0x7f, 0x7f, 0x0e, 0x1c, 0x7f, 0x7f, 0x00,  # 78=N
  0x00, 0x3e, 0x7f, 0x41, 0x41, 0x7f, 0x3e, 0x00,  # 79=O
  0x00, 0x7f, 0x7f, 0x09, 0x09, 0x0f, 0x06, 0x00,  # 80=P
  0x00, 0x1e, 0x3f, 0x21, 0x61, 0x7f, 0x5e, 0x00,  # 81=Q
  0x00, 0x7f, 0x7f, 0x19, 0x39, 0x6f, 0x46, 0x00,  # 82=R
  0x00, 0x26, 0x6f, 0x49, 0x49, 0x7b, 0x32, 0x00,  # 83=S
  0x00, 0x01, 0x01, 0x7f, 0x7f, 0x01, 0x01, 0x00,  # 84=T
  0x00, 0x3f, 0x7f, 0x40, 0x40, 0x7f, 0x3f, 0x00,  # 85=U
  0x00, 0x1f, 0x3f, 0x60, 0x60, 0x3f, 0x1f, 0x00,  # 86=V
  0x00, 0x7f, 0x7f, 0x30, 0x18, 0x30, 0x7f, 0x7f,  # 87=W
  0x00, 0x63, 0x77, 0x1c, 0x1c, 0x77, 0x63, 0x00,  # 88=X
  0x00, 0x07, 0x0f, 0x78, 0x78, 0x0f, 0x07, 0x00,  # 89=Y
  0x00, 0x61, 0x71, 0x59, 0x4d, 0x47, 0x43, 0x00,  # 90=Z
  0x00, 0x00, 0x7f, 0x7f, 0x41, 0x41, 0x00, 0x00,  # 91=[
  0x00, 0x02, 0x06, 0x0c, 0x18, 0x30, 0x60, 0x40,  # 92=(backslash)
  0x00, 0x00, 0x41, 0x41, 0x7f, 0x7f, 0x00, 0x00,  # 93=]
  0x00, 0x08, 0x0c, 0x06, 0x06, 0x0c, 0x08, 0x00,  # 94=^
  0xc0, 0xc0, 0xc0, 0xc0, 0xc0, 0xc0, 0xc0, 0xc0,  # 95=_
  0x00, 0x00, 0x01, 0x03, 0x06, 0x04, 0x00, 0x00,  # 96=`
  0x00, 0x20, 0x74, 0x54, 0x54, 0x7c, 0x78, 0x00,  # 97=a
  0x00, 0x7f, 0x7f, 0x44, 0x44, 0x7c, 0x38, 0x00,  # 98=b
  0x00, 0x38, 0x7c, 0x44, 0x44, 0x6c, 0x28, 0x00,  # 99=c
  0x00, 0x38, 0x7c, 0x44, 0x44, 0x7f, 0x7f, 0x00,  # 100=d
  0x00, 0x38, 0x7c, 0x54, 0x54, 0x5c, 0x58, 0x00,  # 101=e
  0x00, 0x08, 0x7e, 0x7f, 0x09, 0x03, 0x02, 0x00,  # 102=f
  0x00, 0x98, 0xbc, 0xa4, 0xa4, 0xfc, 0x7c, 0x00,  # 103=g
  0x00, 0x7f, 0x7f, 0x04, 0x04, 0x7c, 0x78, 0x00,  # 104=h
  0x00, 0x00, 0x00, 0x7d, 0x7d, 0x00, 0x00, 0x00,  # 105=i
  0x00, 0x40, 0xc0, 0x80, 0x80, 0xfd, 0x7d, 0x00,  # 106=j
  0x00, 0x7f, 0x7f, 0x30, 0x38, 0x6c, 0x44, 0x00,  # 107=k
  0x00, 0x00, 0x41, 0x7f, 0x7f, 0x40, 0x00, 0x00,  # 108=l
  0x00, 0x7c, 0x7c, 0x18, 0x30, 0x18, 0x7c, 0x7c,  # 109=m
  0x00, 0x7c, 0x7c, 0x04, 0x04, 0x7c, 0x78, 0x00,  # 110=n
  0x00, 0x38, 0x7c, 0x44, 0x44, 0x7c, 0x38, 0x00,  # 111=o
  0x00, 0xfc, 0xfc, 0x24, 0x24, 0x3c, 0x18, 0x00,  # 112=p
  0x00, 0x18, 0x3c, 0x24, 0x24, 0xfc, 0xfc, 0x00,  # 113=q
  0x00, 0x7c, 0x7c, 0x04, 0x04, 0x0c, 0x08, 0x00,  # 114=r
  0x00, 0x48, 0x5c, 0x54, 0x54, 0x74, 0x20, 0x00,  # 115=s
  0x04, 0x04, 0x3f, 0x7f, 0x44, 0x64, 0x20, 0x00,  # 116=t
  0x00, 0x3c, 0x7c, 0x40, 0x40, 0x7c, 0x3c, 0x00,  # 117=u
  0x00, 0x1c, 0x3c, 0x60, 0x60, 0x3c, 0x1c, 0x00,  # 118=v
  0x00, 0x1c, 0x7c, 0x30, 0x18, 0x30, 0x7c, 0x1c,  # 119=w
  0x00, 0x44, 0x6c, 0x38, 0x38, 0x6c, 0x44, 0x00,  # 120=x
  0x00, 0x9c, 0xbc, 0xa0, 0xa0, 0xfc, 0x7c, 0x00,  # 121=y
  0x00, 0x44, 0x64, 0x74, 0x5c, 0x4c, 0x44, 0x00,  # 122=z
  0x00, 0x08, 0x08, 0x3e, 0x77, 0x41, 0x41, 0x00,  # 123={
  0x00, 0x00, 0x00, 0xff, 0xff, 0x00, 0x00, 0x00,  # 124=|
  0x00, 0x41, 0x41, 0x77, 0x3e, 0x08, 0x08, 0x00,  # 125=}
  0x00, 0x02, 0x03, 0x01, 0x03, 0x02, 0x03, 0x01,  # 126=~
  0xaa, 0x55, 0xaa, 0x55, 0xaa, 0x55, 0xaa, 0x55,  # 127
])


def _mono_vlsb_set(fb, x, y, c):
  index = (y >> 3) * fb.stride + x
  offset = y & 0x07
  fb.buf[index] = (fb.buf[index] & ~(1 << offset) & 0xFF) | ((c & 1) << offset)


def _mono_vlsb_get(fb, x, y):
  index = (y >> 3) * fb.stride + x
  offset = y & 0x07
  return (fb.buf[index] >> offset) & 1


def _mono_hlsb_set(fb, x, y, c):
  index = (x + y * fb.stride) >> 3
  offset = 7 - (x & 7)
  fb.buf[index] = (fb.buf[index] & ~(1 << offset) & 0xFF) | ((c & 1) << offset)


def _mono_hlsb_get(fb, x, y):
  index = (x + y * fb.stride) >> 3
  offset = 7 - (x & 7)
  return (fb.buf[index] >> offset) & 1


def _mono_hmsb_set(fb, x, y, c):
  index = (x + y * fb.stride) >> 3
  offset = x & 7
  fb.buf[index] = (fb.buf[index] & ~(1 << offset) & 0xFF) | ((c & 1) << offset)


def _mono_hmsb_get(fb, x, y):
  index = (x + y * fb.stride) >> 3
  offset = x & 7
  return (fb.buf[index] >> offset) & 1


def _rgb565_set(fb, x, y, c):
  index = (x + y * fb.stride) * 2
  fb.buf[index] = c & 0xFF
  fb.buf[index + 1] = (c >> 8) & 0xFF


def _rgb565_get(fb, x, y):
  index = (x + y * fb.stride) * 2
  return fb.buf[index] | (fb.buf[index + 1] << 8)


def _gs2_hmsb_set(fb, x, y, c):
  index = (x + y * fb.stride) >> 2
  shift = 6 - 2 * (x & 3)
  mask = 0x03 << shift
  fb.buf[index] = (fb.buf[index] & ~mask & 0xFF) | ((c & 0x03) << shift)


def _gs2_hmsb_get(fb, x, y):
  index = (x + y * fb.stride) >> 2
  shift = 6 - 2 * (x & 3)
  return (fb.buf[index] >> shift) & 0x03


def _gs4_hmsb_set(fb, x, y, c):
  index = (x + y * fb.stride) >> 1
  if (x & 1) == 0:
    fb.buf[index] = (fb.buf[index] & 0x0F) | ((c & 0x0F) << 4)
  else:
    fb.buf[index] = (fb.buf[index] & 0xF0) | (c & 0x0F)


def _gs4_hmsb_get(fb, x, y):
  index = (x + y * fb.stride) >> 1
  if (x & 1) == 0:
    return (fb.buf[index] >> 4) & 0x0F
  return fb.buf[index] & 0x0F


def _gs8_set(fb, x, y, c):
  fb.buf[x + y * fb.stride] = c & 0xFF


def _gs8_get(fb, x, y):
  return fb.buf[x + y * fb.stride]


_OPS = {
  MONO_VLSB: (_mono_vlsb_set, _mono_vlsb_get),
  MONO_HLSB: (_mono_hlsb_set, _mono_hlsb_get),
  MONO_HMSB: (_mono_hmsb_set, _mono_hmsb_get),
  RGB565: (_rgb565_set, _rgb565_get),
  GS2_HMSB: (_gs2_hmsb_set, _gs2_hmsb_get),
  GS4_HMSB: (_gs4_hmsb_set, _gs4_hmsb_get),
  GS8: (_gs8_set, _gs8_get),
}


class FrameBuffer:
  def __init__(self, buffer, width, height, format, stride=None):
    if format not in _OPS:
      raise ValueError("format de pixel inconnu")
    self.buf = buffer
    self.width = width
    self.height = height
    self.format = format
    self.stride = width if stride is None else stride
    self._set, self._get = _OPS[format]

  def pixel(self, x, y, c=None):
    if x < 0 or x >= self.width or y < 0 or y >= self.height:
      return None
    if c is None:
      return self._get(self, x, y)
    self._set(self, x, y, c)
    return None

  def fill(self, c):
    self.fill_rect(0, 0, self.width, self.height, c)

  def fill_rect(self, x, y, w, h, c):
    if w < 1 or h < 1 or x + w <= 0 or y + h <= 0 or x >= self.width or y >= self.height:
      return
    xend = min(self.width, x + w)
    yend = min(self.height, y + h)
    x = max(x, 0)
    y = max(y, 0)
    set_ = self._set
    for yy in range(y, yend):
      for xx in range(x, xend):
        set_(self, xx, yy, c)

  def hline(self, x, y, w, c):
    self.fill_rect(x, y, w, 1, c)

  def vline(self, x, y, h, c):
    self.fill_rect(x, y, 1, h, c)

  def rect(self, x, y, w, h, c, f=False):
    if w < 1 or h < 1:
      return
    if f:
      self.fill_rect(x, y, w, h, c)
    else:
      self.fill_rect(x, y, w, 1, c)
      self.fill_rect(x, y + h - 1, w, 1, c)
      self.fill_rect(x, y, 1, h, c)
      self.fill_rect(x + w - 1, y, 1, h, c)

  def line(self, x0, y0, x1, y1, c):
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    x, y = x0, y0
    while True:
      FrameBuffer.pixel(self, x, y, c)
      if x == x1 and y == y1:
        break
      e2 = 2 * err
      if e2 >= dy:
        err += dy
        x += sx
      if e2 <= dx:
        err += dx
        y += sy

  def ellipse(self, cx, cy, xr, yr, c, f=False, m=0x0F):
    if xr <= 0 or yr <= 0:
      return
    for dy in range(-yr, yr + 1):
      # bornes de l'ellipse sur cette ligne horizontale
      ratio = dy / yr
      span = xr * (1 - ratio * ratio) ** 0.5
      if dy <= 0:
        quad_right, quad_left = 0x01, 0x02  # Q1, Q2
      else:
        quad_right, quad_left = 0x08, 0x04  # Q4, Q3

      if f:
        if m & quad_right:
          FrameBuffer.hline(self, cx, cy + dy, int(round(span)) + 1, c)
        if m & quad_left:
          FrameBuffer.hline(self, cx - int(round(span)), cy + dy, int(round(span)) + 1, c)
      else:
        xi = int(round(span))
        if m & quad_right:
          FrameBuffer(self, cx + xi, cy + dy, c)
        if m & quad_left:
          FrameBuffer.pixel(self, cx - xi, cy + dy, c)

  def poly(self, x, y, coords, c, f=False):
    n = len(coords) // 2
    if n < 2:
      return
    pts = [(x + coords[2 * i], y + coords[2 * i + 1]) for i in range(n)]
    if f:
      self._fill_poly(pts, c)
    else:
      for i in range(n):
        x0, y0 = pts[i]
        x1, y1 = pts[(i + 1) % n]
        FrameBuffer.line(self,x0, y0, x1, y1, c)

  def _fill_poly(self, pts, c):
    n = len(pts)
    ys = [p[1] for p in pts]
    ymin, ymax = min(ys), max(ys)
    for yy in range(ymin, ymax + 1):
      xs = []
      for i in range(n):
        x0, y0 = pts[i]
        x1, y1 = pts[(i + 1) % n]
        if y0 == y1:
          continue
        if min(y0, y1) <= yy < max(y0, y1):
          t = (yy - y0) / (y1 - y0)
          xs.append(x0 + t * (x1 - x0))
      xs.sort()
      for i in range(0, len(xs) - 1, 2):
        xstart = int(round(xs[i]))
        xend = int(round(xs[i + 1]))
        FrameBuffer.hline(self, xstart, yy, max(xend - xstart, 1), c)

  def text(self, s, x, y, c=1):
    for i, ch in enumerate(s):
      self._draw_char(ch, x + i * 8, y, c)

  def _draw_char(self, ch, x, y, c):
    o = ord(ch)
    if o < 32 or o > 127:
      return
    offset = (o - 32) * 8
    glyph = _FONT[offset:offset + 8]
    for col in range(8):
      byte = glyph[col]
      if byte == 0:
        continue
      for row in range(8):
        if byte & (1 << row):
          FrameBuffer.pixel(self, x + col, y + row, c)

  def scroll(self, xstep, ystep):
    if xstep < 0:
      sx, xend, dx = 0, self.width + xstep, 1
    else:
      sx, xend, dx = self.width - 1, xstep - 1, -1
    if ystep < 0:
      sy, yend, dy = 0, self.height + ystep, 1
    else:
      sy, yend, dy = self.height - 1, ystep - 1, -1

    y = sy
    while y != yend:
      x = sx
      while x != xend:
        src = FrameBuffer.pixel(self, x - xstep, y - ystep)
        if src is not None:
          FrameBuffer.pixel(self, x, y, src)
        x += dx
      y += dy

  def blit(self, fbuf, x, y, key=-1, palette=None):
    for j in range(fbuf.height):
      yy = y + j
      if yy < 0 or yy >= self.height:
        continue
      for i in range(fbuf.width):
        xx = x + i
        if xx < 0 or xx >= self.width:
          continue
        src = fbuf.pixel(i, j)
        if src == key:
          continue
        if palette is not None:
          src = palette.pixel(src, 0)
        FrameBuffer.pixel(self, xx, yy, src)

##################################################################
##### End of reimplementation form MicroPython's framebuffer #####
##################################################################


def unpack_(data):
  return zlib.decompress(base64.b64decode(data)).decode()


def getObjectIndice():
  global objectCounter_

  objectCounter_ += 1

  return objectCounter_


def getObject_(id):
  return f"{ITEMS_}[{id}]"


def displayMissingConfigMessage_():
  displayExitMessage_(  # noqa: F821
    "Please launch the 'Config' app first to set the device to use!"
  )


def handleConfig_():
  if not CONFIG_:  # noqa: F821
    return "", ""

  if K_DEVICE not in CONFIG_:  # noqa: F821
    displayMissingConfigMessage_()

  device = CONFIG_[K_DEVICE]  # noqa: F821

  if K_DEVICE_TOKEN not in device:
    displayMissingConfigMessage_()

  token = device[K_DEVICE_TOKEN]

  if K_DEVICE_ID not in device:
    displayMissingConfigMessage_()

  id = device[K_DEVICE_ID]

  return token, id


def _getConfigToken_(): # deprecated
  try:
    return CONFIG_[K_DEVICE][K_DEVICE_TOKEN]  # noqa: F821
  except:
    return ""


def setDevice(tokenId=None, *, device=None):
  if device != None:
    global device_
    if tokenId:
      raise ValueError("'device' and tokenIid' can not set together!")
    device_ = device
  else:
    getDevice(tokenId=tokenId)


# Infos keys and subkeys
IK_DEVICE_ID_ = "DeviceId"
IK_DEVICE_UNAME_ = "uname"
IK_HARDWARE = "Hardware"
IK_FEATURES = "Features"
IK_KIT_LABEL = "KitLabel"

# Kits keys
IK_BRAND_ = "brand"
IK_MODEL_ = "model"
IK_VARIANT_ = "variant"

SLEEP_WAIT_SCRIPT_ = """
def sleepWait(start, us):
  elapsed = time.ticks_us() - start
            
  if elapsed < us:
    time.sleep_us(int(us - elapsed))
"""

INFO_SCRIPT_ = f"""
def ucuqStructToDict(obj):
  return {{attr: getattr(obj, attr) for attr in dir(obj) if not attr.startswith('__')}}

def ucuqGetInfos():
  infos = {{
  "{IK_DEVICE_ID_}": ucuq.settings.getDeviceId(),
  "{IK_DEVICE_UNAME_}": ucuqStructToDict(__import__('uos').uname())
  }}

  if kit := ucuq.settings.getKitLabel():
    infos["{IK_KIT_LABEL}"] = kit

  return infos
"""

# NOTA: Wokwi works only with PWM freq of 50 Hz !
WOKWI_KIT_PATCH_SCRIPT_ = f"""
try:
  with open("diagram.json") as f:
    content = f.read()
  assert '"editor"' in content
  assert '"editor": "wokwi"' in content
  CONV_ = {tuple(int(255 * math.log(1+i) / math.log(32)) for i in range(32))}
  def wc_(color):
    return tuple(CONV_[min(color[i],31)] for i in range(3))
  def sp_(pin):
    return pin if pin >= 2 else pin + 2
  def su_(u16):
    return 9830 - u16
  def sn_(ns):
    return 3 - ns
except (OSError, AssertionError):
  def wc_(color):
    return color
  def sp_(pin):
    return pin
  def su_(u16):
    return u16
  def sn_(ns):
    return ns
"""


ATK_BODY_ = (
  """
<style>
  .ucuq {
    max-height: 200px;
    overflow: hidden;
    opacity: 1;
    animation: ucuqFadeOut 2s forwards;
  }

  @keyframes ucuqFadeOut {
  0% {
    max-height: 200px;
  }
  100% {
    max-height: 0;
  }
}
</style>
<div style="display: flex; justify-content: center;" class="ucuq">
  <h3>'BRACES' (<em>BRACES</em>)</h3>
</div>
<div id="ucuq_body" style_="display: flex; justify-content: center;">
</div>
""".replace(
    "{", "{{"
  )
  .replace("}", "}}")
  .replace("BRACES", "{}")
)


ATK_XDEVICE_ = """
<dialog id="ucuq_xdevice" style="width: min-content;">
  <fieldset>
    <legend>Device</legend>
    <label style="display: flex; justify-content: space-between; margin: 5px;">
      <span>Token:&nbsp;</span>
      <input id="ucuq_xdevice_token">
    </label>
    <label style="display: flex; justify-content: space-between; margin: 5px;">
      <span>Id:&nbsp;</span>
      <input id="ucuq_xdevice_id">
    </label>
  </fieldset>
  <div style="display: flex; justify-content: space-around; margin: 5px;">
    <button xdh:onevent="ucuq_xdevice_ok"/>{}</button>
    <button xdh:onevent="ucuq_xdevice_cancel">{}</button>
  </div>
  <fieldset>{}</fieldset>
</dialog>
"""

UCUQ_XDEVICE_ACTION_ = "UCUqXDevice"


async def handleXDevice_(dom, response):
  await dom.executeVoid("document.getElementById('ucuq_xdevice').close();")

  if response:
    await atlastk.getUserGlobals()["UCUqXDevice"](
      dom,
      Device(
        id=await dom.getValue("ucuq_xdevice_id"),
        token=await dom.getValue("ucuq_xdevice_token"),
      ),
    )

  await dom.executeVoid("element = document.getElementById('ucuq_xdevice').remove();")


def getDOM_(dom1, dom2):
  if isinstance(dom1, atlastk.DOM):
    return dom1
  else:
    return dom2


UCUQ_XDEVICE_I10N = (
  ("OK", "Cancel", "Click on ‘Cancel’ unless you know exactly what you're doing!"),
  (
    "OK",
    "Annuler",
    "Cliquez sur 'Annuler' à moins que vous ne sachiez exactement ce que vous faites !",
  ),
)


async def handleXDeviceRetrieving_(dom1, dom2):
  dom = getDOM_(dom1, dom2)

  language = dom.language

  i10n = UCUQ_XDEVICE_I10N[
    1 if (language[:2].upper() if len(language) >= 2 else "") == "FR" else 0
  ]

  await dom.end("", ATK_XDEVICE_.format(*i10n))

  atlastk.setCallback("ucuq_xdevice_ok", handleXDeviceOK_)
  atlastk.setCallback("ucuq_xdevice_cancel", handleXDeviceCancel_)

  await dom.executeVoid("document.getElementById('ucuq_xdevice').showModal();")


async def handleXDeviceOK_(dom1, dom2):
  await handleXDevice_(getDOM_(dom1, dom2), True)


async def handleXDeviceCancel_(dom1, dom2):
  await handleXDevice_(getDOM_(dom1, dom2), False)


CB_AUTO = 0
CB_MANUAL = 1

defaultCommitBehavior_ = CB_AUTO


def testCommit_(commit, behavior=None):
  if commit is None:
    if behavior is None:
      behavior = defaultCommitBehavior_

    return behavior == CB_AUTO
  else:
    return commit


def sleepStart():
  return getDevice().sleepStart()


def sleepWait(secs):
  return getDevice().sleepWait(secs)


def sleep(secs):
  return getDevice().sleep(secs)


def patchKeys_(keys):
  return keys if keys else []

B_LCD = "LCD"
B_OLED = "OLED"
B_BUZZER = "Buzzer"
B_LOUDSPEAKER = "Loudspeaker"
RING = "Ring"
B_MATRIX = "Matrix"
B_TFT = "TFT"


class Auto:
  def __new__(cls, bit, infos, item, hardwareKeys, featuresKeys, **kwargs):
    hardware = getKitHardware_(infos)
    features = getKitFeatures_(infos)

    if not hasHardware_(hardware, item) and not hasFeatures_(features, item):
      return Nothing()

    hardwareKeys = patchKeys_(hardwareKeys)
    featuresKeys = patchKeys_(featuresKeys)

    return bit(
      *getDescItems_(features, item, featuresKeys),
      *getDescItems_(hardware, item, hardwareKeys),
      **kwargs,
    )


def getBits(infos, *bitLabels, device=None):
  bits = [getDevice(device=device)]

  for label in bitLabels:
    match label:
      case "LCD":
        bits.append(
          Auto(
            HD44780_I2C,
            infos,
            label,
            None,
            ["Width", "Height"],
            i2c=Auto(
              I2C,
              infos,
              label,
              ["SDA", "SCL", "Soft"],
              None,
              device=device,
            ),
          )
        )
      case "OLED":
        bits.append(
          Auto(
            OLED_I2C,
            infos,
            label,
            None,
            ["Driver", "Width", "Height"],
            i2c=Auto(
              I2C,
              infos,
              label,
              ["SDA", "SCL", "Soft"],
              None,
              device=device,
            ),
          )
        )
      case "Buzzer" | "Loudspeaker":
        bits.append(Auto(PWM, infos, label, ["Pin"], None, device=device))
      case "Ring":
        bits.append(
          Auto(WS2812, infos, label, ["Pin"], ["Count"], device=device)
        )
      case "Matrix":
        bits.append(
          Auto(
            HT16K33,
            infos,
            label,
            None,
            None,
            i2c=Auto(
              I2C,
              infos,
              "Matrix",
              ["SDA", "SCL", "Soft"],
              None,
              device=device,
            ),
          )
        )
      case "TFT":
        bits.append(
          Auto(
            ILI9341,
            infos,
            label,
            ["DC", "CS", "RST"],
            ["Width", "Height", "Rotation"],
            spi=Auto(
              SPI,
              infos,
              label,
              ["Id", "SCK", "MOSI", "MISO", "Baudrate"],
              None,
              device=device,
            ),
          )
        )
      case _:
        raise Exception(f"Unknown bit label: {label}")

  return bits


class Multi:
  def __init__(self, object = None):
    self.objects_ = []

    if object is not None:
      self.add(object)

  def add(self, object):
    self.objects_.append(object)
    
  def __len__(self):
    return len(self.objects_)

  def __getattr__(self, methodName):
    def wrapper(*args, **kwargs):
      for object in self.objects_:
        if hasattr(object, "__getattr__"):
          returned = object.__getattr__(methodName)(*args, **kwargs)
        else:
          returned = getattr(object, methodName)(*args, **kwargs)
      if type(returned) is type(object):
        returned = self
      return returned

    return wrapper

  def __getitem__(self, index):
    if index < len(self.objects_):
      return self.objects_[index]
    else:
      raise IndexError("Index out of range for Multi object.")
    
  def __setitem__(self, index, value):
    for object in self.objects_:
      object.__setitem__(index, value)
    
  def index(self, object):
    return self.objects_.index(object)
    
  def getObjects(self):
    return self.objects_

  # Workaround for Brython (https://github.com/brython-dev/brython/issues/2590)
  def __bool__(self):
    return True


def testRawId_(rawId):
  return set(rawId) <= set(string.ascii_letters + string.digits + "-_:")


def parseRawIds_(defaultToken, rawIds):
  items = []

  for rawId in rawIds.split():
    if not testRawId_(rawId):
        raise ValueError(f"Misformed id: '{rawId}'!")

    match rawId.split(':'):
      case [token, id]:
        items.append((token, id))
      case [id]:
        items.append((id,))
      case _:
        raise ValueError(f"Misformed id: '{rawId}'!")


  token = defaultToken

  tokenIds = []

  for item in items:
    if len(item) == 1:
      tokenIds.append(TokenId_(token, item[0]))
    elif not item[0] and not item[1]:
      token = defaultToken
    elif not item[0]:
      tokenIds.append(TokenId_(defaultToken, item[1]))
    elif not item[1]:
      token = item[0]
    else:
      tokenIds.append(TokenId_(item[0], item[1]))
      
  return tokenIds


class TokenId_:
  def __init__(self, token ,id):
    self.token = token
    self.id = id


class Device(Device_):  # noqa: F821
  def __new__(cls, tokenIds = None, *, callback=None):
    token, configRawIds = handleConfig_()

    if not tokenIds:
      tokenIds = configRawIds

    if isinstance(tokenIds, TokenId_):
      tokenIds = (tokenIds,)
    if not isinstance(tokenIds, (tuple, list)):
      tokenIds = parseRawIds_(token, tokenIds)

    match len(tokenIds):
      case 0:
        displayMissingConfigMessage_()
      case 1:
        tokenId = tokenIds[0]

        if not tokenId.token:
          displayMissingConfigMessage_()

        instance = object.__new__(Device)
        instance.__init__(tokenId, callback=callback)
        return instance
      case _:
        multi = Multi()

        for tokenId in tokenIds:
          multi.add(Device(tokenIds=tokenId, callback=callback))
        
        return multi
        
  def __init__(self, tokenIds=None, *, rawIds=None, callback=None):
    if rawIds:
      raise ValueError("'rawIds' can not be set !")

    if not isinstance(tokenIds, TokenId_):
      return  # method already called by '__new__'.
    
    self.pendingModules_ = ["Init-1"]
    self.handledModules_ = []
    self.commands_ = []
    self.commitBehavior_ = None
    self.timer_ = None

    super().__init__(id=tokenIds.id, token=tokenIds.token, callback=callback)

    for script in START_SCRIPTS_:
      self.addCommand(script)

  def __del__(self):
    try:
      self.commit()
    except:
      pass

  def testCommit_(self, commit):
    return testCommit_(commit, self.commitBehavior_)

  def addModule(self, module):
    if module not in self.pendingModules_ and module not in self.handledModules_:
      self.pendingModules_.append(module)

    return self

  def addModules(self, modules):
    if isinstance(modules, str):
      self.addModule(modules)
    else:
      for module in modules:
        self.addModule(module)

    return self

  def addCommand(self, command, commit=None):
    self.commands_.append(command)

    if self.testCommit_(commit):
      self.commit()

    return self

  def sleepStart(self):
    if self.timer_ is None:
      self.timer_ = getObjectIndice()

    self.addCommand(f"{getObject_(self.timer_)} = time.ticks_us()")

    return id

  def sleepWait(self, secs):
    if self.timer_ is None:
      raise Exception("'sleepWait' called before 'sleepStart'!")
      
    self.addCommand(f"sleepWait({getObject_(self.timer_)}, {secs * 1000000})")

  def sleep(self, secs):
    self.addCommand(f"time.sleep_us({int(secs * 1_000_000)})")
    
  def ntpSetTime(self):
    self.addCommand("ntp_set_time()")
    
  def ntpSleepUntil(self, timestamp):
    # self.addCommand(f"sleep_until_us({timestamp})")
    self.addCommand(f"time.sleep_us({int(timestamp * 1_000_000)} - precise_time_us())")
    
  def ntpSleep(self, delay):
    self.addCommand(f"time.sleep_us({int(delay * 1_000_000)})")
    
  async def ntpTimeAwait(self):
    return self.commitAwait("precise_time_us()") / 1_000_000
    


async def getBaseInfosAwait_(device=None):
  device = getDevice(device=device)

  device.addCommand(INFO_SCRIPT_, False)

  return await device.commitAwait("ucuqGetInfos()")


def getKitFromDeviceId_(deviceId):
  for kit in KITS_:  # noqa: F821
    if "devices" in kit and deviceId in kit["devices"]:
      return kit
  else:
    return None


buildKitLabel_ = lambda brand, model, variant: f"{brand}/{model}/{variant}"


def getKitLabelFromDeviceId_(deviceId):
  kit = getKitFromDeviceId_(deviceId)

  if kit:
    return buildKitLabel_(kit[IK_BRAND_], kit[IK_MODEL_], kit[IK_VARIANT_])
  else:
    return "Undefined"


def getKitFromLabel_(label):
  brand, model, variant = label.split("/")

  for kit in KITS_:  # noqa: F821
    if (
      kit["brand"] == brand
      and kit["model"] == model
      and kit["variant"] == variant
    ):
      return kit
  else:
    return None


def getKitLabel(infos):
  return infos[IK_KIT_LABEL]


def getKit_(infosOrLabel):
  if type(infosOrLabel) != str:
    infosOrLabel = getKitLabel(infosOrLabel)

  return getKitFromLabel_(infosOrLabel)


def getKitDesc_(infosOrLabel, descLabel):
  kit = getKit_(infosOrLabel)

  if kit:
    return kit[descLabel]
  else:
    return "Undefined"


def getKitHardware_(infosOrLabel):
  return getKitDesc_(infosOrLabel, "hardware")


def getKitFeatures_(infosOrLabel):
  return getKitDesc_(infosOrLabel, "features")


subGetDescItems_ = lambda desc, key, index: (
  desc[key][index] if key in desc and index < len(desc[key]) else None
)


def getDescItems_(kitDesc, stringOrList, keys=None, *, index=0):
  if type(stringOrList) == str:
    items = subGetDescItems_(kitDesc, stringOrList, index)
  else:
    for key in stringOrList:
      if items := subGetDescItems_(kitDesc, key, index):
        break

  if items and (keys or keys == []):
    result = tuple(
      items[keys] if type(keys) == str else (items[key] for key in keys)
    )
  elif items:
    result = items
  else:
    result = ()

  return result


def hasHardware_(kitHardware, item):
  return bool(getDescItems_(kitHardware, item))


def hasFeatures_(kitFeatures, item):
  return bool(getDescItems_(kitFeatures, item))


def getFeatures(infosOrLabel, item, keys=None, *, index=0):
  kitFeatures = getKitFeatures_(infosOrLabel)

  if not kitFeatures:
    return ()

  return getDescItems_(kitFeatures, item, keys, index=index)


def getHardware(infosOrLabel, item, keys=None, *, index=0):
  kitHardware = getKitHardware_(infosOrLabel)

  if not kitHardware:
    return ()

  return getDescItems_(kitHardware, item, keys, index=index)


def getDeviceId(infos):
  return infos[IK_DEVICE_ID_]


async def getInfosAwait(device):
  infos = await getBaseInfosAwait_(device)

  if not IK_KIT_LABEL in infos:
    infos[IK_KIT_LABEL] = getKitLabelFromDeviceId_(getDeviceId(infos))
  infos[IK_HARDWARE] = getKitDesc_(infos, "hardware")
  infos[IK_FEATURES] = getKitDesc_(infos, "features")

  return infos


async def ATKConnectAwait(dom, body, *, target="", device=None):
  await getKitsAwait()  # noqa: F821

  if not KITS_:  # noqa: F821
    raise Exception("No kits defined!")

  await dom.inner(
    target,
    """
  <style>
  .ucuq-connection {
    display: inline-block;
    /* Pour éviter les retours à la ligne */
    white-space: nowrap;
    /* Pour que le texte ne déborde pas */
    overflow: hidden;
    /* Animation en continu */
    animation: ucuq-connection 1s linear infinite;
    /* Masque linéaire horizontal */
    -webkit-mask-image: linear-gradient(to right, transparent 0%, black 50%, transparent 100%);
    mask-image: linear-gradient(to right, transparent 0%, black 50%, transparent 100%);
    -webkit-mask-size: 200% 100%;
    mask-size: 200% 100%;
    -webkit-mask-position: 0% 0%;
    mask-position: 0% 0%;
  }

  @keyframes ucuq-connection {
    100% {
    -webkit-mask-position: 0% 0%;
    mask-position: 0% 0%;
    }
    50% {
    -webkit-mask-position: 100% 0%;
    mask-position: 100% 0%;
    }
    0% {
    -webkit-mask-position: 200% 0%;
    mask-position: 200% 0%;
    }
  }
  </style>
  <h2 class="ucuq-connection">💻…📡…🛰️…<span style='display: inline-block;transform: scaleX(-1)';>📡</span>…🤖</h2>
  """,
  )

  if device or CONFIG_:  # noqa: F821
    device = getDevice(device=device)

  if not device:
    await dom.inner(
      target, "<h3>ERROR: Please launch the 'Config' application!</h3>"
    )
    raise SystemExit("Unable to connect to a device!")

  setDevice(device=device)

  start = time.monotonic()
  infos = await getInfosAwait(device)

  if (elapsed := time.monotonic() - start) < 3:
    await sleepAwait(3 - elapsed)  # noqa: F821

  deviceId = getDeviceId(infos)

  await dom.inner(target, ATK_BODY_.format(infos[IK_KIT_LABEL], deviceId))

  await dom.inner("ucuq_body", body)

  await sleepAwait(1.5)  # noqa: F821

  await dom.inner(target, body)

  atlastk.setCallback(UCUQ_XDEVICE_ACTION_, handleXDeviceRetrieving_)

  return infos

def isDeviceAvailable():
  return device_ != None

def getDevice(*, tokenId=None, device=None):
  if device and tokenId:
    displayExitMessage_("'device' and 'tokenId' can not be set together with 'token' or 'id'!")  # type: ignore # noqa: F821

  if device is None:
    global device_

    if tokenId:
      device_ = Device(tokenId)
    elif device_ is None:
      device_ = Device()
    return device_
  else:
    return device


def addCommand(command, commit=False, /, device=None):
  getDevice(device=device).addCommand(command, commit)


# does absolutely nothing whichever method is called but returns 'self'.
# for the handling of the 'extra' parameter in the init method, which handles extra initialisation.
class Nothing:
  def __getattr__(self, name):
    def doNothing(*args, **kwargs):
      return self

    return doNothing

  def __bool__(self):
    return False

  def __len__(self):
    return 0
  
  def __getitem__(self, _):
    return self


# does absolutely nothing whichever method is called.
# 'if Nothing()' returns 'False'.
class Nothing_:
  def __init__(self, object):
    self.object = object

  def __getattr__(self, name):
    def doNothing(*args, **kwargs):
      return self.object

    return doNothing

  def __bool__(self):
    return False


class Core_:
  def __new__(cls, *kargs, **kwargs):
    if "device" not in kwargs or (devices := kwargs["device"]) is None :
      devices = getDevice()
    
    if type(devices) is Multi:
      if "device" in kwargs:
        kwargs.pop("device")
        
      multi = Multi()
      
      for device in devices:
        obj = object.__new__(cls)
        cls.__init__(obj, *kargs, **kwargs, **{"device": device})
        multi.add(obj)
        
      return multi
    else:
      obj = object.__new__(cls)
      cls.__init__(obj, *kargs, **kwargs) # TODO: '__init__' is called twice for object accessing
                                          # device through another object (servo, I2C-related objects… )
      return obj
  
  def __init__(self, device=None):
    self.id = None
    self.device_ = device

  def __del__(self):
    if self.id:
      self.addCommand(f"del {ITEMS_}[{self.id}]")

  def getDevice(self):
    return self.device_

  def getId(self):
    return self.id

  def init(self, modules, instanciation, device, extra, *, before=""):
    if self.device_:
      if device and device != self.device_:
        raise Exception("'device' already given!")
    else:
      self.device_ = getDevice(device=device)

    if modules:
      self.device_.addModules(modules)

    if before:
      self.addCommand(before)

    if instanciation:
      self.id = getObjectIndice()
      self.addCommand(f"{self.getObject()} = {instanciation}")

    return self if not isinstance(extra, bool) or extra else Nothing_(self)

  def getObject(self):
    return getObject_(self.id)

  def addCommand(self, command):
    self.device_.addCommand(command)
    return self

  def addMethods(self, methods):
    return self.addCommand(f"{self.getObject()}.{methods}")

  def callMethodAwait(self, method):
    return self.device_.commitAwait(f"{self.getObject()}.{method}")

  def sleepStart(self):
    return self.device_.sleepStart()

  def sleepWait(self, secs):
    self.device_.sleepWait(secs)
    return self

  def sleep(self, secs):
    self.device_.sleep(secs)
    return self
  
  def ntpSetTime(self):
    self.device_.ntpSetTime()
    return self
  
  def ntpSleepUntil(self, timestamp):
    self.device_.ntpSleepUntil(timestamp)
    return self
    
  def ntpSleep(self, delay):
    self.device_.ntpSleep(delay)
    return self
    
  def ntpTime(self):
    return self.device_.ntpTime()


class GPIO(Core_):
  def __init__(self, pin=None, device=None, extra=True):
    super().__init__(device)

    if pin:
      self.init(pin, device, extra)

  def init(self, pin, device=None, extra=True):
    self.pin = f'"{pin}"' if isinstance(pin, str) else pin

    super().init("GPIO-1", f"GPIO({self.pin})", device, extra)

  def high(self, value=True):
    return self.addMethods(f"high({value})")

  def low(self):
    return self.high(False)


class I2C_Core_(Core_):
  def __init__(self, sda=None, scl=None, soft=None, *, device=None):
    super().__init__(device)

    if sda == None != scl == None:
      raise Exception("None or both of sda/scl must be given!")
    elif sda != None:
      self.init(sda, scl, soft=soft, device=device)

  async def scanAwait(self):
    return await commitAwait(f"{self.getObject()}.scan()")  # noqa: F821


class I2C(I2C_Core_):
  def init(self, sda, scl, soft=None, *, device=None, extra=True):
    if soft == None:
      soft = False

    super().init(
      "I2C-1",
      f"machine.{'Soft' if soft else ''}I2C({'0,' if not soft else ''} sda=machine.Pin({sda}), scl=machine.Pin({scl}))",
      device=device,
      extra=extra,
    )


class SoftI2C(I2C):
  def init(self, sda, scl, *, soft=None, device=None):
    if soft == None:
      soft = True

    super().init(sda, scl, soft=soft, device=device)


class SPI(Core_):
  def __init__(
    self,
    id,
    sck=None,
    mosi=None,
    miso=None,
    baudrate=None,
    *,
    polarity=None,
    phase=None,
    bits=None,
    device=None,
  ):
    super().__init__(device)

    if sck == None != mosi == None or sck == None != miso == None:
      raise Exception("None or all of sck/ mosi/ miso must be given!")
    elif sck != None:
      self.init(
        id,
        sck,
        mosi,
        miso,
        baudrate=baudrate,
        polarity=polarity,
        phase=phase,
        bits=bits,
        device=device,
      )

  def init(
    self,
    id,
    sck=None,
    mosi=None,
    miso=None,
    baudrate=None,
    polarity=None,
    phase=None,
    bits=None,
    device=None,
    extra=True,
  ):
    super().init(
      None,
      f"machine.{'Soft' if not id else ''}SPI({str(id) + ', ' if id else ''}sck=machine.Pin({sck}){getParam_('mosi', mosi, 'machine.Pin({})')}{getParam_('miso', miso, 'machine.Pin({})')}{getParam_('baudrate', baudrate)}{getParam_('polarity', polarity)}{getParam_('phase', phase)}{getParam_('bits', bits)})",
      device=device,
      extra=extra,
    )


class SoftSPI(SPI):
  def __init__(
    self,
    sck,
    mosi,
    miso,
    *,
    id=None,
    baudrate=None,
    polarity=None,
    phase=None,
    bits=None,
    device=None,
  ):
    super().__init__(
      id,
      sck,
      mosi,
      miso,
      baudrate=baudrate,
      polarity=polarity,
      phase=phase,
      bits=bits,
      device=device,
    )


class WS2812(Core_):
  def __init__(self, n=None, pin=None, offset=0, device=None, extra=True):
    super().__init__(device)

    if (pin is None) != (n is None):
      raise Exception("Both or none of 'pin'/'n' must be given")

    if pin is not None:
      WS2812.init(self, n, pin, offset=offset, device=device, extra=extra)

  def init(self, n, pin, offset=0, device=None, extra=True):
    self.n_ = n
    self.offset_ = offset
    self.current_ = [(0,0,0)] * n
    self.new_ = [(0,0,0)] * n
    super().init(
      "WS2812-1", f"neopixel.NeoPixel(machine.Pin({pin}), {n})", device, extra
    ).flash(extra)

  def __len__(self):
    return self.n_
  
  def __getitem__(self, index):
    return self.new_[self.convert(index)]
  
  def __setitem__(self, index, value):
    self.new_[self.convert(index)] = value
    
  def getOffset(self):
    return self.offset_
  
  def getAll(self):
    return tuple(self.new_)
  
  async def straightLenAwait(self):
    return int(await self.callMethodAwait("__len__()"))
  
  def convert(self, index):
    return (index + self.offset_) % self.n_

  def setValue(self, index, value):
    self.new_[self.convert(index)] = tuple(value)
    return self
  
  def straightSetValue(self, index, val):
    self.setValue(index, val)
    return self.addMethods(f"__setitem__({self.convert(index)}, {json.dumps(val)})")
  
  def getValue(self, index):
    return self.new_[self.convert(index)]

  async def straightGetValueAwait(self, index):
    return await self.callMethodAwait(f"__getitem__({self.convert(index)})")
  
  def fill(self, val):
    self.new_ = [tuple(val)] * self.n_
    return self

  def straightFill(self, color, conv = lambda color : json.dumps(color)):
    self.fill(color)
    return self.addMethods(f"fill({conv(color)})")

  def straightWrite(self):
    self.current_ = copy.deepcopy(self.new_)
    return self.addMethods("write()")
  
  def write(self, conv = lambda color : json.dumps(color)):
    diffs = []
    same = self.new_[0]
    
    for i in range(len(self.new_)):
      if self.new_[i] != self.current_[i]:
        diffs.append((i,self.new_[i]))
        
      if same is not None and same != self.new_[i]:
        same = None
      
    if len(diffs):
      if same is not None:
        self.straightFill(same, conv)
      else:
        command = ""
        for diff in diffs:
#          command += f"{self.getObject()}.__setitem__({diff[0]},{conv(diff[1])})\n"
          command += f"{self.getObject()}[{diff[0]}]={conv(diff[1])}\n"
        self.addCommand(command)
      return self.straightWrite()
    else:
      return self

  def flash(self, extra=True):
    self.fill((255, 255, 255)).write()
    self.getDevice().sleep(FLASH_DELAY_ if isinstance(extra, bool) else extra)
    return self.fill((0, 0, 0)).write()
  

class HT16K33(Core_):
  def __init__(self, i2c=None, addr=None, extra=True):
    super().__init__()

    if i2c:
      self.init(i2c, addr=addr, extra=extra)

  def init(self, i2c, addr=None, extra=True):
    return (
      super()
      .init(
        "HT16K33-1",
        f"HT16K33({i2c.getObject()}, {addr})",
        i2c.getDevice(),
        extra,
      )
      .setBrightness(15)
      .flash(extra)
      .setBrightness(0)
    )

  def flash(self, extra=True):
    self.draw("ffffffffffffffffffffffffffffffff")
    self.getDevice().sleep(FLASH_DELAY_ if isinstance(extra, bool) else extra)
    return self.draw("")

  def setBlinkRate(self, rate):
    return self.addMethods(f"set_blink_rate({rate})")

  def setBrightness(self, brightness):
    return self.addMethods(f"set_brightness({brightness})")

  def clear(self):
    return self.addMethods(f"clear()")

  def draw(self, motif):
    return self.addMethods(f"clear().draw('{motif}').render()")

  def plot(self, x, y, ink=True):
    return self.addMethods(f"plot({x}, {y}, ink={1 if ink else 0})")

  def rect(self, x0, y0, x1, y1, ink=True):
    return self.addMethods(f"rect({x0}, {y0}, {x1}, {y1}, ink={1 if ink else 0})")

  def show(self):
    return self.addMethods("render()")


def getParam_(label, value, expr=None):
  if value:
    return f", {label} = {value if expr is None else expr.format(value)}"
  else:
    return ""


class PWM(Core_):
  def __init__(
    self, pin=None, *, freq=None, ns=None, u16=None, device=None, extra=True, convPin = lambda pin: pin, convU16 = lambda u16: u16, convNS = lambda ns : ns):
    super().__init__(device)

    if pin is not None:
      self.init(pin, freq=freq, u16=u16, ns=ns, device=device, extra=extra, convPin = convPin, convU16 = convU16, convNS = convNS)

  def init(self, pin, *, freq=None, u16=None, ns=None, device=None, extra=True, convPin = lambda pin: pin, convU16 = lambda u16: u16, convNS = lambda ns : ns):
    self.pin_ = pin
    command = f"machine.PWM(machine.Pin({convPin(pin)}, machine.Pin.OUT){getParam_('freq', freq)}{getParam_('duty_u16', u16)}{getParam_('duty_ns', ns)})"
    super().init("PWM-1", command, device, extra, before=f"{command}.deinit()")
    self.convU16_ = convU16
    self.convNS_ = convNS
    
  def GPIO(self):
    return GPIO(self.pin_)

  async def getU16Await(self):
    return int(await self.callMethodAwait("duty_u16()"))

  def setU16(self, u16):
    return self.addMethods(f"duty_u16({self.convU16_(u16)})")

  async def getNSAwait(self):
    return int(await self.callMethodAwait("duty_ns()"))

  def setNS(self, ns):
    return self.addMethods(f"duty_ns({self.convNS_(ns)})")

  async def getFreqAwait(self):
    return int(await self.callMethodAwait("freq()"))

  def setFreq(self, freq):
    return self.addMethods(f"freq({freq})")

  def deinit(self):
    return self.addMethods(f"deinit()")
  
  
class Multi_:
  def __new__(cls, *kargs, **kwargs):
    position, name = cls.MULTI_PARAMS_
    
    if name in kwargs:
      ArgIsKW = True
      values = kwargs[name]
    elif len(kargs) > position:
      values = kargs[position]
      ArgIsKW = False
      kargs = list(kargs)
    else:
      values = None
    
    if type(values) is Multi:
      multi = Multi()
      
      for value in values:
        if ArgIsKW:
          kwargs[name] = value
        else:
          kargs[position] = value

        obj = object.__new__(cls)
        cls.__init__(obj, *kargs, **kwargs)
        multi.add(obj)
      return multi
    else:
      obj = object.__new__(cls)
      cls.__init__(obj, *kargs, **kwargs)
      return obj

BUZZER_MUL_ = 2 ** (1/12)
BUZZER_BASE_FREQ_ = 6.875

def buzzerConvert_(note):
  return note if note <= 0 else round(BUZZER_BASE_FREQ_ * BUZZER_MUL_ ** ( note + 3 ))

class Buzzer(Multi_):
  MULTI_PARAMS_ = (0, "pwm")

  def __init__(self, pwm=None, *, u16=32000, extra=True):
    self.on_ = False
    Buzzer.init(self, pwm, u16=u16, extra=extra)

  def init(self, pwm, *, u16=32000, extra=True):
    self.u16_ = u16
    self.pwm_ = pwm
    
    if pwm is not None:
      self.pwm_.setU16(0)
    
    return self
  
  def ratio(self, ratio = None):
    prevRatio = self.u16_ / 65535

    if ratio is not None:
      self.u16_ = int(65535 * ratio)

      if self.on_:
        self.pwm_.setU16(self.u16_)
    
    return prevRatio
    
  def PWM(self):
    return self.pwm_
    
  def off(self):
    if self.on_:
      self.on_ = False
      self.pwm_.setU16(0)
      
    return self
    
  def on(self, freq):
    if freq == 0:
      self.off()
    elif self.on_:
        self.pwm_.setFreq(int(freq))
    else:
        self.pwm_.setFreq(int(freq)).setU16(self.u16_)
        self.on_ = True

    return self
        
  def play(self, note):
    if note == 0:
      return self.off()
    else:
      return self.on(buzzerConvert_(note))
    
  def getDevice(self):
    return self.pwm_.getDevice()
  
  def flash(self):
    self.pwm_.setU16(0)


class PCA9685(Core_):
  def __init__(self, i2c=None, *, addr=None):
    super().__init__()

    if i2c:
      self.init(i2c, addr=addr)

  def init(self, i2c, addr=None):
    super().init(
      "PCA9685-1", f"PCA9685({i2c.getObject()}, {addr})", i2c.getDevice()
    )

  def deinit(self):
    self.addMethods(f"reset()")

  def nsToU12_(self, duty_ns):
    return int(self.freq() * duty_ns * 0.000004095)

  def u12ToNS_(self, value):
    return int(200000000 * value / (self.freq() * 819))

  async def getOffsetAwait(self):
    return int(await self.callMethodAwait("offset()"))

  def setOffset(self, offset):
    return self.addMethods(f"offset({offset})")

  async def getFreqAwait(self):
    return int(await self.callMethodAwait("freq()"))

  def setFreq(self, freq):
    return self.addMethods(f"freq({freq})")

  async def getPrescaleAwait(self):
    return int(await self.callMethodAwait("prescale()"))

  def setPrescale(self, value):
    return self.addMethods(f"prescale({value})")


class PWM_PCA9685(Core_):
  def __init__(self, pca=None, channel=None):
    super().__init__()

    if bool(pca) != (channel != None):
      raise Exception("Both or none of 'pca' and 'channel' must be given!")

    if pca:
      self.init(pca, channel)

  def init(self, pca, channel):
    super().init(
      "PWM_PCA9685-1",
      f"PWM_PCA9685({pca.getObject()}, {channel})",
      pca.getDevice(),
    )

    self.pca = pca  # Not used inside this object, but to avoid pca being destroyed by GC, as it is used on the µc.

  def deinit(self):
    self.addMethods(f"deinit()")

  async def getOffsetAwait(self):
    return self.pca.getOffsetAwait()

  def setOffset(self, offset):
    self.pca.setOffset(offset)

  async def getNSAwait(self):
    return int(await self.callMethodAwait(f"duty_ns()"))

  def setNS(self, ns):
    self.addMethods(f"duty_ns({ns})")

  async def getU16Await(self, u16=None):
    return int(await self.callMethodAwait("duty_u16()"))

  def setU16(self, u16):
    self.addMethods(f"duty_u16({u16})")

  async def getFreqAwait(self):
    return await self.pca.getFreqAwait()

  def setFreq(self, freq):
    self.pca.setFreq(freq)

  async def getPrescaleAwait(self):
    return await self.pca.getPrescaleAwait()

  def setPrescale(self, value):
    self.pca.setPrescale(value)


class HD44780_I2C(Multi_, Core_):
  VERTICAL_GAUGES_TABLE_ = tuple((' ',) + tuple(chr(c) for c in (range(8))))
  HORIZONTAL_GAUGES_TABLE_ = ('',) + tuple(chr(c) for c in range(5)) + (chr(4),)
  VERTICAL_PEAKS_TABLE_ = tuple(chr(c) for c in (32, 0, 95, 1, 2, 45, 3, 4, 5, 32))
  HORIZONTAL_PEAKS_TABLE_ = tuple(chr(c) for c in range(6))
  MULTI_PARAMS_ = (2, "i2c")

  def __init__(self, numColumns, numLines, /, i2c, addr=None, extra=True):
    super().__init__()

    if i2c:
      HD44780_I2C.init(self, numColumns, numLines, i2c, addr=addr, extra=extra)
    elif addr is not None:
      raise Exception("addr can not be given without i2c!")

  def init(self, numColumns, numLines, i2c, addr=None, extra=True):
    self.numLines_ = numLines
    self.numColumns_ = numColumns
    return (
      super()
      .init(
        "HD44780_I2C-1",
        f"HD44780_I2C({i2c.getObject()},{numLines},{numColumns},{addr})",
        i2c.getDevice(),
        extra,
      )
      .flash(extra)
    )

  def moveTo(self, x, y):
    return self.addMethods(f"move_to({x},{y})")

  def putString(self, string):
    # Below line is due to https://github.com/micropython/micropython/issues/19529.
    # According to the HD44780 datasheet, both character of code 0 and 8  display custom char 0…
    string = string.replace(chr(0), chr(8))
    return self.addMethods('putstr("{}")'.format(string.replace('"','\\"')))

  def clear(self):
    # return self.addMethods("clear()") # Do not work !
    return self.moveTo(0,0).putString(" " * self.numColumns_ * self.numLines_)

  def showCursor(self, value=True):
    return self.addMethods("show_cursor()" if value else "hide_cursor()")

  def hideCursor(self):
    return self.showCursor(False)

  def blinkCursorOn(self, value=True):
    return self.addMethods("blink_cursor_on()" if value else "blink_cursor_off()")

  def blinkCursorOff(self):
    return self.blinkCursorOn(False)

  def displayOn(self, value=True):
    return self.addMethods("display_on()" if value else "display_off()")

  def displayOff(self):
    return self.displayOn(False)

  def backlightOn(self, value=True):
    return self.addMethods("backlight_on()" if value else "backlight_off()")

  def backlightOff(self):
    return self.backlightOn(False)
  
  def createChar(self, location, charmap):
    return self.addMethods(f"custom_char({location},{charmap})")

  def flash(self, extra=True):
    self.backlightOn()
    self.getDevice().sleep(FLASH_DELAY_ if isinstance(extra, bool) else extra)
    return self.backlightOff()

  def uploadUpwardGaugeChars(self):
    charmap = [0b00000] * 8
    
    for i in range(8):
      charmap[7-i] = 0b11111
      self.createChar(i, charmap)
      
    return self
  
  def putUpwardGauges(self, position, gauges, strip = False):
    up = ""
    down = ""
    table = self.VERTICAL_GAUGES_TABLE_
    
    for gauge in gauges:
      up += table[max(gauge - 8, 0)]
      down += table[min(gauge, 8)]
      
    if not strip and position == 0 and len(gauges) == 16:
      self.moveTo(0,0).putString(up + down)
    else:
      self.moveTo(position,0).putString(up.rstrip() if len(up.rstrip()) != 0 else " " * 16)
      self.moveTo(position,1).putString(down.rstrip() if len(down.rstrip()) != 0 else " " * 16)

  def uploadDownwardGaugeChars(self):
    charmap = [0b00000] * 8
    
    for i in range(8):
      charmap[i] = 0b11111
      self.createChar(i, charmap)
      
    return self
  
  def putDownwardGauges(self, position, gauges, strip = False):
    up = ""
    down = ""
    table = self.VERTICAL_GAUGES_TABLE_
    
    for gauge in gauges:
      up += table[min(gauge, 8)]
      down += table[max(gauge - 8, 0)]
      
    if not strip and position == 0 and len(gauges) == 16:
      self.moveTo(0,0).putString(up + down)
    else:
      self.moveTo(position,0).putString(up.rstrip() if len(up.rstrip()) != 0 else " " * 16)
      self.moveTo(position,1).putString(down.rstrip() if len(down.rstrip()) != 0 else " " * 16)
  
  def uploadForwardGaugeChars(self):
    charmap = [0b00000] * 8
    
    for c in range(5):
      for i in range(len(charmap)):
        charmap[i] = 0b10000 | ( charmap[i] >> 1 )
      self.createChar(c, charmap)
      
    return self
  
  def getForwardGauge(self, gauge):
    table = self.HORIZONTAL_GAUGES_TABLE_
    return table[6] * (gauge // 5) + table[gauge % 5]
      
  def uploadBackwardGaugeChars(self):
    charmap = [0b00000] * 8
    
    for c in range(5):
      for i in range(len(charmap)):
        charmap[i] = 0b00001 | ( charmap[i] << 1 )
      self.createChar(c, charmap)
      
    charmap = [0b10000] * 8
    self.createChar(5, charmap)

    charmap = [0b01000] * 8
    self.createChar(6, charmap)

    charmap = [0b000010] * 8
    self.createChar(7, charmap)
      
    return self
  
  def getBackwardGauge(self, gauge, max):
    table = self.HORIZONTAL_GAUGES_TABLE_
    return " " *((max - gauge) // 5) + table[gauge % 5] + table[5] * (gauge // 5)
  
  def uploadVPeakChars(self):
    charmap = [0b00000] * 7 + [0b11111]
    
    for c in range(7):
      self.createChar(c, charmap)
      del charmap[0]
      charmap.append(0b0000)
      if c in(0,2):
        del charmap[0]
        charmap.append(0b0000)
      
    return self
    
  def putUpwardPeaks(self, position, peaks, strip = False):
    up = ""
    down = ""
    table = self.VERTICAL_PEAKS_TABLE_
    
    for peak in peaks:
      up += table[max(peak - 7, 0)]
      down += table[min(peak + 1, 9)]
      
    if not strip and position == 0 and len(peaks) == 16:
      self.moveTo(0,0).putString(up + down)
    else:
      self.moveTo(position,0).putString(up.rstrip() if len(up.rstrip()) != 0 else " " * 16)
      self.moveTo(position,1).putString(down.rstrip() if len(down.rstrip()) != 0 else " " * 16)

  def putDownwardPeaks(self, position, peaks, strip = False):
    return self.putUpwardPeaks(position, tuple(15 - peak for peak in peaks), strip)

  def uploadHPeakChars(self):
    self.createChar(0, (0b11111,) + (0,) * 6 + (0b11111,))

    for c in range(1, 6):
      self.createChar(c, (0b11111,) + (0b10000 >> (c - 1),) * 6 + (0b11111,))
        
    return self
    
  def getForwardPeak(self, peak, max):
    table = self.HORIZONTAL_PEAKS_TABLE_
    return table[0] * (peak // 5) +  table[peak % 5 + 1] + table[0] * ((max - peak - 1) // 5)

  def getBackwardPeak(self, peak, max):
    return self.getForwardPeak(max - peak, max)


class Servo(Multi_):
  MULTI_PARAMS_ = (1, 'pwm')
  class Specs:
    def __init__(self, u16_min, u16_max, range):
      self.min = u16_min
      self.max = u16_max
      self.range = range

  class Tweak:
    def __init__(self, angle, u16_offset, invert):
      self.angle = angle
      self.offset = u16_offset
      self.invert = invert

  class Domain:
    def __init__(self, u16_min, u16_max):
      self.min = u16_min
      self.max = u16_max

  def test_(self, specs, tweak, domain):
    if tweak:
      if not specs:
        raise Exception("'tweak' can not be given without 'specs'!")

    if domain:
      if not specs:
        raise Exception("'domain' can not be given without 'specs'!")

  def __init__(self, pwm=None, specs=None, /, *, tweak=None, domain=None, smooth=False):
    super().__init__()

    self.test_(specs, tweak, domain)
    
    self.pwm_ = None
    self.u16_ = None

    if pwm:
      self.init(pwm, specs, smooth=smooth, tweak=tweak, domain=domain)

  def init(self, pwm, specs, *, tweak=None, domain=None, smooth=False, extra=True):
    self.test_(specs, tweak, domain)

    if not tweak:
      tweak = self.Tweak(specs.range / 2, 0, False)

    if not domain:
      domain = self.Domain(specs.min, specs.max)

    self.specs_ = specs
    self.tweak_ = tweak
    self.domain_ = domain

    self.pwm_ = pwm

    self.set = self.setSmooth if smooth else self.setRough
    
  def getDevice(self):
    return self.pwm_.getDevice()

  def angleToDuty_(self, angle):
    if self.tweak_.invert:
      angle = -angle

    u16 = (
      self.specs_.min
      + (angle + self.tweak_.angle)
      * (self.specs_.max - self.specs_.min)
      / self.specs_.range
      + self.tweak_.offset
    )

    if u16 > self.domain_.max:
      u16 = self.domain_.max
    elif u16 < self.domain_.min:
      u16 = self.domain_.min
      
    return int(u16)

  def dutyToAngle_(self, duty):
    angle = (
      self.specs_.range
      * (duty - self.tweak_.offset - self.specs_.min)
      / (self.specs_.mas - self.specs_.min)
    )

    if self.tweak_.invert:
      angle = -angle

    return angle - self.tweak_.angle

  async def getAngleAwait(self):
    return self.dutyToAngle_(await self.pwm_.getU16Await())
  
  def setU16Straight_(self, u16):
    return self.pwm_.setU16(u16)
    
  def setU16Rough(self, u16):
    self.u16_ = min(max(u16, self.specs_.min), self.specs_.max)
    return self.setU16Straight_(u16)
  
  def getU16(self):
    return self.u16_
  
  def setU16Smooth(self, u16):
    step = 40
    
    if self.u16_ is None:
      self.setU16Rough(u16)
    else:
      while self.u16_ < u16:
        self.setU16Rough(min(self.u16_ + step, u16))
        
      while self.u16_ > u16:
        self.setU16Rough(max(self.u16_ - step, u16))
      
    return self
  
  def setAngleRough(self, angle):
    return self.setU16Rough(self.angleToDuty_(angle))
  
  def setAngleSmooth(self, angle):
    return self.setU16Smooth(self.angleToDuty_(angle))
  
  def setRough(self, value):
    return self.setU16Rough(value + self.specs_.min)
  
  def setSmooth(self, value):
    return self.setU16Smooth(value + self.specs_.min)
  
  def get(self):
    return self.u16_ - self.specs_.min
  

def hexImageToBytearray_(hex_string, width=128, height=64):
  bits = []
  for c in hex_string:
    nibble = int(c, 16)
    bits.append((nibble >> 3) & 1)
    bits.append((nibble >> 2) & 1)
    bits.append((nibble >> 1) & 1)
    bits.append(nibble & 1)

  pages = height // 8
  out = bytearray(width * pages)

  for page in range(pages):
    for x in range(width):
      byte = 0
      for bit in range(8):
        y = page * 8 + bit
        pixel = bits[y * width + x]
        byte |= pixel << bit
      out[page * width + x] = byte

  return out


class _OLED_(Core_):
  def show(self):
    return self.addMethods("show()")

  def powerOff(self):
    return self.addMethods("poweroff()")

  def powerOn(self):
    return self.addMethods("poweron()")

  def contrast(self, contrast):
    return self.addMethods(f"contrast({contrast})")

  def invert(self, invert):
    return self.addMethods(f"invert({invert})")

  def fill(self, col):
    return self.addMethods(f"fill({col})")

  def pixel(self, x, y, col=1):
    return self.addMethods(f"pixel({x},{y},{col})")

  def scroll(self, dx, dy):
    return self.addMethods(f"scroll({dx},{dy})")

  def text(self, string, x, y, col=1):
    return self.addMethods(f"text('{string}',{x}, {y}, {col})")

  def hText(self, string, y, col=1, trueWidth=None):
    trueWidth = trueWidth or f"{self.getObject()}.width"
    return self.addMethods(
      f"text('{string}',max(( {trueWidth} - len('{string}' ) * 8) // 2, 0), {y}, {col})"
    )

  def rect(self, x, y, w, h, col, fill=False):
    return self.addMethods(f"rect({x},{y},{w},{h},{col},{fill})")

  def hline(self, x, y, w, col):
    return self.addMethods(f"hline({x},{y},{w},{col})")

  def vline(self, x, y, h, col):
    return self.addMethods(f"vline({x},{y},{h},{col})")

  def line(self, x1, y1, x2, y2, col):
    return self.addMethods(f"line({x1},{y1},{x2},{y2},{col})")

  def ellipse(self, x, y, rx, ry, col, fill=False, quad=15):
    return self.addMethods(f"ellipse({x},{y},{rx},{ry},{col},{fill},{quad})")
  
  def draw(self, pattern, width, ox=0, oy=0, mul=1, compress=True):
    if width % 4:
      raise Exception("'width' must be a multiple of 4!")
    if width == 128 and ox == 0 and oy == 0 and mul == 1 and len(pattern) >= 2048:
      if compress:
        return self.addMethods(f'buffer[:] = deflate.DeflateIO(io.BytesIO(ubinascii.a2b_base64("{base64.b64encode(gzip.compress(hexImageToBytearray_(pattern), compresslevel = 9)).decode("ascii")}")), deflate.AUTO, 10).read()')
      else:
        return self.addMethods(f'buffer[:] = ubinascii.a2b_base64("{base64.b64encode(hexImageToBytearray_(pattern)).decode("ascii")}")')
    else:
      return self.addMethods(f"draw('{pattern}',{width},{ox},{oy},{mul})")

  def flash(self, extra=True):
    self.fill(1).show()
    self.getDevice().sleep(FLASH_DELAY_ if isinstance(extra, bool) else extra)
    return self.fill(0).show()

OLED_SCRIPT = """
def oled_show(self, buffer, compressed = True):
  x0 = 0
  x1 = self.width - 1
  if self.width == 64:
    # displays with width of 64 pixels are shifted by 32
    x0 += 32
    x1 += 32
#  self.write_cmd(_SSD1306_SET_COL_ADDR)  # TOFIX
  self.write_cmd(const(0x21))
  self.write_cmd(x0)
  self.write_cmd(x1)
#  self.write_cmd(_SSD1306_SET_PAGE_ADDR) # TOFIX
  self.write_cmd(const(0x22))
  self.write_cmd(0)
  self.write_cmd(self.pages - 1)
  if compressed:
    with deflate.DeflateIO(io.BytesIO(ubinascii.a2b_base64(buffer)), deflate.RAW, 10) as decompressor:
      self.write_data(decompressor.read())
  else:
    self.write_data(ubinascii.a2b_base64(buffer))
"""

class OLED_(Core_, FrameBuffer):
  def __init__(self, width, height, device = None):
    self.width = width
    self.height = height
    self.pages = self.height // 8
    self.buffer = bytearray(self.pages * self.width)
    Core_.__init__(self, device)
    FrameBuffer.__init__(self, self.buffer, self.width, self.height, MONO_VLSB)
  
  def show(self, compress = OLED_SHOW_DEFAULT_COMPRESS_VALUE):
    # 'compress' can not be set to True for Brython due to https://github.com/brython-dev/brython/issues/2910
    if compress:
      compressor = zlib.compressobj(level=9, method=zlib.DEFLATED, wbits=-10)
      command = f'oled_show({self.getObject()}, "{base64.b64encode(compressor.compress(self.buffer) + compressor.flush()).decode("ascii")}")'
    else:
      command = f'oled_show({self.getObject()}, "{base64.b64encode(self.buffer).decode("ascii")}", False)'

    # print(command)
    return self.addCommand(command)

  def show_(self, compress = True):
    if compress:
      self.addMethods(f'buffer[:] = deflate.DeflateIO(io.BytesIO(ubinascii.a2b_base64("{base64.b64encode(gzip.compress(self.buffer, compresslevel = 9)).decode("ascii")}")), deflate.AUTO, 10).read()')
    else:
      self.addMethods(f'buffer[:] = ubinascii.a2b_base64("{base64.b64encode(self.buffer).decode("ascii")}")')

    return self.addMethods("show()")

  def powerOff(self):
    return self.addMethods("poweroff()")

  def powerOn(self):
    return self.addMethods("poweron()")

  def contrast(self, contrast):
    return self.addMethods(f"contrast({contrast})")

  def invert(self, invert):
    return self.addMethods(f"invert({invert})")

  def fill(self, col):
    FrameBuffer.fill(self, col)

    return self

  def pixel(self, x, y, col=1):
    FrameBuffer.pixel(self, x, y, col)

    return self

  def scroll(self, dx, dy):
    FrameBuffer.scroll(self, dx, dy)

    return self

  def text(self, string, x, y, col=1):
    FrameBuffer.text(self, string, x, y, col)

    return self

  def hText(self, string, y, col=1, trueWidth=None):
    trueWidth = trueWidth or self.width

    return FrameBuffer.text(self, string, max(( {trueWidth} - len(string) * 8) // 2, 0), y, col)
  
  def rect(self, x, y, w, h, col, fill=False):
    FrameBuffer.rect(self, x, y, w, h, col, fill)

    return self

  def hline(self, x, y, w, col):
    FrameBuffer.hline(self, x, y, w, col)

    return self

  def vline(self, x, y, h, col):
    FrameBuffer.vline(self, x, y, h, col)

    return self

  def line(self, x1, y1, x2, y2, col):
    FrameBuffer.line(self, x1, y1, x2, y2, col)

    return self

  def ellipse(self, x, y, rx, ry, col, fill=False, quad=15):
    FrameBuffer.ellipse(self, x, y, rx, ry, col, fill, quad)

    return self
  
  def draw(self, pattern, width, ox=0, oy=0, mul=1):
    if width % 4:
      raise Exception("'width' must be a multiple of 4!")
    py = width >> 2
    for pos in range(len(pattern)):
      char = int(pattern[pos],16) 
      # y = oy + mul * int(pos / py)
      y = oy + mul * ( pos // py )
      px = ( pos << 2 ) % width
      masq = 8
      for offset in range(px, px + 4):
        if mul == 1:
          self.pixel(ox + offset, y, 1 if char & masq else 0)
        else:
          self.rect(ox + mul * offset, y, mul, mul, 1 if char & masq else 0, True)
        masq = masq >> 1

    return self

  def flash(self, extra=True):
    self.fill(1).show()
    self.getDevice().sleep(FLASH_DELAY_ if isinstance(extra, bool) else extra)
    return self.fill(0).show()


class SSD1306(OLED_):
  def rotate(self, rotate=True):
    return self.addMethods(f"rotate({rotate})")


class SSD1306_I2C(Multi_, SSD1306):
  MULTI_PARAMS_ = (2, 'i2c')
  def __init__(
    self,
    width=None,
    height=None,
    /,
    i2c=None,
    addr=None,
    external_vcc=False,
    extra=True,
  ):
    Multi.__init__(self)
    SSD1306.__init__(self, width, height)

    if bool(width) != bool(height) != bool(i2c):
      raise Exception("All or none of width/height/i2c must be given!")
    elif width:
      self.init(
        width, height, i2c, external_vcc=external_vcc, addr=addr, extra=extra
      )
    elif addr:
      raise Exception("addr can not be given without i2c!")

  def init(self, width, height, /, i2c, external_vcc=False, addr=None, extra=True):
    SSD1306.init(
      self,
      "SSD1306_I2C-1",
      f"SSD1306_I2C({width}, {height}, {i2c.getObject()}, {addr}, {external_vcc})",
      i2c.getDevice(),
      extra,
    ).flash(extra if not isinstance(extra, bool) else 0.15)


class SH1106(OLED_):
  pass


class SH1106_I2C(SH1106):
  def __init__(
    self,
    width=None,
    height=None,
    /,
    i2c=None,
    addr=None,
    external_vcc=False,
    extra=True,
  ):
    super().__init__()

    if bool(width) != bool(height) != bool(i2c):
      raise Exception("All or none of width/height/i2c must be given!")
    elif width:
      self.init(
        width, height, i2c, external_vcc=external_vcc, addr=addr, extra=extra
      )
    elif addr:
      raise Exception("addr can not be given without i2c!")

  def init(self, width, height, /, i2c, external_vcc=False, addr=None, extra=True):
    super().init(
      "SH1106_I2C-1",
      f"SH1106_I2C({width}, {height}, {i2c.getObject()}, addr={addr}, external_vcc={external_vcc})",
      i2c.getDevice(),
      extra,
    ).flash(extra if not isinstance(extra, bool) else 0.15)


OD_SH1106_ = "SH1106"
OD_SSD1306_ = "SSD1306"


class OLED_I2C:
  def __new__(cls, driver, *args, **kwargs):
    if driver == OD_SH1106_:
      return SH1106_I2C(*args, **kwargs)
    elif driver == OD_SSD1306_:
      return SSD1306_I2C(*args, **kwargs)
    else:
      raise Exception(f"Unknown OLED driver {driver}!")


c_ = lambda color: f"color565({color})"
f_ = lambda function, fill: f"{'fill_' if fill else 'draw_'}{function}"


def zoom_rgb565_(raw_data, width, height, hzoom, vzoom):
  zoomed_width = width * hzoom
  zoomed_height = height * vzoom

  zoomed_data = bytearray(zoomed_width * zoomed_height * 2)

  for y in range(height):
    for x in range(width):
      idx_src = (y * width + x) * 2
      pixel = raw_data[idx_src : idx_src + 2]  # 2 octets RGB565

      x_start = x * hzoom
      y_start = y * vzoom

      for dy in range(vzoom):
        for dx in range(hzoom):
          x_dst = x_start + dx
          y_dst = y_start + dy
          idx_dst = (y_dst * zoomed_width + x_dst) * 2
          zoomed_data[idx_dst : idx_dst + 2] = pixel

  return bytes(zoomed_data)


class ILI9341(Core_):
  def __init__(
    self,
    width,
    height,
    /,
    rotation=0,
    dc=None,
    cs=None,
    rst=None,
    spi=None,
    extra=True,
  ):
    super().__init__()

    if (
      bool(width)
      != bool(height)
      != bool(spi)
      != bool(dc)
      != bool(cs)
      != bool(rst)
    ):
      raise Exception("All or none of width/height/spi/dc/cs/rst must be given!")
    elif width:
      self.init(
        width,
        height,
        rotation=rotation,
        spi=spi,
        dc=dc,
        cs=cs,
        rst=rst,
        extra=extra,
      )

  def init(
    self,
    width,
    height,
    /,
    rotation=0,
    spi=None,
    dc=None,
    cs=None,
    rst=None,
    extra=True,
  ):
    super().init(
      "ILI9341-1",
      f"ILI9341({spi.getObject()}, machine.Pin({cs}), machine.Pin({dc}), machine.Pin({rst}), {width}, {height}, {rotation})",
      spi.getDevice(),
      extra,
    )

  def on(self, value=True):
    return self.addMethods(f"display_{'on' if value else 'off'}()")

  def off(self):
    return self.on(False)

  def clear(self, color=0):
    return self.addMethods(f"clear(color565({color}))")

  def cleanup(self):
    return self.addMethods("cleanup()")

  def invert(self, value=True):
    return self.addMethods(f"invert({value})")

  def pixel(self, x, y, color):
    return self.addMethods(f"draw_pixel({x}, {y}, {c_(color)})")

  def hline(self, x, y, w, color):
    return self.addMethods(f"draw_hline({x}, {y}, {w}, {c_(color)})")

  def vline(self, x, y, h, color):
    return self.addMethods(f"draw_vline({x}, {y}, {h}, {c_(color)})")

  def line(self, x0, y0, x1, y1, color):
    return self.addMethods(f"draw_line({x0}, {y0}, {x1}, {y1}, {c_(color)})")

  def lines(self, coords, color):
    return self.addMethods(f"draw_lines([tuple(map(int, pair.split(','))) for pair in '{{';'.join(f\"{{x}},{{y}}\" for x,y in coords)}}'.split(';')], {c_(color)})")

  def rect(self, x, y, w, h, color, fill=True):
    return self.addMethods(
      f"{f_('rectangle', fill)}({x}, {y}, {w}, {h}, {c_(color)})"
    )

  def poly(self, sides, x0, y0, r, color, rotate=0, fill=True):
    return self.addMethods(
      f"{f_('polygon', fill)}({sides}, {x0}, {y0}, {r}, {c_(color)}, {rotate})"
    )

  def circle(self, x, y, r, color, fill=True):
    return self.addMethods(f"{f_('circle', fill)}({x}, {y}, {r}, {c_(color)})")

  def ellipse(self, x, y, rx, ry, color, fill=True):
    return self.addMethods(
      f"{f_('ellipse', fill)}({x}, {y}, {rx}, {ry}, {c_(color)})"
    )

  def text(self, x, y, text, color=255, bgcolor=0, rotate=0):
    return self.addMethods(
      f"draw_text8x8({x}, {y}, '{text}', {c_(color)}, {c_(bgcolor)}, {rotate})"
    )

  def draw(self, stream, width, height, speed=1, hzoom=1, vzoom=0):
    if vzoom == 0:
      vzoom = hzoom

    for i in range(height // speed):
      data = stream.read(width * 2 * speed)
      self.addMethods(
        f"draw('{base64.b64encode(zoom_rgb565_(data, width, speed, hzoom, vzoom)).decode('ascii')}',0, {i*speed*vzoom}, {width*hzoom}, {speed*vzoom})"
      )

    if remainder := height % speed:
      data = stream.read(width * 2 * remainder)
      self.addMethods(
        f"draw('{base64.b64encode(zoom_rgb565_(data, width, speed, hzoom, vzoom)).decode('ascii')}',0, {(height // speed) * speed*vzoom}, {width*hzoom}, {remainder*vzoom})"
      )

    return self


class SSD1680_SPI(OLED_):
  def __init__(self, cs, dc, rst, busy, spi, landscape=True):
    super().__init__()
    self.init(cs, dc, rst, busy, spi, landscape=landscape)

  def init(self, cs, dc, rst, busy, spi, landscape=False, extra=True):
    super().init(
      "SSD1680-1",
      f"SSD1680({spi.getObject()},machine.Pin({cs}, machine.Pin.OUT),machine.Pin({dc}, machine.Pin.OUT),{rst},machine.Pin({busy}, machine.Pin.IN),{landscape})",
      spi.getDevice(),
      extra,
    )
    self.addMethods("init()")

  def hText(self, *args, trueWidth=None, **kargs):
    return super().hText(*args, trueWidth=trueWidth or 250, **kargs)


def pwmJumps(jumps, step=100, delay=0.05):
  command = "pwmJumps([\n"

  for jump in jumps:
    command += f"\t[{jump[0].getObject()},{jump[1]}],\n"

  command += f"], {step}, {delay})"

  return command


def execute_(command, device):
  device.addModule("PWMJumps-1")
  device.addCommand(command)


def servoMoves(moves, step=100, delay=0.05):
  jumps = {}
  devices = {}
  commands = {}

  for move in moves:
    servo = move[0]
    key = id(servo.getDevice())

    if key not in devices:
      devices[key] = servo.getDevice()
      jumps[key] = []
      commands[key] = []

    jumps[key].append([servo.pwm_, servo.angleToDuty_(move[1])])

  for key in jumps:
    commands[key].append(pwmJumps(jumps[key], step, delay))

  for key in commands:
    for command in commands[key]:
      execute_(command, devices[key])


def rbShade(variant, i, max):
  match int(variant) % 6:
    case 0:
      return [max, i, 0]
    case 1:
      return [max - i, max, 0]
    case 2:
      return [0, max, i]
    case 3:
      return [0, max - i, max]
    case 4:
      return [i, 0, max]
    case 5:
      return [max, 0, max - i]


def rbFade(variant, i, max, inOut):
  if not inOut:
    i = max - i
  match variant % 6:
    case 0:
      return [i, 0, 0]
    case 1:
      return [i, i, 0]
    case 2:
      return [0, i, 0]
    case 3:
      return [0, i, i]
    case 4:
      return [0, 0, i]
    case 5:
      return [i, 0, i]


def rbShadeFade(variant, i, max):
  if i < max:
    return rbFade(variant, i, max, True)
  elif i > max * 6:
    return rbFade((variant + 5) % 6, i % max, max, False)
  else:
    return rbShade(variant + int((i - max) / max), i % max, max)


def setCommitBehavior(behavior):
  global defaultCommitBehavior_
  
  oldCommitBehavior = defaultCommitBehavior_
  defaultCommitBehavior_ = behavior
  return oldCommitBehavior
  
  
def getCommitBehavior():
  return defaultCommitBehavior_
  
  
PP_NOTE_MAP_ = {
  'C': -9, 'C#': -8, 'Db': -8, 'D': -7, 'D#': -6, 'Eb': -6,
  'E': -5, 'F': -4, 'F#': -3, 'Gb': -3, 'G': -2, 'G#': -1, 'Ab': -1,
  'A': 0, 'A#': 1, 'Bb': 1, 'B': 2
}  
  
def voicesNote2Midi_(noteStr, octave):
  if noteStr == 'R':
    return 0  # silence
  elif noteStr == '-':
    return -1
  
  if len(noteStr) == 2 and noteStr[1] in('b','#'):
    noteKey = noteStr
  else:
    noteKey = noteStr[0]

  if noteKey not in PP_NOTE_MAP_:
    return 0
  
  return 12 * (int(octave) + 2) + PP_NOTE_MAP_[noteKey]


def voicesDuration2Seconds_(duration, base, dots=0):
  value = 1 / (2 ** (4 - duration))

  total = value
  
  if dots == -1:
    total = total * 2  / 3
  else:
    for _ in range(dots):
      value /= 2
      total += value

  return base * total


def voicesParseNoteString_(note_str, base):
  match = re.match(r'([A-Z][b#]?)(\d)(\d)(\.*,?)', re.sub(r"\s+", "", note_str))

  if not match:
    match = re.match(r'([R\-])(\d)(\.*,?)', note_str)

    if not match:
      return None

    octave = 0
    note, duration, dots = match.groups()
  else:
    note, octave, duration, dots = match.groups()
    
  return buzzerConvert_(voicesNote2Midi_(note, int(octave))), voicesDuration2Seconds_(int(duration), base, len(dots) if len(dots) == 0 or dots[0] != ',' else -1),


def voicesExtractNotes_(voice_str):
  return re.findall(r'([A-Z\-][b#]?\d\d\.*,?|[R\-]\d\.*,?)', voice_str)


def playEvents(polyEvents, durationCallback):
  cumul = 0

  indexes = [0] * len(polyEvents)
  events = indexes.copy()
  delays = indexes.copy()

  while any(i is not None for i in indexes):
    duration = 100000

    for i in range(len(indexes)):
      if indexes[i] is not None:
        if delays[i] == 0:
          events[i], delays[i] = polyEvents[i][indexes[i]]
          indexes[i] += 1
          events[i]()
        duration = min(duration, delays[i])
        
    cumul += duration
    params = [duration]

    if len(inspect.signature(durationCallback).parameters) > 1:
      params.append(cumul)

    durationCallback(*params)
        
    for i in range(len(indexes)):
      if indexes[i] is not None and indexes[i] >= len(polyEvents[i]):
        indexes[i] = None
      else:
        delays[i] -= duration
        
  return cumul
        

def voicesToEvents(voices, tempo, callback):
  voiceNotes = [voicesExtractNotes_(v) for v in voices]
  
  raws = []

  for i in range(len(voiceNotes)):
    raw = []
    for b in voiceNotes[i]:
      freq, duration = voicesParseNoteString_(b, 60.0 / tempo)

      raw.append((
        lambda
          freq=freq,
          turn=i:
            callback(freq, turn) if len(inspect.signature(callback).parameters) > 1 else callback(freq),
        duration))
    raw.append((
      lambda turn=i:
        callback(0, turn) if len(inspect.signature(callback).parameters) > 1 else callback(0), 
      0))
    raws.append(raw)

  return raws


def playVoices(voices, tempo, voiceCallback, durationCallback):
  return playEvents(voicesToEvents(voices, tempo, voiceCallback), durationCallback)


###### Begin of section high precision time handling based on NTP #####
NTP_SCRIPT_ = """
import socket
import struct

NTP_DELTA = 2208988800  # Différence entre epoch NTP (1900) et Unix (1970)

def unpack_ntp_timestamp_us(data, offset):
  sec, frac = struct.unpack("!II", data[offset:offset+8])
  unix_sec = sec - NTP_DELTA
  return unix_sec * 1_000_000 + (frac * 1_000_000) // 2**32


def ntp_time_t1_t4_us(host="fr.pool.ntp.org"):
  addr = socket.getaddrinfo(host, 123)[0][-1]
  s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  s.settimeout(2)

  packet = chr(0x1b) + 47 * chr(0)

  T1_us = time.ticks_us()
  s.sendto(packet, addr)

  data = s.recv(48)
  T4_us = time.ticks_us()  # µs
  s.close()

  T2_us = unpack_ntp_timestamp_us(data, 32)
  T3_us = unpack_ntp_timestamp_us(data, 40)

  offset_us = ((T2_us - T1_us) + (T3_us - T4_us)) // 2

  return T4_us + offset_us


def precise_time_us():
  t_ntp_us, t0_ticks_us = TIME_ANCHOR_US
  elapsed_us = time.ticks_diff(time.ticks_us(), t0_ticks_us)
  return t_ntp_us + elapsed_us


def set_rtc_from_us(timestamp_us):
  ts = timestamp_us // 1_000_000
  tm = time.localtime(ts)
  us = timestamp_us % 1_000_000
  rtc_tuple = (tm[0], tm[1], tm[2], tm[6] + 1, tm[3], tm[4], tm[5], us)
  machine.RTC().datetime(rtc_tuple)


def sleep_until_us(target_time_us):
  while precise_time_us() < target_time_us:
    pass
        
        
def ntp_set_time():
  global TIME_ANCHOR_US
  gc.collect()
  t_ntp_us = ntp_time_t1_t4_us()
  t0_ticks_us = time.ticks_us()
  TIME_ANCHOR_US = (t_ntp_us, t0_ticks_us)

  set_rtc_from_us(precise_time_us())
"""

def gcCollect():
  addCommand("gc.collect()")

def ntpSetTime(device = None):
  return getDevice(device=device).ntpSetTime()

def ntpSleepUntil(timestamp, device = None):
  return getDevice(device=device).ntpSleepUntil(timestamp)

def ntpSleep(delay, device = None):
  return getDevice(device=device).ntpSleep(delay)

def ntpTime(device = None):
  return getDevice(device=device).ntpTime()

###### End of section high precision time handling based on NTP #####


##### Section dédicated to micro:bit #####

MB_SCRIPT_ = """
import time
from machine import UART

# --- UART + framing ---
MB_START_ = 0x7E
MB_END_   = 0x7F

mbUART_ = UART(1, baudrate=115200, tx=21, rx=20)

def mbChecksum_(data):
    return sum(data) & 0xFF

def mbSendFrame_(payload_str):
    data = payload_str.encode()
    frame = bytes([MB_START_, len(data)]) + data + bytes([mbChecksum_(data), MB_END_])
    mbUART_.write(frame)

# Buffer circulaire
mbRXBuffer_ = bytearray()

def mbFindByte_(buf, value, start=0):
    for i in range(start, len(buf)):
        if buf[i] == value:
            return i
    return -1

def mbReadFrame_():
    global mbRXBuffer_

    if mbUART_.any():
        mbRXBuffer_.extend(mbUART_.read())

    s = mbFindByte_(mbRXBuffer_, MB_START_)
    if s < 0:
        if len(mbRXBuffer_) > 128:
            mbRXBuffer_ = bytearray()
        return None

    e = mbFindByte_(mbRXBuffer_, MB_END_, s + 1)
    if e < 0:
        return None

    frame = mbRXBuffer_[s:e+1]
    mbRXBuffer_ = mbRXBuffer_[e+1:]

    if len(frame) < 4:
        return None

    length = frame[1]
    if len(frame) < 3 + length + 1:
        return None

    payload = frame[2:2+length]
    cks = frame[2+length]

    if mbChecksum_(payload) != cks:
        return None

    return ''.join(chr(b) for b in payload)

mbSeq_ = 0

def mbSendReliable_(content, retries=5, timeout_ms=600):
    global mbSeq_

    payload = "%d:%s" % (mbSeq_, content)

    for attempt in range(retries):

        # Purge du buffer avant envoi
        global mbRXBuffer_
        mbRXBuffer_ = bytearray()

        mbSendFrame_(payload)
        time.sleep_ms(20)

        t0 = time.ticks_ms()

        while time.ticks_diff(time.ticks_ms(), t0) < timeout_ms:
            msg = mbReadFrame_()
            if msg:

                if msg.startswith("ACK:"):
                    ack_seq = int(msg[4:])
                    if ack_seq == mbSeq_:
                        mbSeq_ ^= 1
                        return True

                if msg.startswith("NACK:"):
                    nack_seq = int(msg[5:])
                    if nack_seq == mbSeq_:
                        break

        # timeout → nouvelle tentative

    return False

# --- Envoi fiable AVEC valeur de retour (réponse + ACK) ---

def mbRequestValue_(cmd, prefix):
    global mbSeq_, mbRXBuffer_

    payload = "%d:%s" % (mbSeq_, cmd)

    for attempt in range(5):
        mbRXBuffer_ = bytearray()
        mbSendFrame_(payload)
        time.sleep_ms(20)

        t0 = time.ticks_ms()
        value = None

        while time.ticks_diff(time.ticks_ms(), t0) < 600:
            msg = mbReadFrame_()
            if not msg:
                continue

            # Réponse de la micro:bit
            if msg.startswith(prefix):
                try:
                    value = int(msg[len(prefix):])
                except:
                    value = None
                continue

            # ACK
            if msg.startswith("ACK:"):
                ack_seq = int(msg[4:])
                if ack_seq == mbSeq_:
                    mbSeq_ ^= 1
                    return value

        # timeout → retry

    return None


# --- SYNC initial ---

def mbSync():
    global mbSeq_
    mbSeq_ = 0
    print(mbSendReliable_("SYNC"))


# --- Classe Image (style micro:bit) ---

class Microbit:
    class Image:
        def __init__(self, data):
            self.data = data

        @staticmethod
        def fromRows(rows):
            return Microbit.Image("".join(rows))

    class Display:
        @staticmethod
        def clear():
            return mbSendReliable_("CLR")

        @staticmethod
        def setPixel(x, y, b):
            return mbSendReliable_("PIX:%d,%d,%d" % (x, y, b))

        @staticmethod
        def getPixel(x, y):
            return mbRequestValue_("GET:%d,%d" % (x, y), "VAL:")

        @staticmethod
        def showText(text, delay=150):
            return mbSendReliable_("SCR:%d:%s" % (delay, text))

        @staticmethod
        def scroll(text, delay=150):
            return Microbit.Display.showText(text, delay)

        @staticmethod
        def showImage(img):
            return mbSendReliable_("IMG:" + img)

        @staticmethod
        def animate(images, delay=150, loop=False):
            loop_flag = 1 if loop else 0
            payload = "ANM:%d:%d:%s" % (delay, loop_flag, "|".join(images))
            return mbSendReliable_(payload)

        @staticmethod
        def stopAnimation():
            return mbSendReliable_("STOP")

        @staticmethod
        def on():
            return mbSendReliable_("ON")

        @staticmethod
        def off():
            return mbSendReliable_("OFF")

        @staticmethod
        def isOn():
            val = mbRequestValue_("ISON", "ION:")
            return bool(val) if val is not None else None

        @staticmethod
        def readLightLevel():
            return mbRequestValue_("LUX", "LIG:")

        @staticmethod
        def show(obj, delay=400, loop=False, wait=True):
            if isinstance(obj, str):
                return Microbit.Display.scroll(obj, delay)

            if isinstance(obj, Microbit.Image):
                return Microbit.Display.showImage(obj.data)

            if isinstance(obj, list):
                frames = []
                for img in obj:
                    if isinstance(img, Microbit.Image):
                        frames.append(img.data)
                    else:
                        raise TypeError("List must contain Image objects")
                return Microbit.Display.animate(frames, delay=delay, loop=loop)

            raise TypeError("Unsupported type for show()")


# Quelques images pré-définies (optionnel)
Microbit.Image.HEART = Microbit.Image.fromRows([
    "09090",
    "99999",
    "99999",
    "09990",
    "00900",
])

Microbit.Image.HEART = Microbit.Image.fromRows([
    "09090",
    "99999",
    "99999",
    "09990",
    "00900",
])

Microbit.Image.HEART_SMALL = Microbit.Image.fromRows([
    "00000",
    "09090",
    "09990",
    "00900",
    "00000",
])

Microbit.Image.HAPPY = Microbit.Image.fromRows([
    "00000",
    "09090",
    "00000",
    "90009",
    "09990",
])

Microbit.Image.SAD = Microbit.Image.fromRows([
    "00000",
    "09090",
    "00000",
    "09990",
    "90009",
])


mbSync()
"""


class Microbit():
  def execute_(self, command):
    self.device_.addCommand(f"Microbit.Display.{command}")
    
  def __init__(self, device=None, extra=True):
    self.init(device=device, extra=extra)
    
  def init(self, device=None, extra=True):
    self.device_ = getDevice(device=device)
    self.device_.addCommand(MB_SCRIPT_)
    self.matrix_ = [[0] * 5 for _ in range(5)]
    self.flash()
    
  def clear(self):
    for x in range(5):
      for y in range(5):
        self.matrix_[x][y] = 0
    self.execute_("clear()")
    
  def setPixel(self, x, y, level):
    self.matrix_[x][y] = level
    self.execute_(f'setPixel({x}, {y}, {level})')
    
  def getPixel(self, x, y):
    return self.matrix_[x][y]
  
  def showText(self, text, delay=150):
    self.execute_(f'showText("{text}", {delay})')
    
  def flash(self):
    self.execute_("""show(Microbit.Image.fromRows([
  "99999",
  "99999",
  "99999",
  "99999",
  "99999",
]))
""")
    time.sleep(FLASH_DELAY_)
    self.clear()

##### End of section dedicated to micro:bit #####

##### Begin of generic section for kits #####

class kit_: # Act as namespace.
  @staticmethod
  def ensureSequence_(component):
    return component if isinstance(component, Multi) else (component, )
    
  class WS2812(globals()["WS2812"]):  # Workaround to Brython issue     
    def write(self):
      super().write(lambda color: f"(wc_({color}))")
      return self
    
  class Buzzer(globals()["Buzzer"]):  # Workaround to Brython issue 'https://github.com/brython-dev/brython/issues/2662'.
    pass
      
  class HD44780_I2C(globals()["HD44780_I2C"]):  # Workaround to Brython issue 'https://github.com/brython-dev/brython/issues/2662'.

    @staticmethod
    def deepMax_(x):
      return x if not isinstance(x,(list,tuple,set)) else max((kit_.HD44780_I2C.deepMax_(i) for i in x), default=None)

    # - globalMax == -1: same max for all gauges.
    # - globalMax == 0: each gauge has its own max. 
    def displayRingGauges(self, ring, x, y, size, globalMax = False, placeholder=".", addendum="  "):
      result = ""
      pixels = ring.getAll()
      
      if globalMax == -1:
        maxValue = self.deepMax_(pixels)
        
      if len(placeholder) == 0:
        placeholder = " "
        
      if len(placeholder) == 1:
        placeholder = placeholder + " "
        
      if len(placeholder) == 2:
        placeholder = placeholder.rjust(4, placeholder[0])
        
      if len(placeholder) == 3:
        placeholder += " "
        
      for i in range(len(pixels)):
        sub = ""
        
        j = i if i < 4 else 11 - i
        
        if globalMax == 0:
          maxValue = max(pixels[j])
        elif globalMax !=-1:
          maxValue = globalMax
          
        if maxValue == 0:
          maxValue = 1
          
        for k in range(len(pixels[j])):
          gauge = 8 * pixels[j][k] // maxValue
          if gauge == 0 and pixels[j][k] != 0:
            gauge = 1
          sub += placeholder[k] if gauge == 0 else chr(gauge - 1)
        result += sub + ( addendum[0] if i == 3 else addendum[1] if i == 7 else placeholder[3]) 
      
      if x != 0 or y != 0 or len(result) % size:
        for l in len(result) // size:
          self.moveTo(x, y + l).putString(result[l * size][:size])
      else:
        self.moveTo(0,0).putString(result)
      
      return self
    
    def ttyWrite(self, text, delay = .2, hideCursorOnEnd = True):
      limit = len(text) - 1 if hideCursorOnEnd else -1 
      
      for i in range(len(text)):
        self.putString(text[i][:1])
        if i >= limit:
          self.hideCursor()
        self.getDevice().sleep(delay)
        
      return self
      
  class SSD1306_I2C(globals()["SSD1306_I2C"]):  # Workaround to Brython issue 'https://github.com/brython-dev/brython/issues/2662'.
    pass
  
  class Servo180(Servo):
    def __init__(self, pin, rest, smooth=False, device=None, extra=True):
      self.rest_ = rest
      pwm = PWM(pin, freq=50, device=device, extra=extra, convPin = lambda pin : f"(sp_({pin}))", convU16 = lambda u16: f"(su_({u16}))", convNS = lambda ns: f"(sn_({ns}))")
      super().__init__(pwm, Servo.Specs(1638, 8192, 180), smooth=smooth)
      self.flash()

    def park(self):
      self.setSmooth(self.rest_)


def BaseClassPatch_(caller, owner):
#  return caller if caller != owner else owner.__base__
  return caller if caller != owner else owner.__bases__[0] # Workaround to Brython issue 'https://github.com/brython-dev/brython/issues/2663'.

##### End of generic section for kits #####

##### Begin of section dedicated to the Ravel kit #####

class Ravel:
  @staticmethod
  def init_(create, object, instanciation):
    return object if object is not None else (instanciation() if create else None)
    
  def __init__(self, ringOffset=0, device=None, extra=True, *, buzzer=None, ring=None, oled=None, lcd=None, upper=None, lower=None, create = None):
    if create is None:
      create =  all(x is None for x in (buzzer, ring, oled, lcd, upper, lower))

    cls = self.__class__
    self.buzzer_ = cls.init_(create, buzzer, lambda : ravel.Buzzer(device, extra))
    self.ring_ = cls.init_(create, ring, lambda : ravel.Ring(ringOffset, device, extra))
    self.oled_ = cls.init_(create, oled, lambda : ravel.OLED(device, extra))
    self.lcd_ = cls.init_(create, lcd, lambda : ravel.LCD(device, extra))
    self.upper_ =  cls.init_(create, upper, lambda : ravel.Upper(False, device, extra))
    self.lower_ =  cls.init_(create, lower, lambda : ravel.Lower(False, device, extra))
    
  def raz(self):
    self.__init__(self.ring_.getOffset())
    
  def buzzer(self):
    return self.buzzer_
  
  def ring(self):
    return self.ring_
  
  def oled(self):
    return self.oled_
  
  def lcd(self):
    return self.lcd_

  def upper(self):
    return self.upper_
  
  def lower(self):
    return self.lower_
  
  def get(self, list):

    components = []

    for item in list:
      match item.upper():
        case "B":
          components.append(self.buzzer())
        case "L":
          components.append(self.lcd())
        case "O":
          components.append(self.oled())
        case "R":
          components.append(self.ring())
        case "S":
          components.extend([self.upper(), self.lower()])
        case _:
          raise ValueError(f"Unknown '{item}' component!")
        
    return components


  def displayRingGauges(self, globalMax = 0, placeholder=".", addendum="  "):
    ravel.displayRingGauges(kit_.ensureSequence_(self.ring_), kit_.ensureSequence_(self.lcd_), globalMax, placeholder, addendum)
    

class ravel_:  # act as namespace
  class Upper(kit_.Servo180):
    def __init__(self, smooth=False, device=None, extra=True):
      super().__init__(0, ravel.SERVO_MAX, smooth, device, extra)
    
    def flash(self):
      self.setSmooth(ravel.SERVO_MAX - 500)
      self.park()
  
  class Lower(kit_.Servo180):
    def __init__(self, smooth=False, device=None, extra=True):
      super().__init__(1, 0, smooth, device, extra)
    
    def flash(self):
      self.setSmooth(500)
      self.park()


class ravel:  # act as namespace
  @staticmethod
  def displayRingGauges(rings, lcds, globalMax, placeholder, addendum):
    for ring in rings:
      lcds[rings.index(ring)].displayRingGauges(ring, 0, 0, 16, globalMax, placeholder, addendum)
  
  class Buzzer(kit_.Buzzer):
    def __new__(cls, device=None, extra=True):
      return super().__new__(BaseClassPatch_(cls, ravel.Buzzer), PWM(5, device=device), extra=extra)
      
  class Ring(kit_.WS2812):
    def __new__(cls, offset=0, device=None, extra=True):
      return super().__new__(BaseClassPatch_(cls, ravel.Ring), 8, 20, offset=offset, device=device, extra=extra)
    
  class OLED(kit_.SSD1306_I2C):
    def __new__(cls, device=None, extra=True):
      return super().__new__(BaseClassPatch_(cls, ravel.OLED), 128, 64, I2C(10, 9, device=device), extra=extra)
      
  class LCD(kit_.HD44780_I2C):
    def __new__(cls, device=None, extra=True):
      return super().__new__(BaseClassPatch_(cls, ravel.LCD), 16, 2, SoftI2C(6, 7, device=device), extra=extra)
    
  class Upper(ravel_.Upper):
    def __new__(cls, smooth=False, device=None, extra=True):
      return super().__new__(BaseClassPatch_(cls, ravel.Upper), smooth=smooth, device=device, extra=extra)
    
  class Lower(ravel_.Lower):
    def __new__(cls, smooth=False, device=None, extra=True):
      return super().__new__(BaseClassPatch_(cls, ravel.Lower), smooth=smooth, device=device, extra=extra)
    
  @staticmethod
  def get(list):

    components = []

    for item in list:
      match item.upper():
        case "B":
          components.append(ravel.Buzzer())
        case "L":
          components.append(ravel.LCD())
        case "O":
          components.append(ravel.OLED())
        case "R":
          components.append(ravel.Ring())
        case "S":
          components.extend([ravel.Upper(), ravel.Lower()])
        case _:
          raise ValueError(f"Unknown '{item}' component!")
        
    return components

  @staticmethod
  def raz():
    Ravel()
    
  SERVO_MAX = 6554
  RING_MAX = 31
  RING_SIZE = 8
  OLED_WIDTH = 128
  OLED_HEIGHT = 64
  OLED_BLACK = 0
  OLED_WHITE = 1
  LCD_WIDTH = 16
  LCD_HEIGHT = 2

##### End of section dedicated to the Ravel kit #####

START_SCRIPTS_ = (
  "import deflate, io",
  "gc.collect()",
  SLEEP_WAIT_SCRIPT_,
  NTP_SCRIPT_,
  WOKWI_KIT_PATCH_SCRIPT_,
  OLED_SCRIPT
)
