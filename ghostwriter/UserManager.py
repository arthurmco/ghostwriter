from ghostwriter.models.models import MUser, models
from ghostwriter.User import User
from datetime import datetime

class UserManager():

    def __init__(self):
        self.logged_list = []

    def _castPermissionToNumber(self, permissions):
        from ghostwriter.User import UserPerm

        permn = 0
        for perm in permissions:
            permn |= perm.value

        return permn

    def _castNumberToPermission(self, num):
        from ghostwriter.User import UserPerm

        perms = []
        for n in (p.value for p in UserPerm):
            if (num & n):
                perms.append(UserPerm(n))

        return perms

    def registerLogIn(self, user, password_hash):
        """ Register login in database.
            Return the session token if login is OK, None if it isn't """
        from sqlalchemy import and_
        mu = MUser.query.filter(and_(MUser.username == user.username, 
                                MUser.password_hash == password_hash))
        if (len(mu.all()) <= 0):
            return None

        session_token = str(datetime.utcnow()).encode('utf-8')
        self.logged_list.append(user)
        return session_token

    def getLoggedUsersbyToken(self, token):
        us = []
        for user in self.logged_list:
            if user.session_token == token:
                us.append(user)

        if len(us) <= 0:
            return None

        return us

    def updateUser(self, user):
        mus = MUser.query.get(user.uid)
        if mus is None:
            return False

        mus.username = user.username
        mus.name = user.name
        mus.security_flags = self._castPermissionToNumber(user.permissions)
        models.session.commit()
        return True        

    def getAllUsers(self, start=0, end=None):
        """ Get all posts by IDorder, from start to start+end.
            If none found, return empty list
        """
        us = []

        muq = MUser.query.order_by(MPost.id).offset(start)
        if not (end is None):
            muq = muq.limit(end)

        mu = muq.all()
        if mu is None:
            return []
        
        for muitem in mu:
            u = User(mu.username, mu.name, self._castNumberToPermission(mu.security_flags))
            u._id = mu.id
            us.append(u)

        return us

    def getUserbyID(self, uid):
        mu = MUser.query.get(uid)
        if mu is None:
            return None

        u = User(mu.username, mu.name, self._castNumberToPermission(mu.security_flags))
        u._id = mu.id
        return u;

    def removeUser(self, user):
        """ Remove an user.
            Return false if user doesn't exist
        """
        if user.uid < 0:
            return False

        mu = MUser.query.get(user.uid)
        if mu is None:
            return False

        models.session.delete(mu)
        models.session.commit()
        user._id = -1
        return True

    def getUserbyUsername(self, uname):
        mu = MUser.query.filter_by(username=uname).first()
        if mu is None:
            return None

        u = User(mu.username, mu.name)
        u._id = mu.id
        return u;

    def addUser(self, user, password):
        import hashlib
        password_hash = hashlib.sha1(password.encode('utf-8')).hexdigest()
        mu = MUser(user.username, password_hash, self._castPermissionToNumber(user.permissions), user.name)
        models.session.add(mu)
        models.session.commit()
        
        #
        #   TODO: Treat the SQLIntegrity error that occurs when we try tp
        #   add an existing user
        #

        user._id = mu.id

um = UserManager()
def get_user_manager():
    return um


