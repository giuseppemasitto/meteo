from server import Server

import Adafruit_DHT

handler = Server(Adafruit_DHT.DHT22, 4)

handler.Server_Print_CustomMessage("commands [status exit update upload humidity temperature rain]")
handler.Server_Print_CustomMessage("to use humidity, temperature, rain and upload use update before")
handler.waitForCommand()

del handler
