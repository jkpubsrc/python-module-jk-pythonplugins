from setuptools import setup


def readme():
	with open('README.rst') as f:
		return f.read()


setup(name='jk_pythonplugins',
	version='0.2018.2.11',
	description='This python module provides classes to implement a simple plugin infrastructure in python.',
	author='Jürgen Knauth',
	author_email='pubsrc@binary-overflow.de',
	license='Apache 2.0',
	url='https://github.com/jkpubsrc/python-module-jk-pythonplugins',
	download_url='https://github.com/jkpubsrc/python-module-jk-pythonplugins/tarball/0.2018.2.9',
	keywords=['plugins'],
	packages=['jk_pythonplugins'],
	install_requires=[
		"jk_logging",
	],
	include_package_data=True,
	classifiers=[
		'Development Status :: 5 - Production/Stable',
		'Programming Language :: Python :: 3.5',
		'License :: OSI Approved :: Apache Software License'
	],
	long_description=readme(),
	zip_safe=False)

