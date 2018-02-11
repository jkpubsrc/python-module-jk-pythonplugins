#!/usr/bin/python3
# -*- coding: utf-8 -*-


import os
import sys
import importlib
import inspect
import time
import types


import jk_logging





#
# This is a wrapper around a python source code file that should be available to the rest of the python program as a plugin.
#
# The python source code wrapped must contain a single class. An initialization method may be available but it must expect no arguments.
#
class PluginWrapper(object):

	# ================================================================
	# == Constructors/Destructors
	# ================================================================

	#
	# Initialization method
	#
	# @param	str moduleFilePath			The absolute path to the (existing) python file
	#
	def __init__(self, moduleFilePath, initCallback):
		if not moduleFilePath.endswith(".py"):
			raise Exception("Not a python source code file: " + moduleFilePath)
		if not os.path.isabs(moduleFilePath):
			raise Exception("Not an absolute path: " + moduleFilePath)

		self.__initCallback = initCallback
		self.__moduleName = os.path.basename(moduleFilePath)
		self.__moduleName = self.__moduleName[:-3]
		self.__moduleDirPath = os.path.dirname(moduleFilePath)

		self.__moduleFilePath = moduleFilePath
		self.__modificationTimeStamp = -1
		self.__bIsLoaded = False

		self.__moduleInstance = None
		self.__class = None
		self.__classInstance = None
		self.__classMethodNames = None
		self.__extraData = None
	#

	# ================================================================
	# == Properties
	# ================================================================

	#
	# The absolute path file of the python source code file this object should wrap around
	#
	@property
	def filePath(self):
		return self.__moduleFilePath
	#

	#
	# The name of this plugin. This name is derived from the file name, not the class implementing this plugin.
	#
	@property
	def name(self):
		return self.__moduleName
	#

	#
	# Has the underlying source code file been changed?
	#
	@property
	def isChanged(self):
		mt = self.__getModificationTimeStamp(self.__moduleFilePath)
		return mt != self.__modificationTimeStamp
	#

	#
	# Is this plugin still in use?
	#
	@property
	def isInUse(self):
		if self.__moduleInstance is None:
			return False
		return sys.getrefcount(self.__moduleInstance) > 3
	#

	#
	# Is the underlying plugin class loaded?
	#
	def isLoaded(self):
		return self.__bIsLoaded
	#

	#
	# Provides extra data about the plugin. This data is provided by the initialization callback.
	#
	@property
	def extraData(self):
		return self.__extraData
	#

	# ================================================================
	# == Helper Methods
	# ================================================================

	def __getModificationTimeStamp(self, filePath):
		if os.path.isfile(filePath):
			try:
				return os.path.getmtime(filePath)
			except:
				return -1
		else:
			return -1
	#

	# ================================================================
	# == Public Methods
	# ================================================================

	#
	# Load the source code file. For this to succeed the current state must be "UNLOADED".
	# An exception is thrown on error.
	#
	# @param	AbstractLogger log					A logger to receive debug output (or <c>None</c> if not needed)
	# @param	bool bAcceptIsChangedAlsoOnError	If <c>True</c> even a failed loading attempt will make the wrapper remember the file.
	#												Successive calls to <c>isChanged</c> will then return <c>False</c>. But if <c>False</c>
	#												is specified here <c>load()</c> will not remember the file if loading fails.
	#												I that case successive calls to <c>isChanged</c> will then return <c>True</c>.
	#
	def load(self, log, bAcceptIsChangedAlsoOnError = False):
		if self.__bIsLoaded:
			log.debug("Module already loaded, nothing to do.")
			return

		mt = self.__getModificationTimeStamp(self.__moduleFilePath)
		if mt < 0:
			raise Exception("No such file: " + self.__moduleFilePath)
		if bAcceptIsChangedAlsoOnError:
			self.__modificationTimeStamp = mt

		if not self.__moduleDirPath in sys.path:
			log.debug("Adding module directory to sys.path ...")
			sys.path.append(self.__moduleDirPath)

		log.debug("Loading and parsing module ...")
		self.__moduleInstance = importlib.import_module(self.__moduleName)
		#print(sys.getrefcount(self.__moduleInstance))

		log.debug("Scanning module for classes ...")
		countClassesFound = 0
		for name, element in inspect.getmembers(self.__moduleInstance):
			if inspect.isclass(element) and (element.__module__ == self.__moduleInstance.__name__):
				log.debug("Found: " + element.__name__)
				self.__class = element
				countClassesFound += 1
		if countClassesFound == 0:
			log.debug("No classes found in module: " + self.__moduleFilePath)
			self.unload(log)
			raise Exception("No classes found in module: " + self.__moduleFilePath)
		if countClassesFound > 1:
			log.debug("Multiple classes found in module: " + self.__moduleFilePath)
			self.unload(log)
			raise Exception("Multiple classes found in module: " + self.__moduleFilePath)

		self.__classInstance = self.__class()
		
		if self.__initCallback:
			try:
				self.__extraData = self.__initCallback(self.__classInstance)
			except Exception as e:
				log.error("Initialization callback failed:")
				log.error(e)
				self.unload(log)
				raise Exception("Initialization callback failed for class in module: " + self.__moduleFilePath)

		log.debug("Module loaded.")
		self.__bIsLoaded = True
		self.__modificationTimeStamp = mt

		#for key in sys.modules:
		#	print(key + " -- " + str(sys.modules[key]))
	#

	#
	# Removes all traces of the loaded python class.
	#
	# This method is indempotent. You may invoke it even if the underlying python source code is not yet loaded.
	#
	# @param	AbstractLogger log					A logger to receive debug output (or <c>None</c> if not needed)
	#
	def unload(self, log):
		log.debug("Unloading module ...")

		self.__classMethodNames = None
		self.__classInstance = None
		self.__class = None
		self.__extraData = None

		if self.__moduleInstance:
			del sys.modules[self.__moduleName]
			self.__moduleInstance = None
			#self.__moduleInstance = importlib.reload(self.__moduleInstance)

		self.__bIsLoaded = False
	#

	#
	# Invoke a method.
	# The underlying plugin class must be loaded for this to work.
	#
	# @param	str methodName			The name of the method to invoke
	# @param	list args				Arguments
	# @param	dict kwargs				Arguments
	# @return	mixed					Returns the data the invoked method provides
	#
	def invoke(self, methodName, *args, **kwargs):
		if not self.__bIsLoaded:
			raise Exception("Plugin not loaded!")

		m = getattr(self.__classInstance, methodName, None)
		if m:
			return m(*args, **kwargs)
		else:
			raise Exception("No such plugin method: " + methodName)
	#

	#
	# Get a list of all methods available in the (loaded) plugin class.
	# The underlying plugin class must be loaded for this to work.
	#
	# @return		str[]		Returns a tuple of strings.
	#
	def getMethodNames(self):
		if not self.__bIsLoaded:
			raise Exception("Plugin not loaded!")

		if not self.__classMethodNames:
			self.__classMethodNames = [x for x, y in self.__class.__dict__.items() if not x.startswith("_") and (type(y) == types.FunctionType)]

		return tuple(self.__classMethodNames)
	#

#




