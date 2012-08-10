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

Until the project is on Github, mail us your favorite *username* and *ssh pubkey*.
You should get an answer and subsequently be able to clone the repository::

    $ git clone ssh://git@queen.daenerys.de:54884/platform youarehero

.. _bootstrap_dev:

The bootstrap script
====================

After cloning the git repository, browse to your project dir and run::

    $ deploy/bootstrap_dev

The script makes a virtual environment ready (in ``env/``)
and creates the ``static/``, ``media/`` and ``coverage/`` folders, which are
not in the git repo, as they contain generated data.
It also creates the local settings file (``src/youarehero/settings/local.py``) with no content but
including the development settings.
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

Initialize Database
===================

For developing purposes the default Database engine is `sqlite <http://www.sqlite.org/docs.html>`_,
so you don't have to set up a custom database. Run::

    (env)$ src/manage.py syncdb
    (env)$ src/managy.py migrate

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

and insert an smtp-server, user and password, such as for an email-client.

