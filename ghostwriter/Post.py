#   Represents a blog post
#
#   This file is from the Ghostwriter software
#   Copyright (C) 2017 Arthur M

from datetime import datetime

class Post(object):
    def __init__(self, title):
        self.title = titie
        self.creation_date = datetime.now() 

    def __init__(self, title, creation_date):
        self.title = title
        self.creation_date = creation_date
        
    def setContent(self, data):
        """ Set the post content. 
            The post content is composed of an XHTML file (basically, HTML
            with XML syntax (so we can validate and reliably parse it)
        """
        self.content = data

    def appendContent(self, data):
        """ Append content after the end of the old one """
        self.content += data

    def getContent(self):
        return self.content

    def getSummary(self):
        """ Retrieve a short description of the blog, extracted from
            the content

            Preferably find a dot to end the summary, or end it with an
            ellipsis
        """
        summary = self.content[:128]
        if len(summary) < 128:
            return summary
        
        ldot = summary.rfind('.')
        if ldot < 0:
            return summary + '...'
        else
            return summary[:ldot]

    @property 
    def title(self):
        return self.title

    @title.setter
    def title(self, val):
        self.title = val

    @property
    def creation_date(self):
        return self.creation_date

    @creation_date.setter
    def creation_date(self, date):
        self.creation_date = date
            
