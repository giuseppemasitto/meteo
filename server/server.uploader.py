from server import Server

import Adafruit_DHT

handler = Server(Adafruit_DHT.DHT22, 4)
handler.Server_Update_Sensor()
handler.Server_Upload_Data()

del handler
