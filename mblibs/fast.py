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
from datetime import datetime
from datetime import timedelta

# objets admis
__all__ = ["FastSettings", "FastLogger", "FastEmail", "FastThread", "FastDate"]


# ----------------------------------------------------------------------
# Outils de configuration
# ----------------------------------------------------------------------

# libs
import re
import json
import codecs

# ----------------------------------------------------------------------
class FastSettings(object):
	# ----------------------------------------------------------------------
	""" object de gestion des configuraitons """
	def __init__(self, config_filename="", config_content=""):
		super(FastSettings, self).__init__()
		self.config_filename = config_filename
		self.config_content = config_content

		# vérification d'usage
		if not os.path.isfile(self.config_filename) and config_content == "":
			# le fichier n'existe pas !
			raise Exception("{}: not exists!".format(self.config_filename))

		# - lecture des données de configuration
		self.reload()

	# ----------------------------------------------------------------------
	def reload(self):
		""" 
			fonction de chargement automatique de la configuration
			depuis le fichier extérieur
		"""
		# lecture du fichier de configuration en mode UTF-8
		if self.config_filename != "":
			try:
				# content = open(self.config_filename).read()
				self.config_content = codecs.open(self.config_filename, "r", "utf8").read()

			except Exception as e:
				raise Exception(
					"{}: json/yaml settings error reading: {}".format(self.config_filename, e))

		# init
		self.is_json = False
		self.is_yaml = False

		# interprétation des données
		error_str = ""
		error_reading_json, error_reading_yaml = False, False
		try:
			self.settings = json.loads(self.config_content)
			self.is_json = True
		except Exception as e:
			error_str = e
			error_reading_json = True

		if error_reading_json:
			try:
				# préservation des duplications de clef
				# https://stackoverflow.com/questions/44904290/getting-duplicate-keys-in-yaml-using-python

				import yaml
				content = self.config_content.replace("\t", "  ")
				self.settings = yaml.load(content)
				self.is_yaml = True

			except Exception as e:
				error_str = e
				error_reading_yaml = True

		if error_reading_json and error_reading_yaml:
			raise Exception(
				"{}: json/yaml settings incorrect: {}".format(self.config_filename, error_str))

	# ----------------------------------------------------------------------
	# Récupération d'une configuration
	def get(self, name, default="", parent_search=False, multikeys_search=False, __settings_temp=None, __rank_recursion=0):
		""" 
			Récupération d'une configuration 
			le paramètre ```name``` peut être soit un nom ou 
			un chemin vers la valeur (séparateur /)

			```parent_search``` est le boolean qui indique si on doit
			chercher la valeur dans la hiérarchie plus haute. Si la chaîne
			"/document/host/val" retourne None, on recherche dans "/document/val"
			puis dans "/val"

			```multikeys_search``` indique si la recherche d'une clef non trouvabe
			se fait sur les parents en multi clef
			ie: /graphic/output/logo/enable va aussi chercher dans /graphic/logo/enable

			```__settings_temp``` est le dictionnaire temporaire de 
			transmission récursif (intégrant les sous configurations)

			```__rank_recursion``` défini le rang de récusion pour chercher aussi
			depuis la racine du chemin en cas de récursion inverse

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

		# check si le chemin termine par / auquel cas on le supprime
		if name.endswith("/"):
			name = name[:-1]

		# check s'il s'agit d'un chemin complet
		if "/" in name:
			# récupération du nom de la sous configuraiton
			name_master = name.split("/")[0]

			# récupération de l'indice si le nom obtenu contient []
			indice_master = -1
			indices_master = re.findall(r"[\d+]", name_master)
			if len(indices_master) > 0:
				try:
					indice_master = int(indices_master[0].replace("[", "").replace("]", ""))
				except:
					pass

			# suppression de l'indice dans le nom du chemin courant (ie: data[0] devient data)
			name_master = name_master.replace("[{}]".format(indice_master), "")

			# recherche si la clef est présente dans le chemin courant
			if name_master not in __settings_temp.keys():
				return None

			# récupération de la sous configuration
			if indice_master < 0:
				# la sous configuration n'est pas une liste
				__settings_temp = __settings_temp[name_master]

			else:
				# la sous configuration est une liste (SI JSON !!)
				__settings_temp = __settings_temp[name_master][indice_master] if self.is_json else __settings_temp[name]

			# recursion sur le chemin en dessous
			name_split = name.split("/")[1:]
			search_path = "/".join(name_split)
			return_value = self.get(
				search_path, default, parent_search, multikeys_search, __settings_temp, __rank_recursion + 1)

			# pas de valeur trouvé, on cherche sur la récursion inverse
			if len(name_split) > 1 and return_value is None:
				i = len(name_split)
				while i >= 0:
					# on décrémente le curseur de recherche
					i -= 1

					# établissement du nouveau chemin en supprimant le niveau supérieur
					new_search_path = "/".join(name_split[i-len(name_split):])
					return_value = self.get(
						new_search_path, default, parent_search, multikeys_search, __settings_temp, __rank_recursion + 1)

					# pas de recherche multi clef
					if not multikeys_search:
						break

					# une valeur a été trouvée
					if not return_value is None:
						break

			# pas de valeur trouvé et on est à la racine du chemin
			if return_value is None and __rank_recursion == 0:
				# on change le nom du master et on cherche
				name = name_split[-1]
				return_value = self.get(
					name, default, parent_search, multikeys_search, self.settings, 0)

				# toujours pas de valeur, on garde le défaut
				if return_value is None:
					return_value = default

			# retour de la valeur récupérée
			return return_value

		# récupération de l'indice si le nom obtenu contient []
		indice_master = -1
		indices_master = re.findall(r"\[\d+\]", name)
		if len(indices_master) > 0:
			try:
				indice_master = int(indices_master[0].replace("[", "").replace("]", ""))
			except:
				pass

		# suppression de l'indice dans le nom du chemin courant (ie: data[0] devient data)
		name = name.replace("[{}]".format(indice_master), "")

		# check de la précense de la clef
		if type(__settings_temp) is str or name not in __settings_temp.keys():
			# le hash n'est pas présent !
			# si la recherche récursive inverse est activée et pas de valeur trouvée,
			# on recherche plus haut
			if parent_search:
				return None

			return default

		# récupération de la valeur
		if indice_master < 0:
			# la sous configuration n'est pas une liste
			value = __settings_temp[name]

		else:
			# la sous configuration est une liste (SI JSON !!)
			value = __settings_temp[name][indice_master] if self.is_json else __settings_temp[name]

		# interdiction de la valeur "None"
		if value is None:
			# si la recherche récursive inverse est activée et pas de valeur trouvée,
			# on recherche plus haut
			if parent_search:
				return None

			# valeur par défaut
			value = default

		# trim si value est un str
		if isinstance(value, str):
			value = value.strip()

		# retour de la valeur
		return value

	# ---------------------------------------------------------
	def getInt(self, name, default=0, parent_search=False, multikeys_search=False):
		""" récupération d'un élément entier """
		try:
			value = self.get(name, default, parent_search, multikeys_search)
			return int(value)

		except:
			# pas de configuration trouvé ou convertion impossible ?
			return default

	# ---------------------------------------------------------
	def getFloat(self, name, default=0.0, parent_search=False, multikeys_search=False):
		""" récupération d'un élément float """
		try:
			value = self.get(name, default, parent_search, multikeys_search)
			return float(value)

		except:
			# pas de configuration trouvé ou convertion impossible ?
			return default

	# ---------------------------------------------------------
	def getEnable(self, name, default=False, parent_search=False, multikeys_search=False):
		""" récupération d'un élément vrai ou faux (transformation en bool) """
		# valeur
		value = self.get(name, default, parent_search, multikeys_search)
		if type(value) != str:
			return (value == 1 or value)

		# test de retour
		return value.lower() in ["true", "t", "1", "oui", "vrai", "v", "on", "o", "yes", "y", "si", "s", "da", "d", "ja", "j"]

	# ---------------------------------------------------------
	def getWithDateFormat(self, name, default="", parent_search=False, multikeys_search=False):
		""" 
			récupération d'un élément de configuration et interprétation des valeurs de dates
			variables acceptés : {dd}, {mm}, {yyyy}, {H}, {M} et {S}
			{mm_human} donne le nom du mois
		"""
		# récupération de la valeur
		value = self.get(name, default, parent_search, multikeys_search)

		# récupération d'un delta dans le nom
		#  {dd-10} donne 10 jours avant le jour d'aujourd'hui
		#  {H+12} donne 12 heures après l'heure courante
		# delta_d = int(re.findall(r"[+|-]\d+", value)[0]) if value.startswith("{dd") else 0

		# objet de date interne
		d = FastDate()

		# récupation des dates
		now = d.convert()

		tomorrow = d.tomorrow()
		yesterday = d.yesterday()

		weekday_tomorrow = d.weekday_tomorrow()
		weekday_yesterday = d.weekday_yesterday()

		weekend_tomorrow = d.weekend_tomorrow()
		weekend_yesterday = d.weekend_yesterday()

		working_tomorrow = d.working_tomorrow()
		working_yesterday = d.working_yesterday()

		# formatage de la valeur
		return value.format(
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

			weekday_yesterday_yyyy=weekday_yesterday.year,
			weekday_yesterday_mm=weekday_yesterday.strftime("%m"),
			weekday_yesterday_dd=weekday_yesterday.strftime("%d"),
			weekday_yesterday_H=weekday_yesterday.strftime("%H"),
			weekday_yesterday_M=weekday_yesterday.strftime("%M"),
			weekday_yesterday_S=weekday_yesterday.strftime("%S"),
			weekday_yesterday_mm_human=weekday_yesterday.strftime("%B"),

			weekday_tomorrow_yyyy=weekday_tomorrow.year,
			weekday_tomorrow_mm=weekday_tomorrow.strftime("%m"),
			weekday_tomorrow_dd=weekday_tomorrow.strftime("%d"),
			weekday_tomorrow_H=weekday_tomorrow.strftime("%H"),
			weekday_tomorrow_M=weekday_tomorrow.strftime("%M"),
			weekday_tomorrow_S=weekday_tomorrow.strftime("%S"),
			weekday_tomorrow_mm_human=weekday_tomorrow.strftime("%B"),

			weekend_yesterday_yyyy=weekend_yesterday.year,
			weekend_yesterday_mm=weekend_yesterday.strftime("%m"),
			weekend_yesterday_dd=weekend_yesterday.strftime("%d"),
			weekend_yesterday_H=weekend_yesterday.strftime("%H"),
			weekend_yesterday_M=weekend_yesterday.strftime("%M"),
			weekend_yesterday_S=weekend_yesterday.strftime("%S"),
			weekend_yesterday_mm_human=weekend_yesterday.strftime("%B"),

			weekend_tomorrow_yyyy=weekend_tomorrow.year,
			weekend_tomorrow_mm=weekend_tomorrow.strftime("%m"),
			weekend_tomorrow_dd=weekend_tomorrow.strftime("%d"),
			weekend_tomorrow_H=weekend_tomorrow.strftime("%H"),
			weekend_tomorrow_M=weekend_tomorrow.strftime("%M"),
			weekend_tomorrow_S=weekend_tomorrow.strftime("%S"),
			weekend_tomorrow_mm_human=weekend_tomorrow.strftime("%B"),

			working_tomorrow_yyyy=working_tomorrow.year,
			working_tomorrow_mm=working_tomorrow.strftime("%m"),
			working_tomorrow_dd=working_tomorrow.strftime("%d"),
			working_tomorrow_H=working_tomorrow.strftime("%H"),
			working_tomorrow_M=working_tomorrow.strftime("%M"),
			working_tomorrow_S=working_tomorrow.strftime("%S"),
			working_tomorrow_mm_human=working_tomorrow.strftime("%B"),

			working_yesterday_yyyy=working_yesterday.year,
			working_yesterday_mm=working_yesterday.strftime("%m"),
			working_yesterday_dd=working_yesterday.strftime("%d"),
			working_yesterday_H=working_yesterday.strftime("%H"),
			working_yesterday_M=working_yesterday.strftime("%M"),
			working_yesterday_S=working_yesterday.strftime("%S"),
			working_yesterday_mm_human=working_yesterday.strftime("%B"),
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
			handler = RotatingFileHandler(
				self.filename, maxBytes=rotate_log_mode, backupCount=5)

		elif not rotate_log_mode is None and rotate_log_mode.lower() == "stdout":
			handler = logging.StreamHandler()

		else:
			handler = logging.FileHandler(self.filename)

		# format du log
		formatter = logging.Formatter(
			"%(asctime)s - %(name)s - %(levelname)s - %(message)s")
		handler.setFormatter(formatter)
		self.logger.addHandler(handler)

	# ----------------------------------------------------------------------
	def setPrefix(self, text=""):
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
			self.logger.setLevel(logging.DEBUG)

		elif level == "info":
			self.logger.setLevel(logging.INFO)

		elif level == "warning" or level == "warning":
			self.logger.setLevel(logging.WARN)

		elif level == "error":
			self.logger.setLevel(logging.ERROR)

		else:
			# par défaut
			self.logger.setLevel(logging.INFO)

	# ----------------------------------------------------------------------
	def info(self, text):
		""" Ajout d'un message de log de type INFO """
		self.logger.info("{}{}".format(self.message_prefix, text))

	# ----------------------------------------------------------------------
	def debug(self, text):
		""" Ajout d'un message de log de type DEBUG """
		self.logger.debug("{}{}".format(self.message_prefix, text))

	# ----------------------------------------------------------------------
	def warn(self, text):
		""" Ajout d'un message de log de type WARN """
		self.logger.warn("{}{}".format(self.message_prefix, text))

	# ----------------------------------------------------------------------
	def warning(self, text):
		""" Ajout d'un message de log de type WARN """
		self.logger.warning("{}{}".format(self.message_prefix, text))

	# ----------------------------------------------------------------------
	def error(self, text):
		""" Ajout d'un message de log de type ERROR """
		self.logger.error("{}{}".format(self.message_prefix, text))


# ----------------------------------------------------------------------
# Outils emailing
# ----------------------------------------------------------------------

# Import smtplib for the actual sending function
import smtplib

# Import the email modules we'll need
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.utils import formatdate

# ----------------------------------------------------------------------
class FastEmail(object):
	""" Gestionnaire d'envoi de mail vers un destinataire avec un texte préformatée """
	# ----------------------------------------------------------------------
	def __init__(self):
		super(FastEmail, self).__init__()

		# initialisation
		self.mail_from = "contact@fs-dev.com"
		self.mail_subject = "Message inconnu"
		self.mail_text = 'Merci de lire le message depuis un lecteur acceptant le HTML.'
		self.mail_html = "<h2>Message inconnu</h2>"

		# informations sur le smtp à utiliser
		self.smtp_host = "localhost"
		self.smtp_port = 25
		self.smtp_tls = False
		self.smtp_login = ""
		self.smtp_password = ""

	# ----------------------------------------------------------------------
	# Définition d'un texte pour le cord du message
	def setHTML_from_file(self, filename, args):
		""" Définition d'un texte pour le cord du message """
		#  vérification d'usage
		if not os.path.isfile(filename):
			return False

		with open(filename) as fp:
			# Create a text/plain message
			self.mail_html = fp.read().format(**args)

		# retour ok
		return True

	# ----------------------------------------------------------------------
	def send_mail(self, to, cc=[], bcc=[], attachfiles=[], embeddedimages_tag="graphic_embedded", embeddedimages=[]):
		"""
		Envoi d'un email à un ou plusieurs correspondants

		:param to: liste des correspondants en adresse directe
		:param cc: liste des correspondants en copie du mail
		:param bcc: liste des correspondants en copie caché du mail
		:param attachfiles: liste des fichiers à mettre en pièce jointe (chemin exacte)
		:param embeddedimages_tag: tag type <xxx> à prendre en compte dans le body HTML du mail pour intégrer des images
		:param embeddedimages: liste des images à intégrer dans le body HTML
		:return: boolean
		"""
		# vérifications d'usage
		if type(to) != list:
			raise Exception("Sendmail: error formatting adresses To (list)")

		if type(cc) != list:
			raise Exception("Sendmail: error formatting adresses Cc (list)")

		if type(bcc) != list:
			raise Exception("Sendmail: error formatting adresses Bcc (list)")

		if type(attachfiles) != list:
			raise Exception("Sendmail: error formatting attached files (list)")

		# or embeddedimages_tag.find("<") < 0 or embeddedimages_tag.find(">") < 0:
		if type(embeddedimages_tag) != str:
			raise Exception("Sendmail: error formatting tag embedded images")

		if type(embeddedimages) != list:
			raise Exception(
				"Sendmail: error formatting embedded images (list)")

		if len(to) == len(cc) == len(bcc) == 0:
			raise Exception(
				"Sendmail: error, no destinations found (to, cc, bcc)")

		# Create the root message and fill in the from, to, and subject headers
		msgRoot = MIMEMultipart('related')
		msgRoot['Subject'] = self.mail_subject
		msgRoot['From'] = "<{}>".format(
			self.mail_from) if not "<" in self.mail_from else self.mail_from
		if len(to) > 0:
			msgRoot['To'] = ", ".join(to)
		if len(cc) > 0:
			msgRoot['Cc'] = ", ".join(cc)
		if len(bcc) > 0:
			msgRoot['Bcc'] = ", ".join(bcc)
		msgRoot["Date"] = formatdate(localtime=True)
		msgRoot.preamble = 'This is a multi-part message in MIME format.'

		# Encapsulate the plain and HTML versions of the message body in an
		# 'alternative' part, so message agents can decide which they want to display.
		msgAlternative = MIMEMultipart('alternative')
		msgRoot.attach(msgAlternative)

		msgText = MIMEText(self.mail_text)
		msgAlternative.attach(msgText)

		# We reference the image in the IMG SRC attribute by the ID we give it below
		msgText = MIMEText(self.mail_html, "html", "utf-8")
		msgAlternative.attach(msgText)

		# Insertion des fichiers attachés dans le mail
		for file_pathname in attachfiles:
			try:
				# ouverture du fichier
				with open(file_pathname, 'rb') as fp:
					msgAttachment = MIMEApplication(
						fp.read(), Name=os.path.basename(file_pathname))

				msgAttachment.add_header("Content-Disposition",
										"attachment; filename=\"{}\"".format(os.path.basename(file_pathname)))
				# msgAttachment.add_header("Content-Length", os.path.getsize(file_pathname))
				msgRoot.attach(msgAttachment)

			except Exception:
				# pas de fichier valide
				pass

		# - Insertion des images dans l'email
		indice = 1
		for file_pathname in embeddedimages:
			try:
				# construction des variables
				name_embedded = "<{}{}>".format(embeddedimages_tag, indice)

				# Ouverture du fichier
				with open(file_pathname, 'rb') as fp:
					msgImage = MIMEImage(fp.read())

				# Define the image's ID as referenced above
				msgImage.add_header('Content-ID', name_embedded)
				msgRoot.attach(msgImage)

				# incrémentation
				indice += 1

			except Exception:
				# pas de fichier valide
				pass

		# Send the email (this example assumes SMTP authentication is required)
		smtp = smtplib.SMTP(
			self.smtp_host,
			self.smtp_port,
		)
		smtp.ehlo()
		# smtp.connect(smtp_host)

		# gestion du TLS
		if self.smtp_tls:
			smtp.starttls()

		# authentification
		if self.smtp_login != "":
			smtp.login(self.smtp_login, self.smtp_password)

		# Envoi du mail
		smtp.sendmail(msgRoot['From'], to + cc + bcc, msgRoot.as_string())
		smtp.quit()

		# return OK
		return True


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
		self.args = args
		self.kwargs = kwargs

		# debug mode
		self.debug = False

	# ----------------------------------------------------------------------
	# Surcharge du fonctionnement du thread
	def run(self):
		""" Fonctionnement du thread """
		if self.debug:
			print("Starting " + self.name)

		# Lancement du programme du thread
		if isinstance(self.function, str):
			globals()[self.function](*self.args, **self.kwargs)
		else:
			self.function(*self.args, **self.kwargs)

		if self.debug:
			print("Exiting " + self.name)


# ----------------------------------------------------------------------
# Outils de date
# ----------------------------------------------------------------------

# libs
import dateutil.parser

# ----------------------------------------------------------------------
class FastDate(object):
	# ----------------------------------------------------------------------
	def __init__(self):
		super(FastDate, self).__init__()

	# ----------------------------------------------------------------------
	def convert(self, date_from=None, date_format=None):
		"""
		Retourne la date courante ou depuis l'argument au format datetime

		:param: :date_from date de référence
		:return datetime
		"""
		try:
			if date_format is None:
				# on détermine la date avec dateutil
				return dateutil.parser.parse(date_from)

			# il y a un format de date prédéfini
			return datetime.strptime(date_from, date_format)

		except:
			# échec, on prend la date courante
			return datetime.now()

	# ----------------------------------------------------------------------
	def delta(self, date_from=None, date_format=None, days=0, hours=0, minutes=0, seconds=0, days_range=[1, 2, 3, 4, 5, 6, 7]):
		"""
		Retourne la date courante ou depuis une date fournie moins un delta
		et étant autorisé dans une plage de jour (lundi=1 ... dimanche=7)

		:param: :date_from date de référence
		:param: :days nombre de jours à changer
		:param: :hours nombre d'heures à changer
		:param: :minutes nombre de minutes à changer
		:param: :seconds nombre de secondes à changer
		:param: :days_range numéro des jours (iso) autorisé pour le changement
		:return datetime
		"""
		# check des jours autorisés
		range_correct = False
		for i in range(1, 8):
			if i in days_range:
				# au moins un jour autorisé est correcte (de 1 à 7)
				range_correct = True

		# si aucun jour dans days_range ne correspond à jour réel,
		# on affecte un défaut
		if not range_correct:
			days_range = [i for i in range(1, 8)]

		# détermination du sens de déplacement du jour pour le days_range
		day_sens = 1  # en avant
		delta_absolute = days * 24 * 3600 + hours * 3600 + minutes * 60 + seconds
		if delta_absolute < 0:
			day_sens = -1

		# recherche de la date de départ
		now = self.convert(date_from=date_from, date_format=date_format)

		# calcul de la nouvelle date
		current_date = now + timedelta(
			days=days,
			hours=hours,
			minutes=minutes,
			seconds=seconds
		)

		# recherche d'un jour autorisé
		while current_date.isoweekday() not in days_range:
			current_date = current_date + timedelta(days=day_sens)

		# retour
		return current_date

	# ----------------------------------------------------------------------
	# - Jour en moins dans la date
	# ----------------------------------------------------------------------

	# ----------------------------------------------------------------------
	def yesterday(self, date_from=None, date_format=None):
		"""
		Retourne la date d'hier depuis maintenant ou depuis une date fournie

		:param: :date_from date de référence
		:return datetime
		"""
		# date d'hier
		return self.delta(date_from=date_from, date_format=date_format, days=-1)

	# ----------------------------------------------------------------------
	def weekday_yesterday(self, date_from=None, date_format=None):
		"""
		Retourne la date d'hier depuis maintenant ou depuis une date fournie
		seulement sur les jours de semaine.
		Ainsi vendredi devient jeudi et lundi devient vendredi

		:param: :date_from date de référence
		:return datetime
		"""
		# date d'hier que sur les jours de semaine
		return self.delta(days=-1, date_from=date_from, date_format=date_format, days_range=[1, 2, 3, 4, 5])

	# ----------------------------------------------------------------------
	def weekend_yesterday(self, date_from=None, date_format=None):
		"""
		Retourne la date d'hier depuis maintenant ou depuis une date fournie
		seulement sur les jours de weekend.
		Ainsi dimanche devient samedi et samedi devient dimanche

		:param: :date_from date de référence
		:return datetime
		"""
		# date d'hier que sur les jours de week-end
		return self.delta(days=-1, date_from=date_from, date_format=date_format, days_range=[6, 7])

	# ----------------------------------------------------------------------
	def working_yesterday(self, date_from=None, date_format=None):
		"""
		Retourne la date d'hier depuis maintenant ou depuis une date fournie
		seulement sur les jours ouvrableq.
		Ainsi lundi devient samedi et samedi devient vendredi

		:param: :date_from date de référence
		:return datetime
		"""
		# date d'hier que sur les jours de week-end
		return self.delta(days=-1, date_from=date_from, date_format=date_format, days_range=[1, 2, 3, 4, 5, 6])

	# ----------------------------------------------------------------------
	# - Jour en plus dans la date
	# ----------------------------------------------------------------------

	# ----------------------------------------------------------------------
	def tomorrow(self, date_from=None, date_format=None):
		"""
		Retourne la date de demain depuis maintenant ou depuis une date fournie

		:param: :date_from date de référence
		:return datetime
		"""
		# date de demain
		return self.delta(date_from=date_from, date_format=date_format, days=1)

	# ----------------------------------------------------------------------
	def weekday_tomorrow(self, date_from=None, date_format=None):
		"""
		Retourne la date de demain depuis maintenant ou depuis une date fournie
		seulement sur les jours de semaine.
		Ainsi vendredi devient jeudi et lundi devient vendredi

		:param: :date_from date de référence
		:return datetime
		"""
		# date de demain que sur les jours de semaine
		return self.delta(days=1, date_from=date_from, date_format=date_format, days_range=[1, 2, 3, 4, 5])

	# ----------------------------------------------------------------------
	def weekend_tomorrow(self, date_from=None, date_format=None):
		"""
		Retourne la date de demain depuis maintenant ou depuis une date fournie
		seulement sur les jours de weekend.
		Ainsi dimanche devient samedi et samedi devient dimanche

		:param: :date_from date de référence
		:return datetime
		"""
		# date de demain que sur les jours de week-end
		return self.delta(days=1, date_from=date_from, date_format=date_format, days_range=[6, 7])

	# ----------------------------------------------------------------------
	def working_tomorrow(self, date_from=None, date_format=None):
		"""
		Retourne la date de demain depuis maintenant ou depuis une date fournie
		seulement sur les jours ouvrableq.
		Ainsi lundi devient samedi et samedi devient vendredi

		:param: :date_from date de référence
		:return datetime
		"""
		# date de demain que sur les jours de week-end
		return self.delta(days=1, date_from=date_from, date_format=date_format, days_range=[1, 2, 3, 4, 5, 6])
