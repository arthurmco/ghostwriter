#   Database models for GhostWriter
#
#   Copyright (C) 2017 Arthur M
#

from flask_sqlalchemy import SQLAlchemy
from ghostwriter import app

models = app.config['GHOSTWRITER_DATABASE'].database

class MPost(models.Model):
    id = models.Column(models.Integer, primary_key=True)
    title = models.Column(models.String(255), unique=True)
    creation_date = models.Column(models.DateTime, unique=True)
    content = models.Column(models.Text)

    def __init__(self, title, creation_date, content=""):
        self.title = title
        self.creation_date = creation_date
        self.content = content

    def __repr__(self):
        return '<Post title={} creation_date={}>'.format(self.title, self.creation_date)


def db_create_all():
    models.create_all()

