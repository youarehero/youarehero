========
Overview
========

Django
======

**You are HERO** is based on `Django <https://www.djangoproject.com/>`_, a python web-framework.
The `Django documentation <https://docs.djangoproject.com/>`_ is detailed
and we recommend the `Tutorial <https://docs.djangoproject.com/en/1.4/intro/tutorial01/>`_.

Assuming you know the Basics (models, views, urls) we can start with the special characteristics
of the **You are HERO** project.

The source code for this project is located in ``src/``. Note that Django 1.4 comes with a new
directory structure. The project related files are located in ``src/youarehero/``.

By now there are the following custom apps:


* :doc:`herobase` YAH basic models and behaviour
* :doc:`heromessage` internal private messages

We use `south <http://south.readthedocs.org>`_ for database migrations.

.. NOTE::
   If you get an database related error after pulling the git repo, it may be necessary to
   migrate one of the custom apps. Try::

      (env)$ src/managy.py migrate

More documentation follows...

Other Components
================

Beside *Django* and the *project related apps* there are other components used in this project:

* This documentation is build with `sphinx <http://sphinx.pocoo.org/contents.html>`_.
  The documentation source is located in ``docs/``.
* `Django-coverage <https://bitbucket.org/kmike/django-coverage/>`_ generates
  `html <https://youarehero.net/coverage/>`_ with information about the test coverage of our project.
* The most requirements are bundeled in an isolated `virtualenv <http://www.virtualenv.org>`_.