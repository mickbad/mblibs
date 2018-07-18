#!/usr/bin/python3
# ----------------------------------------------------------------------
#  Librairie Outils
# ----------------------------------------------------------------------
"""
	Fast tools for programming

	Usage:
	>>> from mblibs.fast import FastSettings
	>>> settings = FastSettings("/path/to/yaml_or_json")
"""

# compatabilité 
from __future__ import print_function

# libs
import os
import sys
import time
import datetime

__all__ = ["FastSettings", "FastLogger", "FastEmail", "FastThread"]


# ----------------------------------------------------------------------
# Outils de configuration
# ----------------------------------------------------------------------

# libs
import json
import codecs

# ----------------------------------------------------------------------
class FastSettings(object):
	# ----------------------------------------------------------------------
	""" object de gestion des configuraitons """
	def __init__(self, config_filename):
		super(FastSettings, self).__init__()
		self.config_filename = config_filename

		# vérification d'usage
		if not os.path.isfile(self.config_filename):
			# le fichier n'existe pas !
			raise Exception( "{}: not exists!".format(self.config_filename) )

		# - lecture des données de configuration
		self.reload()

	# ----------------------------------------------------------------------
	def reload(self):
		""" 
			fonction de chargement automatique de la configuration
			depuis le fichier extérieur
		"""
		# lecture du fichier de configuration en mode UTF-8
		try:
			# content = open(self.config_filename).read()
			content = codecs.open(self.config_filename, "r", "utf8").read()

		except Exception as e:
			raise Exception( "{}: json/yaml settings error reading: {}".format(self.config_filename, e) )

		# interprétation des données
		error_str = ""
		error_reading_json, error_reading_yaml = False, False
		try:
			self.settings = json.loads(content)
		except Exception as e:
			error_str = e
			error_reading_json = True

		if error_reading_json:
			try:
				import yaml
				self.settings = yaml.load(content.replace("\t", "  "))
			except Exception as e:
				error_str = e
				error_reading_yaml = True

		if error_reading_json and error_reading_yaml:
			raise Exception( "{}: json/yaml settings incorrect: {}".format(self.config_filename, error_str) )

	# ----------------------------------------------------------------------
	# Récupération d'une configuration
	def get(self, name, default = "", __settings_temp = None):
		""" 
			Récupération d'une configuration 
			le paramètre ```name``` peut être soit un nom ou 
			un chemin vers la valeur (séparateur /)

			```__settings_temp``` est le dictionnaire temporaire de 
			transmission récursif (intégrant les sous configurations)

			exemple :
				valeur = self.settings("document/host/val", "mon_defaut")
				valeur = self.settings("/document/host/val", "mon_defaut")
		"""
		# configuration des settings temporaire pour traitement local
		if __settings_temp is None:
			__settings_temp = self.settings

		# check si le chemin commence par / auquel cas on le supprime
		if name.startswith("/"):
			name = name[1:]

		# check s'il s'agit d'un chemin
		if "/" in name:
			# récupération du nom de la sous configuraiton
			name_master = name.split("/")[0]
			if name_master not in __settings_temp.keys():
				return default

			# récupération de la sous configuration
			__settings_temp = __settings_temp[name_master]
			return self.get("/".join(name.split("/")[1:]), default, __settings_temp)

		# check de la précense de la clef
		if name not in __settings_temp.keys():
			# le hash du magazine n'est pas présent !
			return default

		# récupération de la valeur
		value = __settings_temp[name]

		# trim si value est un str
		if isinstance(value, str):
			value = value.strip()

		# retour de la valeur
		return value

	# ---------------------------------------------------------
	def getInt(self, name, default=0):
		""" récupération d'un élément entier """
		try:
			value = self.get(name, default)
			return int(value)

		except:
			# pas de configuration trouvé ou convertion impossible ?
			return default

	# ---------------------------------------------------------
	def getEnable(self, name, default=False):
		""" récupération d'un élément vrai ou faux (transformation en bool) """
		# valeur
		value = self.get(name, default)
		if type(value) != str:
			return (value == 1 or value)

		# test de retour
		return value.lower() in ["true", "t", "1", "oui", "vrai", "v", "on", "o", "yes", "y", "si", "s", "da", "d", "ja", "j"]

	# ---------------------------------------------------------
	def getWithDateFormat(self, name, default=""):
		""" 
			récupération d'un élément de configuration et interprétation des valeurs de dates
			variables acceptés : {dd}, {mm}, {yyyy}, {H}, {M} et {S}
			{mm_human} donne le nom du mois
		"""
		# récupation de la valeur
		now = datetime.datetime.now()
		tomorrow = now + datetime.timedelta(days=1)
		yesterday = now + datetime.timedelta(days=-1)
		return self.get(name, default).format(
			yyyy=now.year,
			mm=now.strftime("%m"),
			dd=now.strftime("%d"),
			H=now.strftime("%H"),
			M=now.strftime("%M"),
			S=now.strftime("%S"),
			mm_human=now.strftime("%B"),

			tomorrow_yyyy=tomorrow.year,
			tomorrow_mm=tomorrow.strftime("%m"),
			tomorrow_dd=tomorrow.strftime("%d"),
			tomorrow_H=tomorrow.strftime("%H"),
			tomorrow_M=tomorrow.strftime("%M"),
			tomorrow_S=tomorrow.strftime("%S"),
			tomorrow_mm_human=tomorrow.strftime("%B"),

			yesterday_yyyy=yesterday.year,
			yesterday_mm=yesterday.strftime("%m"),
			yesterday_dd=yesterday.strftime("%d"),
			yesterday_H=yesterday.strftime("%H"),
			yesterday_M=yesterday.strftime("%M"),
			yesterday_S=yesterday.strftime("%S"),
			yesterday_mm_human=yesterday.strftime("%B"),
		)

	# ----------------------------------------------------------------------
	# Définition d'un texte pour le cord du message
	def getFileFormat(self, name, args):
		""" Récupération du contenu d'un fichier via la configuration
			et interprétation des variables données en argument """
		# récupération du nom du fichier
		template_pathname = self.get(name, "--")
		if not os.path.isfile(template_pathname):
			return False

		# configuration
		content = ""
		with open(template_pathname) as fp:
			# Create a text/plain message
			content = fp.read().format(**args)

		# retour ok
		return content



