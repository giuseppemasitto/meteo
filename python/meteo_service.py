#!/usr/bin/env python2.7

import sys
import requests
from datetime import datetime
from crontab import CronTab

import Adafruit_DHT
import Adafruit_BMP.BMP085 as BMP085
import RPi.GPIO as GPIO

import mysql.connector as database

__author__ = "Giuseppe Masitto"
__copyright__ = "Copyright 2018, mazinthebox"
__credits__ = ["Giuseppe Masitto", "Andrea Germana'"]
__license__ = "MIT License"
__version__ = "1"
__maintainer__ = "mazinthebox"
__email__ = "info@giuseppemasitto.com"
__status__ = "Production"

class Server:
	# funzione: Costruttore
	# descrizione: inizializza i pin di lettura per i sensori, definisce le variabili di ambiente
	# informazioni: per la gestione gpio puoi consultare https://it.pinout.xyz/
	def __init__ (self):
		# numero pin per il sensore pioggia
		self.rain_sensor_pin = 18
		# numero pin per i sensori temperatura e umidità
		self.temperature_humidity_sensor_pin = 4
		# inizializza le variabili per i dati
		self.rain = None
		self.temperature = None
		self.humidity = None
		self.pressure = None
		
		# connessione al server locale mysql
		self.database_user = "username"
		self.database_password = "password"
		self.database_database = "database"
		
		# chiave di sicurezza per l'esecuzione delle query
		self.php_key = "chiave di sicurezza"
		# indirizzo completo php handler
		self.php_handler = "full/path/to/meteo_handler.php"
	
	# funzione: Decostruttore
	# descrizione: libera risorse gpio
	def __del__(self):
		GPIO.cleanup()
	
	# funzione: Server_Update()
	# commento: aggiorna le variabili con i dati letti dai sensori
	def Server_Update(self):
		self.humidity, self.temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT22, self.temperature_humidity_sensor_pin)
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(self.rain_sensor_pin, GPIO.IN)
		self.rain = GPIO.input(self.rain_sensor_pin)
		sensor = BMP085.BMP085()
		sensor = BMP085.BMP085(mode=BMP085.BMP085_ULTRAHIGHRES)
		self.pressure = sensor.read_pressure()
	
	# funzione: Server_Upload()
	# descrizione: inserisce nel database mysql locale i valori dei sensori
	def Server_Upload(self):
		connection = database.connect(user=self.database_user, password=self.database_password, database=self.database_database)
		cursor = connection.cursor()
		cursor.execute("INSERT INTO record (data, pioggia, temperatura, umidita, pressione, vento) VALUES ({}, {}, {}, {}, {}, {})".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), self.rain, '{0:0.1f}'.format(self.temperature), '{0:0.1f}'.format(self.humidity), self.pressure, ""))
		connection.commit()
		connection.close()
		
	# funzione: Server_Sync()
	# descrizione: sincronizza il server remoto con il server locale
	def Server_Sync(self):
		payload = {'key':self.php_key, 'action':"requestid"}
		r = requests.get(self.php_handler, params=payload)
		connection = database.connect(user=self.database_user, password=self.database_password, database=self.database_database)
		cursor = connection.cursor()
		cursor.execute("SELECT * FROM record WHERE id > {}".format(r.text))
		result_from_all = cursor.fetchall()
		query = "INSERT INTO record (id, data, pioggia, temperatura, umidita, pressione, vento) VALUES "
		for row in result_from_all:
			query = query + "({},'{}','{}','{}','{}','{}','{}'),".format(row[0], row[1], row[2], row[3], row[4], row[5], "")

		cursor.execute("SELECT * FROM record ORDER BY id DESC LIMIT 1")
		result_from_one = cursor.fetchone()
		query = query[:-1] + "; ALTER TABLE record MODIFY id int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT={};".format(int(result_from_one[0])+1)
		connection.commit()
		connection.close()
		payload = {'key':self.php_key, 'action':"sync", 'query':query}
		r = requests.get(self.php_handler, params=payload)
	
	# funzione: Server_Live()
	# descrizione: inserisci nel database mysql remoto i dati aggiornati in tempo reale
	def Server_Live(self):
		query = "UPDATE record_live SET data='{}',pioggia='{}',temperatura='{}',umidita='{}',pressione='{}',vento='{}' WHERE id=1".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), self.rain, '{0:0.1f}'.format(self.temperature), '{0:0.1f}'.format(self.humidity), self.pressure, "")
		payload = {'key':self.php_key, 'action':"live", 'query':query}
		r = requests.get(self.php_handler, params=payload)


# ottieni gli argomenti da riga di comando
arg = sys.argv[1]
# inizializza il server
handler = Server()
# aggiorna e prepara i dati
handler.Server_Update()

# starta i service del server
if (arg == "start"):
	scheduler = CronTab(user='pi')
	# invia: Server_Upload() ogni 30 minunti
	job_invia = scheduler.new(command='python /home/pi/meteo_hub/meteo_service.py invia', comment='invia')
	job_invia.minute.every(30)
	# sincronizza: Server_Sync() ogni 6 ore
	job_sincronizza = scheduler.new(command='python /home/pi/meteo_hub/meteo_service.py sincronizza', comment='sincronizza')
	job_sincronizza.hour.every(6)
	# live: Server_Live() ogni 15 minuti
	job_live = scheduler.new(command='python /home/pi/meteo_hub/meteo_service.py live', comment='live')
	job_live.minute.every(15)
	# salva i CronJob
	scheduler.write()
# stoppa i service del server
elif (arg == "stop"):
	scheduler = CronTab(user='pi')
	for job in scheduler:
		if (job.comment == 'invia'):
			scheduler.remove(job)
		elif (job.comment == 'sincronizza'):
			scheduler.remove(job)
		if (job.comment == 'live'):
			scheduler.remove(job)
	scheduler.write()
if (arg == "invia"):
	handler.Server_Upload()
elif (arg == "sincronizza"):
	handler.Server_Sync()
if (arg == "live"):
	handler.Server_Live()
elif (arg == "pioggia"):
	print(handler.rain);
if (arg == "temperatura"):
	print('{0:0.1f}'.format(handler.temperature));
elif (arg == "umidita"):
	print(handler.humidity);
if (arg == "pressione"):
	print(handler.pressure);

# libera le risorse
del handler
