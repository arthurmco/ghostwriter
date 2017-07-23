#
#   Manages and creates the data models
#
#   Copyright (C) 2017 Arthur M

from flask_sqlalchemy import SQLAlchemy

class ModelManager(object):
    def __init__(self, app):
        self.app = app

    def setDatabaseURI(self, path):
        self.app.config['SQLALCHEMY_DATABASE_URI'] = path
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        self.app.config['GHOSTWRITER_DATABASE'] = self

    def init(self):
        self._database = SQLAlchemy(self.app)

    def create(self):
        from ghostwriter.models.models import db_create_all
        """ Create the database. Only do this ONLY ONE F****ING TIME """
        db_create_all()
        from ghostwriter.models.models import MPost
        from datetime import datetime
        self._database.session.add(
                MPost('Test TItle', datetime.utcnow(), "Test content"))
        self._database.session.add(
                MPost('No content title', datetime.utcnow()))
        self._database.session.commit()

    @property
    def database(self):
        return self._database

    
