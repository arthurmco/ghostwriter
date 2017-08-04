import unittest
from ghostwriter import app, mm

#
#   Post basic test fixture(?)
#   Copyright (C) 2017 Arthur M
#
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
        from ghostwriter.User import User
        from ghostwriter.UserManager import UserManager
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

        self.assertEqual(res.status,  "200 OK")

    def deauthenticate(self):
        res = self.app.get('/admin/logoff', follow_redirects=True)
        self.assertEqual(res.status,  "200 OK")  
   
    def test_create_blog_post_unauthenticated(self):
        res = self.app.post('/api/post/create/',
                data = {
                    'title': "This won't work"
                }, follow_redirects=True)

        self.assertEqual(res.status,  "401 UNAUTHORIZED")
    
    def test_create_blog_post_authenticated(self):
        self.authenticate()
        res = self.app.post('/api/post/create/',
                data = {
                    'title': "This will work"
                }, follow_redirects=True)

        self.assertEqual(res.status, "200 OK")
        self.deauthenticate()

    def test_create_and_read_blog_post(self):
        from flask import json

        self.authenticate()
        res = self.app.post('/api/post/create/',
                data = {
                    'title': "This will maybe work"
                }, follow_redirects=True)

        self.assertEqual(res.status, "200 OK")
        create_post_data = json.loads(res.data)

        res = self.app.get('/api/post/'+str(create_post_data['id'])+'/',
                follow_redirects=True)
        get_post_data = json.loads(res.data)

        self.assertEqual(get_post_data['id'], create_post_data['id'])
        self.assertEqual(get_post_data['title'], create_post_data['title'])
        self.assertEqual(get_post_data['creation_date'], create_post_data['creation_date'])
        self.assertEqual(get_post_data['summary'], create_post_data['summary'])
        self.assertEqual(1, get_post_data['owner']['id'])
        self.assertEqual(self.username, get_post_data['owner']['name'])

        self.deauthenticate()

    def test_get_content(self):
        self.authenticate()
        from ghostwriter.Post import Post, PostManager
        from flask import json
        
        p = Post(1, 'Get Content Test')
        p.setContent('Post content')
        pm = PostManager()
        pm.addPost(p)

        res = self.app.get('/api/post/'+str(p.ID)+'/content',
                follow_redirects=True)
        self.assertEqual(res.status,  '200 OK')
        post_data = res.data
        self.assertEqual(b'Post content', post_data)

        self.deauthenticate()

    def test_set_and_get_content(self):
        self.authenticate()
        from ghostwriter.Post import Post, PostManager
        from flask import json
        
        p = Post(1, 'Get Content Test')
        p.setContent('Post content')
        pm = PostManager()
        pm.addPost(p)

        res = self.app.put('/api/post/'+str(p.ID)+'/content',
                data = {
                    'content': 'New Post content'
                },
                follow_redirects=True)
        self.assertEqual(res.status,  '200 OK')

        res = self.app.get('/api/post/'+str(p.ID)+'/content',
                follow_redirects=True)
        self.assertEqual(res.status,  '200 OK')
        post_data = res.data
        self.assertEqual(b'New Post content', post_data)
        self.deauthenticate()

    def test_set_and_get_metadata(self):
        self.authenticate()
        from ghostwriter.Post import Post, PostManager
        from flask import json
        
        p = Post(1, 'Get Meta Test')
        p.setContent('Post content')
        pm = PostManager()
        pm.addPost(p)

        res = self.app.put('/api/post/'+str(p.ID)+'/',
                data = {
                    'title': 'New Meta Test'
                },
                follow_redirects=True)
        self.assertEqual(res.status,  '200 OK')

        res = self.app.get('/api/post/'+str(p.ID)+'/',
                follow_redirects=True)
        self.assertEqual(res.status,  '200 OK')
        post_data = json.loads(res.data)
        self.assertEqual('New Meta Test', post_data['title'])
        self.deauthenticate()

    def test_delete_blog_post(self):
        self.authenticate()
        from ghostwriter.Post import Post, PostManager
        from flask import json
        
        p = Post(1, 'Get Content Test')
        p.setContent('Post content')
        pm = PostManager()
        pm.addPost(p)

        res = self.app.delete('/api/post/'+str(p.ID)+'/',
                follow_redirects=True)
        self.assertEqual(res.status,  '200 OK')        
        res = self.app.delete('/api/post/'+str(p.ID)+'/',
                follow_redirects=True)
        self.assertEqual(res.status,  '404 NOT FOUND')

#
#   Post composition
class PostComposeTestCase(unittest.TestCase):
    from flask import json

    def setUp(self):
        mm.setDatabaseURI('sqlite:////tmp/unittest.db')
        mm.init()
        mm.create()
        self.app = app.test_client()
        self.user = self.create_user('test', 'test')

    def tearDown(self):
        mm.drop()

    def create_user(self, username, password):
        from ghostwriter.User import User
        from ghostwriter.UserManager import UserManager
        u = User(username)
        umng = UserManager()
        umng.addUser(u, password)       
        return u

    def create_post(self, title, body, author, cdate=None):
        from ghostwriter.Post import Post, PostManager
        
        po = Post(author.uid, title, cdate)
        po.setContent(body)

        return po

    def testIfSummaryCorrect(self):
        from ghostwriter.Post import Post

        p = self.create_post("New Post",
                """ This is a big summary
                    Note that we will have a lot of lines, but it finish here.
                    Lorem ipsum dolor sit amet Lorem ipsum dolor sit amet Lorem ipsum dolor sit amet Lorem ipsum dolor sit amet Lorem ipsum dolor sit amet Lorem ipsum dolor sit amet Lorem ipsum dolor sit amet Lorem ipsum dolor sit amet Lorem ipsum dolor sit amet """, self.user)
        
        cdata = p.getSummary()
        self.assertEqual('.', cdata[-1])
        self.assertNotEqual('...', cdata[-3:])

