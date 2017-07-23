#
#   User management class
#
#   Copyright (C) 2017 Arthur M

from datetime import datetime

class User(object):
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
        if not u.registerLogIn(self.username, password_hash):
            return False

        self._authenticated = True
        return True

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
        return unicode(self._id + ':' + self.session_token)

    @property
    def username(self):
        return self._username

    @property
    def name(self):
        return self._name

class UserManager():
    from ghostwriter.models.models import MUser
    def __init__(self):
        self.logged_list = []

    def registerLogIn(self, user, password_hash):
        """ Register login in database.
            Return true if login is OK, false if it isn't """
        mu = MUser.query.filter((MUser.username == user.username) and
                                (MUser.password_hash == password_hash))

        if (mu is None):
            return False

        user.session_token = unicode(str(datetime))
        self.logged_list.append(user)
        return True

    def getLoggedUserbyToken(self, user):
        users = (u for u in self.logged_list 
                    if (u.session_token == user.session_token) and
                    (u.ID == user.ID))
        if len(users) <= 0:
            return None

        return users[0]


    def getUserbyID(self, uid):
        mu = MUser.query.get(postid)
        if mu is None:
            return None

        u = User(mu.username, mu.name)
        u._id = mu.id
        return u;

    def getAllUsers(self):
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
        mu = MUser.query.filter_by(username=uname)
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


