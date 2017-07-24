#
#   User management class
#
#   Copyright (C) 2017 Arthur M

from datetime import datetime

class User(object):
    """
        This user class is a wrapper between the flask_login user class and
        the user database

        Some decisions (like storing the session token as a utf-8 string) were
        done to be compatible with this library
    """
    def __init__(self, username, name=None):
        self._username = username
        self._name = username if name is None else name
        self._id = -1
        self.session_token = 'UL'

    def login(self, password):
        import hashlib
        """ Log in the user. Uses SHA1 to encode the password """
        u = get_user_manager()
        password_hash = hashlib.sha1(password.encode('utf-8')).hexdigest()
        stoken = u.registerLogIn(self, password_hash)
        if stoken is None:
            return False

        self.session_token = stoken.decode('utf-8')
        self._authenticated = True
        return True

    @property
    def uid(self):
        return self._id


    # flask_login proprierties and methods

    @property
    def is_authenticated(self):
        return self._authenticated

    @property
    def is_active(self):
        return True # We don't support inactive accounts yet

    @property
    def is_anonymous(self):
        return (self._id < 0)

    def get_id(self):
        return (str(self._id) + '|' + self.session_token)
    
    @property
    def username(self):
        return self._username

    @property
    def name(self):
        return self._name


    def __repr__(self):
        return '<User {}, is_auth={}, session_token={}, name={} >'.format(
                self._username, self._authenticated, self.session_token, self._name)

class UserManager():

    def __init__(self):
        self.logged_list = []

    def registerLogIn(self, user, password_hash):
        """ Register login in database.
            Return the session token if login is OK, None if it isn't """
        from ghostwriter.models.models import MUser
        from sqlalchemy import and_
        mu = MUser.query.filter(and_(MUser.username == user.username, 
                                MUser.password_hash == password_hash))
        if (len(mu.all()) <= 0):
            return None

        session_token = str(datetime.utcnow()).encode('utf-8')
        self.logged_list.append(user)
        return session_token

    def getLoggedUsersbyToken(self, token):
        from ghostwriter.models.models import MUser
        us = []
        for user in self.logged_list:
            if user.session_token == token:
                us.append(user)

        if len(us) <= 0:
            return None

        return us


    def getUserbyID(self, uid):
        from ghostwriter.models.models import MUser
        mu = MUser.query.get(postid)
        if mu is None:
            return None

        u = User(mu.username, mu.name)
        u._id = mu.id
        return u;

    def getAllUsers(self):
        from ghostwriter.models.models import MUser
        mus = MUser.query.all()
        if mus is None:
            return None

        us = []
        for mu in mus:
            u = User(mu.username, mu.name)
            u._id = mu.id
            us.append(u)

        return us


    def getUserbyUsername(self, uname):
        from ghostwriter.models.models import MUser
        mu = MUser.query.filter_by(username=uname).first()
        if mu is None:
            return None

        u = User(mu.username, mu.name)
        u._id = mu.id
        return u;

    def addUser(self, user, password):
        import hashlib
        from ghostwriter.models.models import MUser, models
        password_hash = hashlib.sha1(password.encode('utf-8')).hexdigest()
        mu = MUser(user.username, password_hash, user.name)
        models.session.add(mu)
        models.session.commit()
        
        #
        #   TODO: Treat the SQLIntegrity error that occurs when we try tp
        #   add an existing user
        #

        user._id = mu.id

umng = UserManager()
def get_user_manager():
    return umng


