#   Database models for GhostWriter
#
#   Copyright (C) 2017 Arthur M
#

from flask_sqlalchemy import SQLAlchemy
from ghostwriter import app

models = app.config['GHOSTWRITER_DATABASE'].database

class MPost(models.Model):
    id = models.Column(models.Integer, primary_key=True, autoincrement=True)
    title = models.Column(models.String(255), unique=True)
    creation_date = models.Column(models.DateTime, unique=True)
    content = models.Column(models.Text)
    user_id = models.Column(models.Integer, models.ForeignKey('m_user.id'))

    def __init__(self, title, creation_date, content=""):
        self.title = title
        self.creation_date = creation_date
        self.content = content

    def __repr__(self):
        return '<Post title={} creation_date={}>'.format(self.title, self.creation_date)


class MUser(models.Model):
    id = models.Column(models.Integer, primary_key=True, autoincrement=True)
    username = models.Column(models.String(64), unique=True)
    password_hash = models.Column(models.String(512))
    name = models.Column(models.String(128))
    security_flags = models.Column(models.Integer)
    posts = models.relationship('MPost', backref='user', lazy='dynamic')

    def __init__(self, username, password_hash, name=None):
        self.username = username
        self.password_hash = password_hash
        if name is None:
            self.name = username
        else:
            self.name = name


    def __repr__(self):
        return '<User username={} pwd_hash={} name={}'.format(self.username, self.password_hash, self.name)







def db_create_all():
    models.create_all()

