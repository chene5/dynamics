# -*- coding: utf-8 -*-
"""config.py
Configurations for Flask.

TODO

Created on Mon Oct 19 11:38:23 2015

@author: Eric
"""
import os.path


basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + \
    os.path.join(basedir, 'local.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'local_db_repository')

SQLALCHEMY_TRACK_MODIFICATIONS = False

WTF_CSRF_ENABLED = True
SECRET_KEY = \
	"!p/\x99\xe4\xfd.'\x0e\xc0\x18\xd1T@\x1c\xd7\x00\x15\x00\xd8\xeaRD\xce"
DEBUG = True
CREATIVE_ADMIN = 'admin'
