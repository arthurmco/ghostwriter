#
#   Ghostwriter test suite
#
#   Copyright (C) 2017 Arthur M
#

import unittest
from . import app, mm

class PostArticleTestCase(unittest.TestCase):
    from flask import json

    def setUp(self):
        mm.setDatabaseURI('sqlite:////tmp/unittest.db')
        mm.init()
        mm.create()
        self.app = app.test_client()
        self.username = ""
        self.password = ""
        self.create_user()


    def tearDown(self):
        mm.drop()

    def create_user(self):
        from ghostwriter.User import User, UserManager
        self.username = 'malakoi'
        self.password = 'dandoboura'
        u = User(self.username)
        umng = UserManager()
        umng.addUser(u, self.password)       

    def authenticate(self):
        res = self.app.post('/admin/login', 
            data = {
                'username': self.username,
                'password': self.password
            }, follow_redirects=True)

        self.assertEquals(res.status,  "200 OK")

    def deauthenticate(self):
        res = self.app.get('/admin/logoff', follow_redirects=True)
        self.assertEquals(res.status,  "200 OK")  
   
    def test_create_blog_post_unauthenticated(self):
        res = self.app.post('/api/post/create/',
                data = {
                    'title': "This won't work"
                }, follow_redirects=True)

        self.assertEquals(res.status,  "401 UNAUTHORIZED")
    
    def test_create_blog_post_authenticated(self):
        self.authenticate()
        res = self.app.post('/api/post/create/',
                data = {
                    'title': "This will work"
                }, follow_redirects=True)

        self.assertEquals(res.status, "200 OK")
        self.deauthenticate()

    def test_create_and_read_blog_post(self):
        from flask import json

        self.authenticate()
        res = self.app.post('/api/post/create/',
                data = {
                    'title': "This will maybe work"
                }, follow_redirects=True)

        self.assertEquals(res.status, "200 OK")
        create_post_data = json.loads(res.data)

        res = self.app.get('/api/post/'+str(create_post_data['id'])+'/',
                follow_redirects=True)
        get_post_data = json.loads(res.data)

        self.assertEqual(get_post_data['id'], create_post_data['id'])
        self.assertEqual(get_post_data['title'], create_post_data['title'])
        self.assertEqual(get_post_data['creation_date'], create_post_data['creation_date'])
        self.assertEqual(get_post_data['summary'], create_post_data['summary'])

        self.deauthenticate()

    def test_get_content(self):
        self.authenticate()
        from ghostwriter.Post import Post, PostManager
        from flask import json
        
        p = Post('Get Content Test')
        p.setContent('Post content')
        pm = PostManager()
        pm.addPost(p)

        res = self.app.get('/api/post/'+str(p.ID)+'/content',
                follow_redirects=True)
        self.assertEquals(res.status,  '200 OK')
        post_data = res.data
        self.assertEqual(b'Post content', post_data)

        self.deauthenticate()

    def test_set_and_get_content(self):
        self.authenticate()
        from ghostwriter.Post import Post, PostManager
        from flask import json
        
        p = Post('Get Content Test')
        p.setContent('Post content')
        pm = PostManager()
        pm.addPost(p)

        res = self.app.put('/api/post/'+str(p.ID)+'/content',
                data = {
                    'content': 'New Post content'
                },
                follow_redirects=True)
        self.assertEquals(res.status,  '200 OK')

        res = self.app.get('/api/post/'+str(p.ID)+'/content',
                follow_redirects=True)
        self.assertEquals(res.status,  '200 OK')
        post_data = res.data
        self.assertEqual(b'New Post content', post_data)
        self.deauthenticate()

    def test_delete_blog_post(self):
        self.authenticate()
        from ghostwriter.Post import Post, PostManager
        from flask import json
        
        p = Post('Get Content Test')
        p.setContent('Post content')
        pm = PostManager()
        pm.addPost(p)

        res = self.app.delete('/api/post/'+str(p.ID)+'/',
                follow_redirects=True)
        self.assertEquals(res.status,  '200 OK')
        
        res = self.app.delete('/api/post/'+str(p.ID)+'/',
                follow_redirects=True)
        self.assertEquals(res.status,  '404 NOT FOUND')
        

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

        self.assertEquals(res.status,  "401 UNAUTHORIZED")  

    def test_login_good_user_bad_pass(self):
        us = self.create_user()
        res = self.app.post('/admin/login', 
            data = {
                'username': self.username,
                'password': 'garotoixpertinho'
            }, follow_redirects=True)

        self.assertEquals(res.status,  "401 UNAUTHORIZED")  

    def test_login(self):
        us = self.create_user()
        res = self.app.post('/admin/login', 
            data = {
                'username': self.username,
                'password': self.password
            }, follow_redirects=True)

        self.assertEquals(res.status,  "200 OK")

    def test_login_and_logoff(self):
        us = self.create_user()
        res = self.app.post('/admin/login', 
            data = {
                'username': self.username,
                'password': self.password
            }, follow_redirects=True)

        self.assertEquals(res.status,  "200 OK")  

        res = self.app.get('/admin/logoff', follow_redirects=True)
        self.assertEquals(res.status,  "200 OK")  
        
    def test_access_unauthenticated(self):
        us = self.create_user()
        res = self.app.post('/admin/login', 
            data = {
                'username': self.username,
                'password': self.password
            }, follow_redirects=True)

        self.assertEquals(res.status, "200 OK")  
        res = self.app.post('/api/post/create/',
            data = {
                'title': 'Test Post'
            }, follow_redirects=True)

        self.assertEquals(res.status, "200 OK")  
        # TODO: check returned JSON
        
    def test_access_unauthenticated_after_logoff(self):
        us = self.create_user()
        res = self.app.post('/admin/login', 
            data = {
                'username': self.username,
                'password': self.password
            }, follow_redirects=True)

        self.assertEquals(res.status,  "200 OK")  
        
        res = self.app.get('/admin/logoff', follow_redirects=True)
        self.assertEquals(res.status,  "200 OK")  
        
        res = self.app.post('/api/post/create/',
            data = {
                'title': 'Test Post'
            }, follow_redirects=True)

        self.assertEquals(res.status, "401 UNAUTHORIZED")  


if __name__ == '__main__':
    unittest.main(verbosity=2)

