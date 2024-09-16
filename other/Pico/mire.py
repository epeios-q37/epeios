LEDS = {
    "A": (4,5,6),
    "B": (5,6,7)
}

for led in LEDS:
    print(led, *LEDS[led])
