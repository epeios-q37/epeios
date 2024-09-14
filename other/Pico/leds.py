import neopixel, machine

p = machine.Pin(16)

n = neopixel.NeoPixel(p, 4)

# Draw a red gradient.
n[0] = (8,0,0)
n[1] = (0,8,0)
n[2] = (0,0,8)
n[3] = (8,8,8)
# Update the strip.
n.write()