#!/usr/bin/python3
# -*- coding: utf-8 -*-


import os
import time


import jk_logging
import jk_pythonplugins












log = jk_logging.ConsoleLogger(logMsgFormatter = jk_logging.COLOR_LOG_MESSAGE_FORMATTER)



pw = jk_pythonplugins.PluginWrapper(os.path.abspath("plugins/myplugin.py"), None)

while True:
	if pw.isChanged:
		pw.unload(log)
		try:
			pw.load(log, bAcceptIsChangedAlsoOnError = True)
		except Exception as e:
			#log.error(e)
			log.error("ERROR")

	pw.invoke("doSomething", log)

	time.sleep(2)

