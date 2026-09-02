import math

import ucuq

from show import sleepUntil as sleepUntil_


def animateLoopingBouncingBall_(fb, width, height, timestamp, bounceCount=3):
  radiusX = 12
  radiusY = 12
  
  maxHeight = height // 2
  amplitude = (height - radiusY) - maxHeight
  
  gravity = 0.6
  vyStart = -math.sqrt(2 * gravity * amplitude)
  
  flightFrames = int(2 * abs(vyStart) / gravity)
  squashFrames = 6
  
  totalFramesPerBounce = flightFrames + squashFrames
  totalFramesTotal = bounceCount * totalFramesPerBounce
  
  startX = -radiusX
  endX = width + radiusX
  distanceToTravel = endX - startX
  
  vx = distanceToTravel / totalFramesTotal
  
  x = startX
  y = maxHeight
  vy = 0.0
  isSquashing = False
  squashTimer = 0
  xImpact = 0.0
  
  for _ in range(198):
    currentRadiusX = radiusX
    currentRadiusY = radiusY
    drawX = x
    
    if isSquashing:
      squashTimer += 1
      progress = squashTimer / squashFrames
      squashFactor = math.sin(progress * math.pi) * 0.4
      
      currentRadiusX = int(radiusX * (1 + squashFactor))
      currentRadiusY = int(radiusY * (1 - squashFactor))
      y = height - currentRadiusY
      
      x += vx
      
      drawX = xImpact + (x - xImpact) * 0.3
      
      if squashTimer >= squashFrames:
        isSquashing = False
        squashTimer = 0
        y = height - radiusY
        vy = vyStart
        
    else:
      vy += gravity
      x += vx
      y += vy
      drawX = x
      
      if y + radiusY >= height:
        isSquashing = True
        squashTimer = 0
        vy = 0
        y = height - radiusY
        xImpact = x
        
    if x >= endX:
      x = startX
      y = maxHeight
      vy = 0.0
      isSquashing = False
      squashTimer = 0
      
    fb.fill(0)
    fb.ellipse(int(drawX), int(y), currentRadiusX, currentRadiusY, 1, True)
    
    fb.show()
      
    timestamp += .05
    sleepUntil_(timestamp, 0)


def launch(timestamp, devices):
  timestamp += 1
  
  sleepUntil_(timestamp, 0)

  timestamp = animateLoopingBouncingBall_(ucuq.OLEDS_Wall((tuple(oled for oled in devices.oleds),)), ucuq.ravel.OLED_WIDTH * 3, ucuq.ravel.OLED_HEIGHT, timestamp)

  return timestamp
