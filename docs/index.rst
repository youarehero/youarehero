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

Bis das Projekt auf Github liegt: Mail uns Deinen ssh-key.

Nachdem Du uns Deinen ssh-key hast zukommen lassen::

    $ git clone ssh://username@queen.daenerys.de:54884/srv/git/youarehero

After cloning the git repository, you need ``pip`` and ``virtualenv`` installed on your system.
You may use your operating system's package manager::

    $ sudo apt-get install python-pip python-virtualenv

or use ``easy_install``::

    $ easy_install pip; easy_install virtualenv

Sieht so aus als bräuchte man noch::

    libjpeg(-dev) python(-dev)

Aber das steht auch in der virtualenv anleitung ...

Project Requirements
--------------------

Browse to the project git dir and run::

    $ deploy/bootstrap_dev ##########

    # ACHTUNG: readline kaputt/ wenn ein module fehlt gibts keinen fehler
    # Falls das script nich durchläuft:
    # (env)$ pip install -r deploy/requirements.txt

The script will make a virtual environment ready (in ``env/``) and install all required
Django apps and python packages.

From now on you need to ``activate`` your virtuel environment::

    $ source env/bin/activate
    (env)$

All commands starting with ``(env)$`` are assumed to run within your virtual env.

Initialize Database
-------------------

For developing purposes the default Database engine is ``sqlite``. Run::

    (env)$ src/manage.py syncdb
    (env)$ src/managy.py migrate

for initial database setup. If you were asked to create a superuser, do so and continue.

Start Development Server
------------------------

Now you are ready to test your installation::

    (env)$ src/manage.py runserver

Try to visit `localhost on port 8000 <http://localhost:8000>`_. If everything is
working correctly you should see the **You are HERO** public home view.

Deactivate Virtual Env
======================

Later you may want to ``deactivate`` the environment::

    (env)$ deactivate
    $

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