# ----------------------------------------------------------------------
# Outils Logging
# ----------------------------------------------------------------------

# libs
import logging
from logging.handlers import TimedRotatingFileHandler
from logging.handlers import RotatingFileHandler

# ----------------------------------------------------------------------
class FastLogger(object):
	# ----------------------------------------------------------------------
	""" Constructeur du système Log """
	def __init__(self, log_name, log_pathlog, rotate_log_mode=None, rotate_log_count=5):
		"""
			Possibilité de mettre une rotation automatique du log
			suivant le paramètre ```rotate_log_mode```

			Ce paramètre accepte les valeurs suivantes
				<int>		nombre de bytes avant rotation
				'S'			Seconds
				'M'			Minutes
				'H'			Hours
				'D'			Days
				'W'			Week day (0=Monday) w0-w6 (weekday, 0=Monday)
				'midnight'	Roll over at midnight
				'stdout'    redirect log to stdout
		"""
		super(FastLogger, self).__init__()

		# # check arguments
		if not os.path.isdir(log_pathlog):
			raise Exception("{}: not a valid directory".format(log_pathlog))

		# sauvegarde des arguments
		self.name = log_name
		self.pathlog = log_pathlog
		self.filename = "{}/{}.log".format(log_pathlog, log_name)

		# préfixe
		self.setPrefix()

		# Système de log
		self.logger = logging.getLogger(self.name)
		self.setLevel("INFO")

		# système de rotation
		if rotate_log_mode in ["S", "M", "H", "D", "W", "midnight"]:
			handler = TimedRotatingFileHandler(self.filename,
												when=rotate_log_mode,
												interval=1,
												backupCount=rotate_log_count)

		elif type(rotate_log_mode) == int:
			# rotation par la taille en bytes
			handler = RotatingFileHandler(self.filename, maxBytes=rotate_log_mode, backupCount=5)

		elif rotate_log_mode.lower() == "stdout":
			handler = logging.StreamHandler()

		else:
			handler = logging.FileHandler(self.filename)

		# format du log
		formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
		handler.setFormatter(formatter)
		self.logger.addHandler(handler)

	# ----------------------------------------------------------------------
	def setPrefix(self, text = ""):
		""" mise en place d'un préfixe à chaque écriture de message """
		if len(text) > 0:
			self.message_prefix = "{}: ".format(text)
		else:
			self.message_prefix = ""


	# ----------------------------------------------------------------------
	def setLevel(self, level):
		""" Changement du niveau du Log """
		if isinstance(level, int):
			self.logger.setLevel(level)
			return

		# level en tant que string
		level = level.lower()
		if level == "debug":
			self.logger.setLevel( logging.DEBUG )

		elif level == "info":
			self.logger.setLevel( logging.INFO )

		elif level == "warning" or level == "warning":
			self.logger.setLevel( logging.WARN )

		elif level == "error":
			self.logger.setLevel( logging.ERROR )

		else:
			# par défaut
			self.logger.setLevel( logging.INFO )

	# ----------------------------------------------------------------------
	def info(self, text):
		""" Ajout d'un message de log de type INFO """
		self.logger.info( "{}{}".format(self.message_prefix, text) )

	# ----------------------------------------------------------------------
	def debug(self, text):
		""" Ajout d'un message de log de type DEBUG """
		self.logger.debug( "{}{}".format(self.message_prefix, text) )

	# ----------------------------------------------------------------------
	def warn(self, text):
		""" Ajout d'un message de log de type WARN """
		self.logger.warn( "{}{}".format(self.message_prefix, text) )

	# ----------------------------------------------------------------------
	def warning(self, text):
		""" Ajout d'un message de log de type WARN """
		self.logger.warning( "{}{}".format(self.message_prefix, text) )

	# ----------------------------------------------------------------------
	def error(self, text):
		""" Ajout d'un message de log de type ERROR """
		self.logger.error( "{}{}".format(self.message_prefix, text) )


