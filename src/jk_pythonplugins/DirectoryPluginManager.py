#!/usr/bin/python3
# -*- coding: utf-8 -*-


import os
import sys
import importlib
import inspect
import time
import types
import collections


import jk_logging

from .PluginWrapper import PluginWrapper






PluginResult = collections.namedtuple("PluginResult", [ "status", "filePath", "pluginWrapper", "logBuffer" ])





#
#
class DirectoryPluginManager(object):

	# ================================================================
	# == Constructors/Destructors
	# ================================================================

	#
	# Initialization method
	#
	# @param	str dirPath					The absolute path to the (existing) python file
	# @param	callable initCallback		A method to invoke after a plugin has been loaded.
	#
	def __init__(self, dirPath, initCallback = None):
		if not os.path.isabs(dirPath):
			raise Exception("Not an absolute path: " + dirPath)
		if not os.path.isdir(dirPath):
			raise Exception("Not an directory: " + dirPath)

		self.__dirPath = dirPath
		self.__wrappers = {}
		self.__wrappersCachedList = None
		self.__wrappersCachedMap = None
		self.__initCallback = initCallback
	#

	# ================================================================
	# == Properties
	# ================================================================

	#
	# The absolute path of the directory where to look for python modules
	#
	@property
	def dirPath(self):
		return self.__dirPath
	#

	#
	# This property returns a list of all plugin objects.
	#
	# @return	list<PluginWrapper>			Returns a tuple of <c>PluginWrapper</c> objects covering all currently known plugins, loaded and unloaded ones.
	#
	@property
	def pluginList(self):
		if self.__wrappersCachedList is None:
			self.__wrappersCachedList = tuple(self.__wrappers.values())
		return self.__wrappersCachedList
	#

	#
	# This property returns a map of all plugin objects.
	#
	# @return	dict<str,PluginWrapper>			Returns a dictionary of names associated with the <c>PluginWrapper</c> objects.
	#											This covers all currently known plugins, loaded and unloaded ones.
	#
	@property
	def pluginMap(self):
		if self.__wrappersCachedMap is None:
			self.__wrappersCachedMap = collections.OrderedDict()
			for pw in self.__wrappers.values():
				self.__wrappersCachedMap[pw.name] = pw
		return self.__wrappersCachedMap
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
	# Looks for plugins that have been removed, modified or new ones that have been added.
	#
	# @param		AbstractLogger log	A log object used to receive debug output and errors. You may specify <c>None</c> here if you're not interested in this data.
	# @return		PluginResult[]		Returns a set of <c>PluginResult</c> objects to reflect changes detected.
	#									The <c>status</c> field of <c>PluginResult</c> will contain one of the following keywords:
	#									* <c>add-ok</c> - A plugin class has successfully been loaded.
	#									* <c>add-err</c> - A plugin class has been found but failed to load.
	#									* <c>del-ok</c> - A plugin class does no longer exist and has therefor been unloaded.
	#									* <c>mod-ok</c> - A plugin class has been modified and was therefor unloaded and successfully loaded again.
	#									* <c>mod-err</c> - A plugin class has been modified and was therefor unloaded but failed to load again.
	#									Each <c>PluginResult</c> object will contain the log output contained in a <c>jk_logging.BufferLogger</c> object.
	#
	def update(self, log = None):
		if log is None:
			log = jk_logging.NullLogger.create()

		newList = []
		modifiedList = []
		unchangedList = []
		removedList = [ x for x in self.__wrappers.values() ]

		for entryName in os.listdir(self.__dirPath):
			fullPath = os.path.join(self.__dirPath, entryName)
			if os.path.isfile(fullPath) and entryName.endswith(".py") and not entryName.startswith("_"):
				if fullPath in self.__wrappers:
					# existing plugin
					pw = self.__wrappers[fullPath]
					if pw.isChanged:
						log.debug("Found modified: " + entryName)
						modifiedList.append(pw)
					else:
						log.debug("Found unchanged: " + entryName)
						unchangedList.append(pw)
					removedList.remove(pw)
				else:
					# new plugin
					log.debug("Found new: " + entryName)
					pw = PluginWrapper(fullPath, self.__initCallback)
					self.__wrappers[fullPath] = pw
					newList.append(pw)

		for pw in removedList:
			log.debug("Found no longer existing: " + os.path.basename(pw.filePath))

		results = []
		mlog = jk_logging.MulticastLogger.create(log)

		for pw in removedList:
			blog = jk_logging.BufferLogger.create()
			mlog.addLogger(blog)
			mlog.info("Unloading: " + os.path.basename(pw.filePath))
			pw.unload(mlog)
			del self.__wrappers[pw.filePath]
			results.append(PluginResult("del-ok", pw.filePath, pw, blog))
			mlog.removeLogger(blog)

		for pw in newList:
			blog = jk_logging.BufferLogger.create()
			mlog.addLogger(blog)
			mlog.info("Loading: " + os.path.basename(pw.filePath))
			try:
				pw.load(mlog, True)
				results.append(PluginResult("add-ok", pw.filePath, pw, blog))
			except Exception as e:
				mlog.error(e)
				results.append(PluginResult("add-err", pw.filePath, pw, blog))
			mlog.removeLogger(blog)

		for pw in modifiedList:
			blog = jk_logging.BufferLogger.create()
			mlog.addLogger(blog)
			mlog.debug("Reloading: " + os.path.basename(pw.filePath))
			pw.unload(log)
			try:
				pw.load(mlog, True)
				results.append(PluginResult("mod-ok", pw.filePath, pw, blog))
			except Exception as e:
				mlog.error(e)
				results.append(PluginResult("mod-err", pw.filePath, pw, blog))
			mlog.removeLogger(blog)

		if len(results) > 0:
			self.__wrappersCachedList = None
			self.__wrappersCachedMap = None

		return results
	#

#




