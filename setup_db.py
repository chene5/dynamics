# -*- coding: utf-8 -*-
"""setup_db.py
Setup functions for the database.

Created on Sat Nov 28 08:59:51 2015

@author: Eric
"""
from application import models, db


models.Role.insert_roles()

"""
print 'Create Admin'
user = models.User(email='admin@example.com',
                   username='admin',
                   password='aGeAVKg9')
db.session.add(user)
db.session.commit()
"""
