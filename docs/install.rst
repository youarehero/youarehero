==================
Installation Guide
==================

This section describes how to set up a local development environment for the **You are HERO** project.
Since ``python`` is a platform independent language, it should be possible on most operating systems.
However, the focus of this document is on Unix based systems like MacOS or Ubuntu/linux.

Preparation and Dependencies
============================

First of all you need `python 2.7 <http://www.python.org/download/>`_ and
the version control system `git <http://git-scm.com/book/en/Getting-Started-Installing-Git>`_.
On most Unix based systems ``python`` is already installed, but you'll need the
``python-dev`` package to compile ``pillow`` later. For the same reason you will need ``libjpeg-dev``.

Further you need `virtualenv`_ to create a isolated python environment,
which we use for handling all other requirements.

You may use your operating system's package manager::

   $ sudo apt-get install git python-dev python-virtualenv libjpeg-dev

or use ``easy_install``::

   $ easy_install virtualenv

or on MacOS::

   coming soon...

Cloning the git repository
==========================

    $ git clone https://github.com/youarehero/youarehero.git

.. _bootstrap_dev:

The bootstrap script
====================

After cloning the git repository, browse to your project dir and run::

    $ make bootstrap-dev

The script creates a virtual environment (in ``env/``)
and creates the ``static/``, ``media/`` and ``coverage/`` folders, which are
not in the git repo, as they contain generated data.
It also creates a local settings file (``src/youarehero/settings/local.py``) which contains the development settings.
At last it installs all required
*django apps* and *python packages* inside the *virtual env*.

.. ATTENTION::
   if the script breaks with an error while installing the requirements,
   follow the instructions for :ref:`installing requirements manually <install-requirements>`
   in the next section.


The Virtual Environment
=======================

The most requirements are installed in a isolated python environment, called `virtualenv`_.
This happened in the last paragraph.

From now on you need to ``activate`` your *virtual environment*::

    $ source env/bin/activate
    (env)$

.. NOTE::
   All commands starting with ``(env)$`` are assumed to run within your *virtual env*.

.. _install-requirements:

Install requirements manually
-----------------------------

If the script breaks or you pull the git repo later with modified requirements,
you may want to install them manually.

Make sure the above dependencies (especially ``python-dev`` and ``libjpeg-dev``)
are installed on your system. To install the requirements type::

  (env)$ pip install -r deploy/requirements.txt

.. _virtualenv: <http://www.virtualenv.org>


Creating a local config file
============================
Create a file named local.py in ``src/youarehero/settings/local.py`` containing the line::

   from devel import *

On linux/mac you can do that by running::
    
   echo "from devel import *" >> src/youarehero/settings/local.py

Initialize Database
===================

For developing purposes the default Database engine is `sqlite <http://www.sqlite.org/docs.html>`_,
so you don't have to set up a custom database. Run::

    (env)$ src/manage.py syncdb
    (env)$ src/manage.py migrate

for initializing the local database. If you were asked to create a superuser, do so and continue.
You will need this user to log into the ``django-admin`` and it is also your first hero.

Start Development Server
========================

Now you are ready to test your installation::

    (env)$ src/manage.py runserver

Try to visit `localhost on port 8000 <http://localhost:8000>`_. If everything is
working correctly you should see your local **You are HERO** instance.

Local Email Setup
=================

If you want to send emails from your local machine, edit ``youarehero/settings/local.py``::

   EMAIL_HOST =
   EMAIL_HOST_USER =
   EMAIL_USE_TLS = True
   EMAIL_PORT = 25
   EMAIL_HOST_PASSWORD =
   DEFAULT_FROM_EMAIL =
   EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

and insert an smtp-server, user and password, such as for an email-client.

