import unittest
from ghostwriter import app, mm

#
#
#   User management tests
#   Copyright (C) 2017 Arthur M
#
class UserManageTestCase(unittest.TestCase):
    from flask import json

    def setUp(self):
        mm.setDatabaseURI('sqlite:////tmp/unittest.db')
        mm.init()
        mm.create()
        self.app = app.test_client()
        self.username = "test"
        self.password = "test"
        self.create_user('test', 'test')

    def tearDown(self):
        mm.drop()

    def create_user(self, name, pwd):
        from ghostwriter.User import User
        from ghostwriter.UserManager import UserManager
        u = User(name)
        umng = UserManager()
        umng.addUser(u, pwd)
        return u

    def authenticate(self):
        res = self.app.post('/admin/login', 
            data = {
                'username': self.username,
                'password': self.password
            }, follow_redirects=True)

        self.assertEqual(res.status,  "200 OK")

    def test_create_user_unauthenticated(self):
        res = self.app.post('/api/users/', data = {
                'username': 'teste',
                'password': 'pasteldebacon',
                'name': 'Teste'
            }, follow_redirects=True)
        self.assertEqual('401 UNAUTHORIZED', res.status)

    def test_delete_user_unauthenticated(self):
        u = self.create_user('deletenoauth', 'deletenoauth')
        res = self.app.delete('/api/user/2/', 
                follow_redirects=True)
        self.assertEqual('401 UNAUTHORIZED', res.status)

    def test_create_user_authenticated(self):
        from flask import json
        import hashlib
        self.authenticate()
        res = self.app.post('/api/users/', data = {
                'username': 'teste',
                'password': 'pasteldebacon',
                'name': 'Teste'
            }, follow_redirects=True)
        self.assertEqual('200 OK', res.status)
        user_load = json.loads(res.data)
        
        from ghostwriter.User import User
        from ghostwriter.UserManager import UserManager
        um = UserManager()
        u = um.getUserbyID(user_load['id'])
        self.assertEqual(u.uid, user_load['id'])
        self.assertEqual(u.username, user_load['username'])
        self.assertEqual(u.name, user_load['name'])
    
        password_hash = hashlib.sha1(b'pasteldebacon').hexdigest()
        self.assertIsNotNone(um.registerLogIn(u, password_hash))

    def test_delete_user_authenticated(self):
        self.authenticate()
        u = self.create_user('deletenoauth', 'deletenoauth')
        res = self.app.delete('/api/user/2/', 
                follow_redirects=True)
        self.assertEqual('200 OK', res.status)
        
        res = self.app.delete('/api/user/2/', 
                follow_redirects=True)
        self.assertEqual('404 NOT FOUND', res.status)

    def test_load_user(self):
        from flask import json
        import hashlib
        self.authenticate()
        u = self.create_user('malakoi', 'devasso')
        res = self.app.get('/api/user/2/', 
                follow_redirects=True)
        self.assertEqual('200 OK', res.status)
        user_load = json.loads(res.data)
        
        from ghostwriter.User import User
        from ghostwriter.UserManager import UserManager
        um = UserManager()
        u = um.getUserbyID(user_load['id'])
        self.assertEqual(u.uid, user_load['id'])
        self.assertEqual(u.username, user_load['username'])
        self.assertEqual(u.name, user_load['name'])
        
        password_hash = hashlib.sha1(b'devasso').hexdigest()
        self.assertIsNotNone(um.registerLogIn(u, password_hash))

    def test_permissionvalidationFull(self):
        from ghostwriter.User import User, UserPerm

        u = User("test", "Test", [UserPerm.MANAGEPOSTS, UserPerm.MANAGEUSERS])

        self.assertTrue(u.checkPermission(UserPerm.CREATEPOST))
        self.assertTrue(u.checkPermission(UserPerm.MANAGEPOSTS))
        self.assertTrue(u.checkPermission(UserPerm.VIEWUSERS))
        self.assertTrue(u.checkPermission(UserPerm.CREATEUSER))
        self.assertTrue(u.checkPermission(UserPerm.MANAGEUSERS))
        self.assertFalse(u.checkPermission(UserPerm.ADMIN))
    
    def test_permissionvalidationPartial(self):
        from ghostwriter.User import User, UserPerm

        u = User("test", "Test", [UserPerm.MANAGEPOSTS, UserPerm.VIEWUSERS])

        self.assertTrue(u.checkPermission(UserPerm.CREATEPOST))
        self.assertTrue(u.checkPermission(UserPerm.MANAGEPOSTS))
        self.assertTrue(u.checkPermission(UserPerm.VIEWUSERS))
        self.assertFalse(u.checkPermission(UserPerm.CREATEUSER))
        self.assertFalse(u.checkPermission(UserPerm.MANAGEUSERS))
        self.assertFalse(u.checkPermission(UserPerm.ADMIN))

    def test_permissionvalidationNone(self):
        from ghostwriter.User import User, UserCreationException, UserPerm

        with self.assertRaises(UserCreationException):
            u = User("test", "test", [])

    def test_update_user(self):
        from flask import json
        from ghostwriter.User import User
        from ghostwriter.UserManager import UserManager

        self.authenticate()
        u = self.create_user('malakoi', 'devasso')
        res = self.app.put('/api/user/2/', data = {
                'name': 'Ixpertinho', 
                'username': 'garoto'
            }, follow_redirects=True)
        self.assertEqual('200 OK', res.status)

        um = UserManager()
        u = um.getUserbyID(2)
        self.assertEqual('Ixpertinho', u.name)
        self.assertEqual('garoto', u.username)

