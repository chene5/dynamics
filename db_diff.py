# -*- coding: utf-8 -*-
"""
Created on Sun Nov 08 14:11:18 2015

@author: eec
"""
import imp
from migrate.versioning import api
from application import db
from config import SQLALCHEMY_DATABASE_URI
from config import SQLALCHEMY_MIGRATE_REPO

v = api.db_version(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)

migration = SQLALCHEMY_MIGRATE_REPO + ('/versions/%03d_migration.py' % (v+1))
tmp_module = imp.new_module('old_model')
old_model = api.create_model(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
exec(old_model, tmp_module.__dict__)

difference = api.compare_model_to_db(SQLALCHEMY_DATABASE_URI,
                                     SQLALCHEMY_MIGRATE_REPO,
                                     db.metadata)

print difference
