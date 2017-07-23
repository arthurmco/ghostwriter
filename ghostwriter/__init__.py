#  GhostWriter main file 
#  Copyright (C) 2017 Arthur M
#
from flask import Flask, request, jsonify;
from ghostwriter.models.model_manager import ModelManager

app = Flask("ghostwriter");

mm = ModelManager(app)
mm.setDatabaseURI('sqlite:////tmp/test.db')
mm.init()

# Test route
@app.route('/')
def test_run():
    return """Ghostwriter 0.0.1 installed successfully<br/> 
        Please disable this route in the setup (not existent yet) """


# REST interfaces
@app.route('/api/post/<int:id>/content', methods=['GET', 'PUT'])
def post_get_content(id):
    """ 
        Retrieves/sets post content
        Returns post data in its native XHTML format, or 404 if post not found

    """
    from ghostwriter.Post import Post, PostManager 
    pm = PostManager()
    post = pm.getPostbyID(id)

    if post is None:
        return '',404

    if request.method == 'GET':
        return post.getContent()

    if request.method == 'PUT':
        post.setContent(request.form['content'])
        pm.updatePostContent(post)
        return '',200

@app.route('/api/post/<int:id>/', methods=['GET'])
def post_get(id):
    """
        Retrieve post metadata in JSON format
        If post not found, give a 404 Not Found error
    """
    from ghostwriter.Post import Post, PostManager
    pm = PostManager()
    post = pm.getPostbyID(id)
    
    if post is None:
        return jsonify(
                {'error': 'The post could not be found'}), 404

    jdata = {   'id': post.ID,
                'title': post.title,
                'creation_date': post.creation_date.isoformat(),
                'summary': post.getSummary()
            }
    return jsonify(jdata), 200


@app.route('/api/post/create/', methods=['POST'])
def post_create():
    """
        Creates post
        Returns post metadata, with ID
    """
    from ghostwriter.Post import Post, PostManager
    pm = PostManager()

    post = Post(request.form['title'])
    pm.addPost(post)
    jdata = {   'id': post.ID,
                'title': post.title,
                'creation_date': post.creation_date.isoformat(),
                'summary': post.getSummary()
            }
    return jsonify(jdata), 200


# Admin interface
@app.route('/admin')
def show_admin_panel():
    return 'admin'


mm.create() # Please remove this, for the love of god

