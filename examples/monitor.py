#!/usr/bin/python3
# -*- coding: utf-8 -*-


import os
import time


import jk_logging
import jk_pythonplugins












log = jk_logging.ConsoleLogger(logMsgFormatter = jk_logging.COLOR_LOG_MESSAGE_FORMATTER)



dpm = jk_pythonplugins.DirectoryPluginManager(os.path.abspath("plugins"))

while True:
	results = dpm.update()
	for item in results:
		print(item)

	print("Sleeping ...")
	time.sleep(2)

