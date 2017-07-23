#  GhostWriter main file 
#  Copyright (C) 2017 Arthur M
#
from flask import Flask, request, jsonify, render_template
from flask_login import LoginManager, login_user, logout_user, current_user
from ghostwriter.models.model_manager import ModelManager

app = Flask("ghostwriter");

mm = ModelManager(app)
mm.setDatabaseURI('sqlite:////tmp/test.db')
mm.init()

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(session_id):
    um = get_user_manager()
    return um.getLoggedUserbyToken(session_id)

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
    return render_template('admin.html')

@app.route('/admin/login/', methods=['POST'])
def do_login():
    pass
# Commands

@app.cli.command()
def initdb():
    """ Initialise the database """
    app.logger.info('Creating database')
    try:
        mm.create()
        app.logger.info('Database created')
    except Exception as e:
        app.logger.error('Error while creating database: {}'.format(e))


