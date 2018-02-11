#!/usr/bin/python3
# -*- coding: utf-8 -*-


import os
import sys


class MyPlugin(object):

	def __init__(self):
		print("PLUGIN init")
	#

	def doSomething(self, log):
		log.info("PLUGIN doSomething")
	#

#



