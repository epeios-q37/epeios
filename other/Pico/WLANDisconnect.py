# For testing purpose. Disconnect the microcontroller from WiFi.
import network

sta_if = network.WLAN(network.STA_IF)

if sta_if.isconnected():
    sta_if.disconnect()

    while sta_if.status() != network.STAT_IDLE:
        pass    
