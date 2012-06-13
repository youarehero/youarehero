.. youarehero documentation master file, created by
   sphinx-quickstart on Mon Mar 19 11:59:21 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

========================================
Welcome to You are HERO's documentation!
========================================

**You are HERO** is based on `Django <https://www.djangoproject.com/>`_.
The `Django documentation <https://docs.djangoproject.com/>`_ is detailed
and we recommend the `Tutorial <https://docs.djangoproject.com/en/1.4/intro/tutorial01/>`_.

Assuming you know the Basics (models, views, urls) we can start with the special characteristics
of the **You are HERO** project.

Installation Guide
==================

After cloning the git repository, you need ``pip`` and ``virtualenv`` installed on your system.
You may use your operating system's package manager; E.g.::

    $ sudo apt-get install pip virtualenv

or using ``easy_install``::

    $ easy_install pip; easy_install virtualenv

Project Requirements
--------------------

Browse to the project git dir and run::

    $ deploy/bootstrap_dev

The script will make a virtual environment ready (in ``env/``) and install all required
Django apps and python packages.

Henceforth you need to ``activate`` your virtuel environment::

    $ source env/bin/activate
    (env)$

You can ``deactivate`` the environment with::

    (env)$ deactivate
    $

Initialize Database
-------------------

For developing purposes the default Database engine is ``sqlite``. Run::

    (env)$ src/manage.py syncdb
    (env)$ src/managy.py migrate

for initial database setup. If you were asked to create a superuser, do so.

Start Development Server
------------------------

Now you are ready to test your installation::

    (env)$ src/manage.py runserver

Try to visit `localhost on port 8000 <http://localhost:8000>`_.

Source Documentation
====================

Contents:

.. toctree::
   :maxdepth: 2

   herobase

   heromessage

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`