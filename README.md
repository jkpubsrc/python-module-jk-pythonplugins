jk_sysctrlplugins
=================

Introduction
------------

This python module provides classes to implement a simple plugin infrastructure in python.

Information about this module can be found here:

* [github.org](https://github.com/jkpubsrc/python-module-jk-pythonplugins)
* [pypi.org](https://pypi.org/project/jk_pythonplugins/)

How to use this module
----------------------

### Import

To import this module use the following statement:

```python
import jk_pythonplugins
```

### How to load plugin classes

The preferred way is to use a plugin manager. Plugin managers take a directory path as input and then perform plugin management on all python code files found in that directory. Example:

```python
dpm = jk_pythonplugins.DirectoryPluginManager("/some/directory/path/for/plugins")
dpm.update()
```

Invoke `update()` in order to reevaluate the content of the diretory.

### How to invoke a plugin method

See this code example to learn how to invoke a specific method on a plugin:

```python
retValue = dpm.pluginMap["MyPlugin"].invoke("doSomething")
```

With `dpm.pluginMap["MyPlugin"]` you retrieve the desired plugin from the plugin manager. Then you can call `invoke()` in order to invoke a specific plugin method. Arguments could be passed to the plugin method if required (which is not done in this particular example).

Contact Information
-------------------

This is Open Source code. That not only gives you the possibility of freely using this code it also
allows you to contribute. Feel free to contact the author(s) of this software listed below, either
for comments, collaboration requests, suggestions for improvement or reporting bugs:

* Jürgen Knauth: jknauth@uni-goettingen.de, pubsrc@binary-overflow.de

License
-------

This software is provided under the following license:

* Apache Software License 2.0