#
#   Post search tests
class PostSearchTestCase(unittest.TestCase):
    from flask import json

    def setUp(self):
        mm.setDatabaseURI('sqlite:////tmp/unittest.db')
        mm.init()
        mm.create()
        self.app = app.test_client()
        self.user = self.create_user('test', 'test')

    def tearDown(self):
        mm.drop()

    def create_user(self, username, password):
        from ghostwriter.User import User
        from ghostwriter.UserManager import UserManager
        u = User(username)
        umng = UserManager()
        umng.addUser(u, password)       
        return u

    def create_post(self, title, body, author, cdate=None):
        from ghostwriter.Post import Post, PostManager
        
        po = Post(author.uid, title, cdate)
        po.setContent(body)

        pm = PostManager()
        pm.addPost(po)

    def test_searchbyTitle(self):
        import json
        self.create_post("Search One", "Post Search One", self.user)
        self.create_post("Normal One", "Post Normal One", self.user)
        self.create_post("Search Two", "Post Search Two", self.user)
        self.create_post("Normal Two", "Post Normal Two", self.user)
        self.create_post("Search THree", "Post Search Three", self.user)
        self.create_post("Normal Three", "Post Normal Three", self.user)
        self.create_post("What is this", "Post different", self.user)

        res = self.app.get('/api/post/search',
                query_string = {
                        'title': 'Search'
                }, follow_redirects=True)

        self.assertEqual(res.status,  '200 OK')
        post_data = json.loads(res.data)
        self.assertEqual(3, len(post_data))

    def test_searchbyAuthor(self):
        import json
        other = self.create_user('other', 'other')
        self.create_post("Search One", "Post Search One", self.user)
        self.create_post("Normal One", "Post Normal One", self.user)
        self.create_post("Search Two", "Post Search Two", other)
        self.create_post("Normal Two", "Post Normal Two", other)
        self.create_post("Search THree", "Post Search Three", other)
        self.create_post("Normal Three", "Post Normal Three", other)
        self.create_post("What is this", "Post different", self.user)

        res = self.app.get('/api/user/1/posts', follow_redirects=True)

        self.assertEqual(res.status,  '200 OK')
        post_data = json.loads(res.data)
        self.assertEqual(3, len(post_data))

    def test_searchbyDate(self):
        from datetime import datetime
        import json
        self.create_post("Search One", "Post Search One", self.user, 
                datetime(2017, 7, 1, 1))
        self.create_post("Normal One", "Post Normal One", self.user)
        self.create_post("Search Two", "Post Search Two", self.user,
                datetime(2017, 7, 1, 2))
        self.create_post("Normal Two", "Post Normal Two", self.user)
        self.create_post("Search THree", "Post Search Three", self.user,
                datetime(2017, 7, 1, 3))
        self.create_post("Normal Three", "Post Normal Three", self.user)
        self.create_post("What is this", "Post different", self.user,
                datetime(2017, 7, 1, 4))

        res = self.app.get('/api/post/search', 
                query_string = {
                    'cdate': '2017-7-1',
                }, follow_redirects=True)

        self.assertEqual(res.status,  '200 OK')
        post_data = json.loads(res.data)
        self.assertEqual(4, len(post_data))

    def test_searchbyTitleandAuthor(self):
        other = self.create_user('other', 'other')
        import json
        self.create_post("Search One", "Post Search One", self.user)
        self.create_post("Normal One", "Post Normal One", self.user)
        self.create_post("Search Two", "Post Search Two", other)
        self.create_post("Normal Two", "Post Normal Two", other)
        self.create_post("Search THree", "Post Search Three", self.user)
        self.create_post("Normal Three", "Post Normal Three", other)
        self.create_post("What is this", "Post different", self.user)

        res = self.app.get('/api/user/1/posts/search', 
                query_string = {
                    'title': 'Search',
                }, follow_redirects=True)

        self.assertEqual(res.status,  '200 OK')
        post_data = json.loads(res.data)
        self.assertEqual(2, len(post_data))

    def test_searchbyDateandAuthor(self):
        from datetime import datetime
        import json
        other = self.create_user('other', 'other')
        self.create_post("Search One", "Post Search One", other, 
                datetime(2017, 7, 1, 1))
        self.create_post("Normal One", "Post Normal One", other)
        self.create_post("Search Two", "Post Search Two", self.user,
                datetime(2017, 7, 1, 2))
        self.create_post("Normal Two", "Post Normal Two", other)
        self.create_post("Search THree", "Post Search Three", self.user,
                datetime(2017, 7, 1, 3))
        self.create_post("Normal Three", "Post Normal Three", other)
        self.create_post("What is this", "Post different", self.user,
                datetime(2017, 7, 1, 4))

        res = self.app.get('/api/user/1/posts/search', 
                query_string = {
                    'cdate': '2017-7-1',
                }, follow_redirects=True)

        self.assertEqual(res.status,  '200 OK')
        post_data = json.loads(res.data)
        self.assertEqual(3, len(post_data))
