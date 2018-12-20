# indica al sistema quale versione di python da utilizzare
#!/usr/bin/env python2.7

# importa le librerie di sistema
import sys
import requests
from datetime import datetime
from crontab import CronTab

# importa le librerie per i sensori
import Adafruit_DHT
import Adafruit_BMP.BMP085 as BMP085
import RPi.GPIO as GPIO

# importa la libreria per la connessione al server MySQL
import mysql.connector as database

# crediti
__author__ = "Giuseppe Masitto"
__copyright__ = "Copyright 2018, mazinthebox"
__credits__ = ["Giuseppe Masitto", "Andrea Germana'"]
__license__ = "MIT License"
__version__ = "1"
__maintainer__ = "mazinthebox"
__email__ = "info@giuseppemasitto.com"
__status__ = "Production"

# Classe: 	Server
# Variabili:	rain_sensor_pin
#		temperature_humidity_sensor_pin
#		rain
#		temperature
#		humidity
#		pressure
#		database_user
#		database_password
#		database_database
#		php_key
#		php_handler
# Funzioni:	__init__
#		__del__
#		Server_Update
#		Server_Upload
#		Server_Sync
#		Server_Live
# Descrizione:	La classe Server fornisce metodi per l'aggiornamento dei dati raccolti dai sensori ed
#		il caricamento dei dati sui server MySQL (MariaDB in locale, MySQL in remoto)
		
class Server:
	# Metodo: 	Costruttore
	# Descrizione: 	Inizializza i pin di lettura per i sensori e definisce le variabili di ambiente
	# Informazioni: Per la gestione GPIO puoi consultare https://it.pinout.xyz/
	def __init__ (self):
		# numero pin per il sensore pioggia
		self.rain_sensor_pin = 18
		# numero pin per i sensori temperatura e umidità
		self.temperature_humidity_sensor_pin = 4
		# inizializza le variabili per i sensori
		self.rain = None
		self.temperature = None
		self.humidity = None
		self.pressure = None
		# inizializza le variabili per la connessione al server locale mysql
		self.database_user = "username"
		self.database_password = "password"
		self.database_database = "database"
		# dichiara la variabile chiave di sicurezza per l'esecuzione delle query
		self.php_key = "chiave di sicurezza"
		# imposta l'indirizzo completo al file meteo_handler.php
		self.php_handler = "full/path/to/meteo_handler.php"
	
	# Funzione: 	Decostruttore
	# Descrizione: 	Libera le risorse GPIO se sono state inizializzate
	# Informazioni: ///
	def __del__(self):
		GPIO.cleanup()
	
	# Funzione: 	Server_Update()
	# Descrizione: 	Aggiorna le variabili con i dati letti dai sensori
	# Informazioni:	///
	def Server_Update(self):
		self.humidity, self.temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT22, self.temperature_humidity_sensor_pin)
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(self.rain_sensor_pin, GPIO.IN)
		self.rain = GPIO.input(self.rain_sensor_pin)
		sensor = BMP085.BMP085()
		sensor = BMP085.BMP085(mode=BMP085.BMP085_ULTRAHIGHRES)
		self.pressure = sensor.read_pressure()
	
	# Funzione: 	Server_Upload()
	# Descrizione: 	Inserisce nel database mysql locale i valori dei sensori
	# Informazioni:	///
	def Server_Upload(self):
		connection = database.connect(user=self.database_user, password=self.database_password, database=self.database_database)
		cursor = connection.cursor()
		cursor.execute("INSERT INTO record (data, pioggia, temperatura, umidita, pressione, vento) VALUES ({}, {}, {}, {}, {}, {})".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), self.rain, '{0:0.1f}'.format(self.temperature), '{0:0.1f}'.format(self.humidity), self.pressure, ""))
		connection.commit()
		connection.close()
		
	# Funzione: 	Server_Sync()
	# Descrizione: 	Sincronizza il server remoto con il server locale
	# Informazioni:	///
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
	
	# Funzione: 	Server_Live()
	# Descrizione: 	Inserisce nel database mysql remoto i dati aggiornati in tempo reale
	# Informazioni:	///
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

# avvia i service del Server
# controlla se l'argomento passato è per la gestione dei CronJob
if (arg == "start"):
	scheduler = CronTab(user='pi')
	# Job: 		invia
	# Descrizione: 	Richiama la funzione Server_Upload()
	# Ripetizione:	Richiama la funzione ogni 30 minuti
	job_invia = scheduler.new(command='python /home/pi/meteo_hub/meteo_service.py invia', comment='invia')
	job_invia.minute.every(30)
	# Job: 		sincronizza
	# Descrizione: 	Richiama la funzione Server_Sync()
	# Ripetizione:	Richiama la funzione ogni 6 ore
	job_sincronizza = scheduler.new(command='python /home/pi/meteo_hub/meteo_service.py sincronizza', comment='sincronizza')
	job_sincronizza.hour.every(6)
	# Job: 		live
	# Descrizione: 	Richiama la funzione Server_Live()
	# Ripetizione:	Richiama la funzione ogni 15 minuti
	job_live = scheduler.new(command='python /home/pi/meteo_hub/meteo_service.py live', comment='live')
	job_live.minute.every(15)
	# salva i CronJob
	scheduler.write()
# ferma i service del Server
elif (arg == "stop"):
	scheduler = CronTab(user='pi')
	for job in scheduler:
		if (job.comment == 'invia'):
			# rimuove il job 'invia' dalla lista dei CronJob
			scheduler.remove(job)
		elif (job.comment == 'sincronizza'):
			# rimuove il job 'sincronizza' dalla lista dei CronJob
			scheduler.remove(job)
		if (job.comment == 'live'):
			# rimuove il job 'live' dalla lista dei CronJob
			scheduler.remove(job)
	# salva i CronJob
	scheduler.write()
	
# controlla se l'argomento passato è per la gestione dei CronJob programmati
if (arg == "invia"):
	handler.Server_Upload()
elif (arg == "sincronizza"):
	handler.Server_Sync()
if (arg == "live"):
	handler.Server_Live()
# controlla se l'argomento passato è per la visualizzazione dei dati da riga di comando
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
