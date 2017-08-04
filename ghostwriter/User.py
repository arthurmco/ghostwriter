#
#   User management class
#
#   Copyright (C) 2017 Arthur M

from datetime import datetime
from enum import Enum, unique
import six

@unique
class UserPerm(Enum):
    """ Some permissions for the user
        Note that each user can manage itself and it's own posts """

    CREATEPOST = 0x1
    MANAGEPOSTS = 0x2
    VIEWUSERS  = 0x100
    CREATEUSER = 0x200
    MANAGEUSERS = 0x400
    ADMIN = 0xffffffff

class UserCreationException(Exception):
    """ Exception raised when someone tries to create an invalid user """
    pass

class User(object):
    """
        This user class is a wrapper between the flask_login user class and
        the user database

        Some decisions (like storing the session token as a utf-8 string) were
        done to be compatible with this library
    """
    def __init__(self, username, name=None, 
            permissions = [UserPerm.CREATEPOST, UserPerm.VIEWUSERS]):
        self._username = username
        self._name = username if name is None else name
        self._id = -1
        self.session_token = 'UL'
        self._authenticated = False

        if len(permissions) == 0:
            raise UserCreationException("Can't create an user with any permission")
        
        self._permissions = permissions

    def _fillPermissions(self):
        postPerms = [UserPerm.CREATEPOST, UserPerm.MANAGEPOSTS]
        userPerms = [UserPerm.VIEWUSERS, UserPerm.CREATEUSER, UserPerm.MANAGEUSERS]
        addPermissions = []

        for perm in self._permissions:
            if perm == UserPerm.ADMIN:
                addPermissions = postPerms + userPerms
                break

            for idx, pperm in enumerate(postPerms):
                if pperm == perm:
                    addPermissions = addPermissions + postPerms[:idx]

            for idx, uperm in enumerate(userPerms):
                if uperm == perm:
                    addPermissions = addPermissions + userPerms[:idx]

        return list(set(self._permissions + addPermissions)) 

    def login(self, password, umng):
        import hashlib
        """ Log in the user. Uses SHA1 to encode the password """
        password_hash = hashlib.sha1(password.encode('utf-8')).hexdigest()
        stoken = umng.registerLogIn(self, password_hash)
        if stoken is None:
            return False

        self.session_token = stoken.decode('utf-8')
        self._authenticated = True
        return True

    def checkPermission(self, perm):
        """ Check if user has a predefined permission """
        self._permissions = self._fillPermissions()

        return (perm in self._permissions)

    @property
    def uid(self):
        return self._id

    @property
    def permissions(self):
        self._permissions = self._fillPermissions()
        return self._permissions

    @permissions.setter
    def permissions(self, val):
        self._permissions = val
        


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

    @username.setter
    def username(self, value):
        self._username = value

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, val):
        self._name = val

    def __repr__(self):
        return '<User {}, is_auth={}, session_token={}, name={} id={}>'.format(
                self._username, self._authenticated, self.session_token, self._name, self._id)