# ----------------------------------------------------------------------
# Outils emailing
# ----------------------------------------------------------------------

# Import smtplib for the actual sending function
import smtplib

# Import the email modules we'll need
from email.mime.text import MIMEText

# ----------------------------------------------------------------------
class FastEmail(object):
	""" Gestionnaire d'envoi de mail vers un destinataire avec un texte préformatée """
	# ----------------------------------------------------------------------
	def __init__(self):
		super(FastEmail, self).__init__()

		# initialisation
		self.mail_from = "contact@fs-dev.com"
		self.mail_subject = "Message inconnu"
		self.mail_text = "Message inconnu"
		self.mail_html = "<h2>Message inconnu</h2>"
		
	# ----------------------------------------------------------------------
	# Définition d'un texte pour le cord du message
	def setHTML_from_file(self, filename, args):
		""" Définition d'un texte pour le cord du message """
		# vérification d'usage
		if not os.path.isfile(filename):
			return False

		with open(filename) as fp:
			# Create a text/plain message
			self.mail_html = fp.read().format(**args)

		# retour ok
		return True

	# ----------------------------------------------------------------------
	# Envoi de l'email préformaté
	def send_email(self, to):
		""" Envoi de l'email préformaté """
		# Create a text/plain message
		msg = MIMEText(self.mail_html, "html", "utf-8")

		# Configuration des informations de l'email
		msg['Subject'] = self.mail_subject
		msg['From'] = self.mail_from
		msg['To'] = to

		# Send the message via our own SMTP server.
		s = smtplib.SMTP('localhost')
		s.send_message(msg)
		s.quit()


# ----------------------------------------------------------------------
# Gestion du multithreading
# ----------------------------------------------------------------------

# libs
import threading

# ----------------------------------------------------------------------
class FastThread(threading.Thread):
	"""
	FastThread est un classe rapide de gestion multithreading en python2 et 3

	exemple d'utilisation:

	# fonction de threads
	def thread_runtime_1(threadName, delay, counter):
		pass

	def thread_runtime_2(delay, text):
		pass

	def thread_runtime_noargs():
		pass

	# Create new threads
	thread1 = FastThread(10, "thread_runtime_1", threadName = "Thread-1", delay = 1, counter = 5)
	thread2 = FastThread(20, thread_runtime_1, threadName = "Thread-2", delay = 2, counter = 5)
	thread3 = FastThread(30, thread_runtime_noargs)
	thread4 = FastThread(40, thread_runtime_2, 3, "killall thread")

	# Start new Threads
	thread1.start()
	thread2.start()
	thread3.start()
	thread4.start()

	# Join all thread and waiting end
	thread1.join()
	thread2.join()
	thread3.join()
	thread4.join()
	"""
	# ----------------------------------------------------------------------
	# Constructeur par défaut
	def __init__(self, threadID, function, *args, **kwargs):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.function = function
		self.args     = args
		self.kwargs   = kwargs

		# debug mode
		self.debug    = False

	# ----------------------------------------------------------------------
	# Surcharge du fonctionnement du thread
	def run(self):
		""" Fonctionnement du thread """
		if self.debug:
			print ("Starting " + self.name)

		# Lancement du programme du thread
		if isinstance(self.function, str):
			globals()[self.function](*self.args, **self.kwargs)
		else:
			self.function(*self.args, **self.kwargs)

		if self.debug:
			print ("Exiting " + self.name)
