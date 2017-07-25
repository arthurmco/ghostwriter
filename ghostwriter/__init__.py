#  GhostWriter main file 
#  Copyright (C) 2017 Arthur M
#
from flask import Flask, request, jsonify, render_template, flash, redirect, url_for
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from ghostwriter.models.modelmanager import ModelManager

app = Flask("ghostwriter");

mm = ModelManager(app)
mm.setDatabaseURI('sqlite:////tmp/test.db')
mm.init()

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(session_id):
    from ghostwriter.User import UserManager, get_user_manager
    um = get_user_manager()
  
    session_parts = str(session_id).split('|')

    us = um.getLoggedUsersbyToken(session_parts[1])
    if not us:
        return None

    for u in us:
        if u.uid == int(session_parts[0]):
            return u


    return None

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
        if not current_user.is_authenticated:
            return login_manager.unauthorized()

        post.setContent(request.form['content'])
        pm.updatePostContent(post)
        return '',200

@app.route('/api/post/<int:id>/', methods=['GET', 'DELETE'])
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

    if request.method == 'GET':
        jdata = {   'id': post.ID,
                 'title': post.title,
                 'creation_date': post.creation_date.isoformat(),
                 'summary': post.getSummary()
             }
        return jsonify(jdata), 200
    elif request.method == 'DELETE':
        pm.removePost(post)
        return "",200
    else:
        return "",405

@app.route('/api/post/create/', methods=['POST'])
@login_required
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

@app.route('/admin/login', methods=['POST'])
def do_login():
    username = request.form['username']
    password = request.form['password']
    print(username)
    print(password)

    from ghostwriter.User import User, UserManager
    um = UserManager()
    u = um.getUserbyUsername(username)
    print(u)

    if u is None:
        flash('User does not exist')
        return render_template('admin.html'), 401

    if not u.login(password):
        flash('Invalid user or password')
        return render_template('admin.html'), 401

    login_user(u)
    return redirect(url_for('show_main_admin'))

@app.route('/admin/panel', methods=['GET'])
def show_main_admin():
    return render_template('main.html')
    

@app.route('/admin/logoff', methods=['GET'])
@login_required
def do_logout():
    logout_user()
    return redirect(url_for('show_admin_panel'))

# Commands

@app.cli.command()
def initdb():
    """ Initialise the database """
    app.logger.info('Creating database')
    try:
        mm.create()
        from ghostwriter.User import User, UserManager
        um = UserManager()
        um.addUser(User('admin', 'Administrator'), 'admin')

        app.logger.info('Database created')
    except Exception as e:
        app.logger.error('Error while creating database: {}'.format(e))

app.secret_key = 'B1Ad99013yX R~XHHHHHHHHHH/,?RT'
