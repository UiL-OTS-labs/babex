# Adult participant administration system BACKEND

Adult participant administration system, written in Django.

## Introduction

This Django project is part of a two-application system used to keep track of 
adult participants, experiments and appointments for the UiL OTS Labs.

This project represents the backend application, which is for system 
administrators only.

## Requirements

* Python 3.9+ (3.8 might work, untested)
* Pip (for installing dependencies, see requirements.txt for details)
* A WSGI capable web server (not needed for development)
* A SQL database (tested with SQLite and MySQL)

## Installation

For production/acceptation deployment, please see our Puppet script. (Hosted on 
our private GitLab server).

Development instructions:
* Clone this repository
* Install the dependencies using pip (it is recommended to use a virtual 
  environment!). ``pip install -r requirements.txt``
* Run all DB migrations ``python manage.py migrate`` and ``python manage.py migrate --database auditlog``
* Edit ``ppn_backend/settings.py`` to suit your needs.
* Create a super user using ``python manage.py createsuperuser``
* Compile the translation files using ``python manage.py compilemessages``
* You can now run a development server with ``python manage.py runserver``

Note: you probably also want to set your new super user as the main admin, 
otherwise the frontend probably won't like you. (Read: it will error without a 
Main Admin)
(You can change this in the 'Admin' section in the menu).

Note 2:
As the ``runserver`` command defaults to using ``localhost:8000`` you will need 
to specify a different port for either the frontend or backend. If you're using
the default settings, the backend should run at port 9000. You can change 
the port the application will listen on by specifying it as an argument.

For example: ``python manage.py runserver 9000`` will set the port used to 9000

## A note on dependencies
We use pip-tools to manage our dependencies (mostly to freeze the versions 
used). It's listed as a dependency, so it will be installed automatically.

``requirements.in`` lists the actual dependency and their version constraints. 
To update ``requirements.txt`` just run ``pip-compile -U``. Don't forget to test 
with the new versions!