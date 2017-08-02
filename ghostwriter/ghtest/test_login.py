import unittest
from ghostwriter import app, mm

#
#
#   Authentication tests
#   Copyright (C) 2017 Arthur M
#
class LoginTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        mm.setDatabaseURI('sqlite:////tmp/unittest.db')
        mm.create()
        self.username = ""
        self.password = ""

    def create_user(self):
        from ghostwriter.User import User
        from ghostwriter.UserManager import UserManager
        self.username = 'malakoi'
        self.password = 'dandoboura'
        u = User(self.username)
        umng = UserManager()
        umng.addUser(u, self.password)
        return u

    def tearDown(self):
        mm.drop()

    def test_login_bad_user_good_pass(self):
        us = self.create_user()
        res = self.app.post('/admin/login', 
            data = {
                'username': 'devaxos',
                'password': self.password
            }, follow_redirects=True)

        self.assertEqual(res.status,  "401 UNAUTHORIZED")  

    def test_login_good_user_bad_pass(self):
        us = self.create_user()
        res = self.app.post('/admin/login', 
            data = {
                'username': self.username,
                'password': 'garotoixpertinho'
            }, follow_redirects=True)

        self.assertEqual(res.status,  "401 UNAUTHORIZED")  

    def test_login(self):
        us = self.create_user()
        res = self.app.post('/admin/login', 
            data = {
                'username': self.username,
                'password': self.password
            }, follow_redirects=True)

        self.assertEqual(res.status,  "200 OK")

    def test_login_and_logoff(self):
        us = self.create_user()
        res = self.app.post('/admin/login', 
            data = {
                'username': self.username,
                'password': self.password
            }, follow_redirects=True)

        self.assertEqual(res.status,  "200 OK")  

        res = self.app.get('/admin/logoff', follow_redirects=True)
        self.assertEqual(res.status,  "200 OK")  
        
    def test_access_unauthenticated(self):
        us = self.create_user()
        res = self.app.post('/admin/login', 
            data = {
                'username': self.username,
                'password': self.password
            }, follow_redirects=True)

        self.assertEqual(res.status, "200 OK")  
        res = self.app.post('/api/post/create/',
            data = {
                'title': 'Test Post'
            }, follow_redirects=True)

        self.assertEqual(res.status, "200 OK")  
        # TODO: check returned JSON
        
    def test_access_unauthenticated_after_logoff(self):
        us = self.create_user()
        res = self.app.post('/admin/login', 
            data = {
                'username': self.username,
                'password': self.password
            }, follow_redirects=True)

        self.assertEqual(res.status,  "200 OK")  
        
        res = self.app.get('/admin/logoff', follow_redirects=True)
        self.assertEqual(res.status,  "200 OK")  
        
        res = self.app.post('/api/post/create/',
            data = {
                'title': 'Test Post'
            }, follow_redirects=True)

        self.assertEqual(res.status, "401 UNAUTHORIZED")  


