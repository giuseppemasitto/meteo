import time
from datetime import datetime
import Adafruit_DHT
import RPi.GPIO as GPIO
import requests

class Server:
	def __init__ (self, arg1, arg2):
		self.sensor = arg1
		self.pin = arg2
		self.continueToLoop = True
		self.action = "empty"
		self.humidity = None
		self.temperature = None
		self.rain = 1
	
	def __del__(self):
		GPIO.cleanup()
		
	def waitForCommand(self):
		while self.continueToLoop:
			self.action = raw_input("<command> ")
			
			if self.action == "status":
				self.Server_Print_CustomMessage("Server is running")
			elif self.action == "exit":
				self.Server_Print_CustomMessage("Server exiting")
				self.continueToLoop = False
			if self.action == "update":
				self.Server_Update_Sensor()
			elif self.action == "humidity":
				self.Server_Get_Humidity()
			if self.action == "temperature":
				self.Server_Get_Temperature()
			elif self.action == "rain":
				self.Server_Get_Rain()
			if self.action == "empty":
				self.Server_Print_CustomMessage("Invalid command")
			elif self.action == "":
				self.Server_Print_CustomMessage("Invalid command")
			if self.action == "upload":
				self.Server_Upload_Data()
				
	def Server_Print_CustomMessage(self, arg1):
		print('[MESSAGE] ['+datetime.now().strftime('%d-%m-%Y %H:%M:%S')+']: '+arg1)
		
	def Server_Update_Sensor(self):
		self.Server_Print_CustomMessage("Server is updating data...")
		
		self.humidity, self.temperature = Adafruit_DHT.read_retry(self.sensor, self.pin)
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(18, GPIO.IN)
		self.rain = GPIO.input(18)
		
		self.Server_Print_CustomMessage("Data updated")

	def Server_Get_Humidity(self):
		if self.humidity is not None:
			self.Server_Print_CustomMessage('The humidity is {0:0.1f}%'.format(self.humidity))
		else:
			self.Server_Print_CustomMessage('Failed to get reading. Try again!')
	
	def Server_Get_Temperature(self):
		if self.temperature is not None:
			self.Server_Print_CustomMessage('The temperature is {0:0.1f} *C'.format(self.temperature))
		else:
			self.Server_Print_CustomMessage('Failed to get reading. Try again!')
	
	def Server_Get_Rain(self):
		if (self.rain == 0):
			self.Server_Print_CustomMessage('Rain detected')
		else:
			self.Server_Print_CustomMessage('No rain detected')
			
	def Server_Upload_Data(self):
		self.Server_Print_CustomMessage('Server is starting to upload datas to database...')
		payload = {'time':datetime.now().strftime('%d-%m-%Y %H:%M:%S'), 'location':'Capo dOrlando', 'temperature':'{0:0.1f}'.format(self.temperature), 'humidity':'{0:0.1f}'.format(self.humidity), 'rain':self.rain}
		r = requests.get("http://quajetri.it/upload.php", params=payload)
		# print(r.url)

		if r.status_code == 200:
			self.Server_Print_CustomMessage('Done!')
			# print(r.text[:300] + '...')
		else:
			self.Server_Print_CustomMessage('Error!')
