#
#   Ghostwriter test suite
#
#   Copyright (C) 2017 Arthur M
#

import unittest
from . import app, mm

class PostArticleTestCase(unittest.TestCase):
    def setUp(self):
        mm.setDatabaseURI('sqlite:////tmp/unittest.db')
        mm.init()
        mm.create()
        self.app = app.test_client()

    def tearDown(self):
        mm.drop()
   
    def test_create_blog_post_unauthenticated(self):
        pass
    
    def test_create_blog_post_authenticated(self):
        pass

    def test_create_and_read_blog_post(self):
        pass

    def test_get_content(self):
        pass

    def test_set_and_get_content(self):
        pass

    def test_delete_blog_post(self):
        pass


class LoginTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        mm.setDatabaseURI('sqlite:////tmp/unittest.db')
        mm.create()
        self.username = ""
        self.password = ""

    def create_user(self):
        from ghostwriter.User import User, UserManager
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

        self.assertTrue(res.status == "401 UNAUTHORIZED")  

    def test_login_good_user_bad_pass(self):
        us = self.create_user()
        res = self.app.post('/admin/login', 
            data = {
                'username': self.username,
                'password': 'garotoixpertinho'
            }, follow_redirects=True)

        self.assertTrue(res.status == "401 UNAUTHORIZED")  

    def test_login(self):
        us = self.create_user()
        res = self.app.post('/admin/login', 
            data = {
                'username': self.username,
                'password': self.password
            }, follow_redirects=True)

        self.assertTrue(res.status == "200 OK")

    def test_login_and_logoff(self):
        us = self.create_user()
        res = self.app.post('/admin/login', 
            data = {
                'username': self.username,
                'password': self.password
            }, follow_redirects=True)

        self.assertTrue(res.status == "200 OK")  

        res = self.app.get('/admin/logoff', follow_redirects=True)
        self.assertTrue(res.status == "200 OK")  
        

    def test_access_unauthenticated(self):
        us = self.create_user()
        res = self.app.post('/admin/login', 
            data = {
                'username': self.username,
                'password': self.password
            }, follow_redirects=True)

        self.assertTrue(res.status == "200 OK")  
        res = self.app.post('/api/post/create/',
            data = {
                'title': 'Test Post'
            }, follow_redirects=True)

        self.assertTrue(res.status == "200 OK")  
        # TODO: check returned JSON
        

    def test_access_unauthenticated_after_logoff(self):
        us = self.create_user()
        res = self.app.post('/admin/login', 
            data = {
                'username': self.username,
                'password': self.password
            }, follow_redirects=True)

        self.assertTrue(res.status == "200 OK")  
        
        res = self.app.get('/admin/logoff', follow_redirects=True)
        self.assertTrue(res.status == "200 OK")  
        
        res = self.app.post('/api/post/create/',
            data = {
                'title': 'Test Post'
            }, follow_redirects=True)

        self.assertTrue(res.status == "401 UNAUTHORIZED")  


if __name__ == '__main__':
    unittest.main(verbosity=2)

