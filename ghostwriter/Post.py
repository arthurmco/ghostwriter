#   Represents a blog post
#
#   This file is from the Ghostwriter software
#   Copyright (C) 2017 Arthur M

from datetime import datetime

class Post(object):
    def __init__(self, ownerid, title, creation_date=None):
        self._title = title
        if creation_date is None:
            creation_date = datetime.utcnow()
        self._ownerid = ownerid
        self._creation_date = creation_date
        self._id = -1
        self._content = ""
        
    def setContent(self, data):
        """ Set the post content. 
            The post content is composed of an XHTML file (basically, HTML
            with XML syntax (so we can validate and reliably parse it)
        """
        self._content = data

    def appendContent(self, data):
        """ Append content after the end of the old one """
        self._content += data

    def getContent(self):
        return self._content

    def getSummary(self):
        """ Retrieve a short description of the blog, extracted from
            the content

            Preferably find a dot to end the summary, or end it with an
            ellipsis
        """
        summary = self._content[:128]
        if len(summary) < 128:
            return summary
        
        ldot = summary.rfind('.')
        if ldot < 0:
            return summary + '...'
        else:
            return summary[:ldot]

    @property 
    def title(self):
        return self._title

    @title.setter
    def title(self, val):
        self._title = val

    @property
    def creation_date(self):
        return self._creation_date

    @creation_date.setter
    def creation_date(self, date):
        self._creation_date = date

    @property
    def ID(self):
        return self._id

    def getOwner(self):
        from ghostwriter.UserManager import get_user_manager, UserManager
        return get_user_manager().getUserbyID(self._ownerid)


from ghostwriter.models.models import MPost

class PostManager(object):
    def getPostbyID(self, postid):
        """ Retrieve post data of id 'postid', or None if no one """
        mp = MPost.query.get(postid)
        if mp is None:
            return None

        post = Post(mp.user_id, mp.title, mp.creation_date)
        post._id = mp.id
        post.setContent(mp.content)
        return post
    
    def getPostsbyTitle(self, title):
        """ Retrieve all posts that contain 'title' in its title
            If none is found, return None
        """
        mp = MPost.query.filter(MPost.title.find(title)).all()
        if mp is None:
            return None

        posts = []
        for mpitem in mp:
            post = Post(mp.user_id, mp.title, mp.creation_date)
            post._id = mp.id
            post.setContent(mp.content)
            posts.append(post)

        return posts

    def getAllPosts(self, start=0, end=None):
        """
            Get all posts, by creation date descending order, from 'start'
            to 'start+end' .
            If none is found, return an empty list

        """
        mpq = MPost.query.order_by(MPost.creation_date.desc()).offset(start)
        if not (end is None):
            mpq = mpq.limit(end)
        
        mp = mpq.all();
        if mp is None:
            return []
        
        posts = []
        for mpitem in mp:
            post = Post(mpitem.user_id, mpitem.title, mpitem.creation_date)
            post._id = mpitem.id
            post.setContent(mpitem.content)
            posts.append(post)

        return posts

    def addPost(self, post):
        """ Adds a post """
        from ghostwriter.models.models import models
        mp = MPost(post.getOwner().uid, post.title, post.creation_date, post.getContent())
        models.session.add(mp)
        models.session.commit()
        post._id = mp.id
        

    def updatePostMetadata(self, post):
        """ Updates post metadata """
        from ghostwriter.models.models import models
        if post._id < 0:
            return False
        
        mp = MPost.query.get(post.ID)
        if mp is None:
            return False
        
        mp.title = post.title
        models.session.commit()

    def updatePostContent(self, post):
        """ Updates post content """
        from ghostwriter.models.models import models
        if post._id < 0:
            return False
        
        mp = MPost.query.get(post.ID)
        if mp is None:
            return False
        
        mp.content = post.getContent()
        models.session.commit()


    def removePost(self, post):
        """ Remove a post. Return false if post does not exist """
        if post.ID < 0:
            return False
        
        mp = MPost.query.get(post.ID)
        if mp is None:
            return False

        from ghostwriter.models.models import models
        models.session.delete(mp)
        models.session.commit()
        post._id = -1
        return True

