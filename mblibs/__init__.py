#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
"""
    Fast tools for programming
"""


__version__ = "1.1.0"


# libs
import os
import sys
import time
import datetime

# ----------------------------------------------------------------------
# Outils de fonction de test d'une application (mini framework)
# ----------------------------------------------------------------------

# variables utiles
__testing_count_success = 0
__testing_count_failed = 0

# ----------------------------------------------------------------------
def testing_successed():
	""" retourne le nombre de succès aux tests """
	global __testing_count_success
	return __testing_count_success

# ----------------------------------------------------------------------
def testing_failed():
	""" retourne le nombre de succès aux tests """
	global __testing_count_failed
	return __testing_count_failed

# ----------------------------------------------------------------------
def testing_function(testing_text):
	""" Décorateur pour traiter les fonctions de tests """
	def testing_decorator(func):
		def test(*args, **kwargs):
			try:
				# log
				print("{} ... ".format(testing_text), end='', flush=True)

				# tests
				chrono_start = time.time()
				return_val = func(*args, **kwargs)
				if return_val is None:
					return_val = True
				if return_val == False:
					raise Exception("check function failed and returns 'False'")

				# log
				print("OK [{:.2}s]".format(time.time() - chrono_start))
				global __testing_count_success
				__testing_count_success += 1

				# return
				return return_val

			except Exception as reason:
				print("Failed [{:.2}s]: {}".format(time.time() - chrono_start, str(reason)))
				global __testing_count_failed
				__testing_count_failed += 1

				# return
				return False

		return test
	return testing_decorator

# -- TEMPLATE POUR TESTER UNE FONCTION --
# ------------------------------------------------------------------
# Vérification de XXX
# @testing_function("Checking XXX")
# def check_XXX():
# 	pass
# check_XXX()
#
# *or if OK :* if check_XXX():



# ----------------------------------------------------------------------
# Outils divers
# ----------------------------------------------------------------------

# ----------------------------------------------------------------------

# ----------------------------------------------------------------------
def DisplayMemory():
	if is_windows():
		print( "Total computer memory used  :  % 2.2f MB" % round(GetMemory() / 1024.0/ 1024.0, 1) )

	else:
		print( "Memory usage  :  % 2.2f MB" % round(GetMemory() / 1024.0/ 1024.0, 1) )

# ----------------------------------------------------------------------
def GetMemory():
	if is_linux():
		import resource
		return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss

	if is_windows():
		import ctypes

		class MEMORYSTATUSEX(ctypes.Structure):
			_fields_ = [
			    ("dwLength", ctypes.c_ulong),
			    ("dwMemoryLoad", ctypes.c_ulong),
			    ("ullTotalPhys", ctypes.c_ulonglong),
			    ("ullAvailPhys", ctypes.c_ulonglong),
			    ("ullTotalPageFile", ctypes.c_ulonglong),
			    ("ullAvailPageFile", ctypes.c_ulonglong),
			    ("ullTotalVirtual", ctypes.c_ulonglong),
			    ("ullAvailVirtual", ctypes.c_ulonglong),
			    ("sullAvailExtendedVirtual", ctypes.c_ulonglong),
			]

			def __init__(self):
				# have to initialize this to the size of MEMORYSTATUSEX
				self.dwLength = ctypes.sizeof(self)
				super(MEMORYSTATUSEX, self).__init__()

		stat = MEMORYSTATUSEX()
		ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat))

		# print(stat.dwLength)
		# print(stat.dwMemoryLoad)
		# print(stat.ullTotalPhys)
		# print(stat.ullAvailPhys)
		# print(stat.ullTotalPageFile)
		# print(stat.ullAvailPageFile)
		# print(stat.ullTotalVirtual)
		# print(stat.ullAvailVirtual)
		# print(stat.sullAvailExtendedVirtual)

		return stat.ullTotalPhys - stat.ullAvailPhys

	return 0


# ----------------------------------------------------------------------
# détection si on est windows
import platform

# ----------------------------------------------------------------------
def is_windows():
	""" détermine si le système actuel est windows """
	return platform.system().lower() == "windows"

# ----------------------------------------------------------------------
def is_mac():
	""" détermine si le système actuel est mac """
	return platform.system().lower() == "darwin"

# ----------------------------------------------------------------------
def is_linux():
	""" détermine si le système actuel est linux """
	return platform.system().lower() == "linux"
