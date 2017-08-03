#  GhostWriter main file 
#  Copyright (C) 2017 Arthur M
#
from flask import Flask, request, jsonify, render_template, flash, redirect, url_for
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from ghostwriter.models.modelmanager import ModelManager

app = Flask("ghostwriter");
app.config.from_envvar('GHOSTWRITER_CONFIG')

mm = ModelManager(app)
mm.setDatabaseURI(app.config['GHOSTWRITER_DATABASE'])
mm.init()

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(session_id):
    from ghostwriter.UserManager import UserManager, get_user_manager
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


def post_array_to_dictionary(posts):
    from ghostwriter.Post import Post
    post_arr = []

    for post in posts:
        post_val = {   
                 'id': post.ID,
                 'title': post.title,
                 'creation_date': post.creation_date.isoformat(),
                 'summary': post.getSummary(),
                 'owner': {
                     'id': post.getOwner().uid,
                     'name': post.getOwner().name
                 }

             }
        post_arr.append(post_val)

    return post_arr


# REST interfaces
@app.route('/api/posts/', methods=['GET'])
def posts_get():
    """
        Gets all posts

        Returns a JSON with their information, without content data
    """
    from ghostwriter.Post import Post, PostManager 
    pm = PostManager()
    posts = pm.getAllPosts()
    if len(posts) <= 0:
        return jsonify({'error': 'No posts found'}), 404
 
    return jsonify(post_array_to_dictionary(posts))

@app.route('/api/post/search', methods=['GET'])
def posts_search(userid = None):
    """
        Search for posts, by date or title
    """
    vsearch = {}
    title = request.args.get('title')
    if not (title is None):
        vsearch['title'] = title

    cdate = request.args.get('cdate')
    if not (cdate is None):
        vsearch['creation_date'] = cdate

    from ghostwriter.Post import Post, PostManager 
    pm = PostManager()
    
    posts = pm.filterPosts(**vsearch)
    if posts is None:
        return jsonify({'error', 'No filter specified'}), 404 # TODO: think of a better error code

    if len(posts) <= 0:
        return jsonify({'error': 'No posts found'}), 404
 
    return jsonify(post_array_to_dictionary(posts))
     

@app.route('/api/post/<int:id>/content', methods=['GET', 'PUT'])
def post_get_content(id):
    """ 
        Retrieves/sets post content
        Returns post data in its native XHTML format, or 404 if post not found

        GET: Retrieve the content
        PUT: Updates content
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



@app.route('/api/post/<int:id>/', methods=['GET', 'DELETE', 'PUT'])
def post_get(id):
    """
        Manage the post
        If post not found, give a 404 Not Found error

        GET: Retrieve post metadata, in JSON format
        PUT: Update any field of post metadata. Return it in JSON format
        DELETE: Delete the post
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
                 'summary': post.getSummary(),
                 'owner': {
                     'id': post.getOwner().uid,
                     'name': post.getOwner().name
                 }
             }
        return jsonify(jdata), 200
    elif request.method == 'DELETE':
        pm.removePost(post)
        return "",200
    elif request.method == 'PUT':
        title = request.form['title']
        post.title = title
        pm.updatePostMetadata(post)
        jdata = {   'id': post.ID,
                 'title': post.title,
                 'creation_date': post.creation_date.isoformat(),
                 'summary': post.getSummary(),
                 'owner': {
                     'id': post.getOwner().uid,
                     'name': post.getOwner().name
                 }

             }
        return jsonify(jdata), 200
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

    post = Post(current_user.uid, request.form['title'])
    pm.addPost(post)
    jdata = {   'id': post.ID,
                'title': post.title,
                'creation_date': post.creation_date.isoformat(),
                'summary': post.getSummary(),
                 'owner': {
                     'id': post.getOwner().uid,
                     'name': post.getOwner().name
                 }

            }
    return jsonify(jdata), 200


@app.route('/api/users/', methods=['GET', 'POST'])
@login_required
def user_list_manage():
    """
        Manages users

        GET: Gets all users
        POST: Creates an user
            username: login name
            password: the password
            name: the user true name. Optional

        Return an 200 OK if all OK
    """
    from ghostwriter.User import User
    from ghostwriter.UserManager import UserManager
    um = UserManager()

    if request.method == 'GET':
        userlist = um.getAllUsers()
        if len(userlist) <= 0:
            return jsonify({'error': 'No users'}), 404

        juser = []

        for user in userlist:
            jdata = {'id': user.uid,
                     'username': user.username,
                     'name': user.name}
            juser.append(jdata)

        return jsonify(juser), 200


    elif request.method == 'POST':
        login = request.form['username']
        password = request.form['password']

        try:
            name = request.form['name']
        except KeyError:
            name = login

        user = User(login, name) 
        um.addUser(user, password)
        jdata = {'id': user.uid,
                 'username': user.username,
                 'name': user.name}
        return jsonify(jdata),200
    else:
        return "",405

@app.route('/api/user/<int:userid>/', methods=['GET','DELETE', 'PUT'])
@login_required
def user_manage(userid):
    """
        Manages an individual user

        GET: Gets information from user with id 'userid'
        DELETE: Delete said user
        PUT: Update user information, unless password

        Returns 404 Not Found if user not found, or 403 Forbidden
        if trying to delete a user you are logged in
    """
    from ghostwriter.User import User
    from ghostwriter.UserManager import UserManager
    um = UserManager()
    u = um.getUserbyID(userid)
    if u is None:
        return jsonify({'error': 'User not found'}), 404

    if request.method == 'GET':
        jdata = {'id': u.uid,
                 'username': u.username,
                 'name': u.name}
        return jsonify(jdata), 200
    elif request.method == "PUT":
        u.username = request.form['username']
        u.name = request.form['name']
        um.updateUser(u)
        jdata = {'id': u.uid,
                 'username': u.username,
                 'name': u.name}
        return jsonify(jdata), 200

    elif request.method == 'DELETE':
        if current_user.uid == u.uid:
            return jsonify({'error': 
                'Cannot delete user you are logged in'}), 403

        um.removeUser(u)
        return "",200
    else:
        return "",405

@app.route('/api/user/<int:userid>/posts', methods=['GET'])
def posts_author_search(userid):
    """
        Search for posts, by author
    """
    from ghostwriter.Post import Post, PostManager 
    pm = PostManager()
    
    posts = pm.filterPosts(author_id = userid)
    
    if len(posts) <= 0:
        return jsonify({'error': 'No posts found'}), 404
 
    return jsonify(post_array_to_dictionary(posts))
    
@app.route('/api/user/<int:userid>/posts/search', methods=['GET'])
def posts_author_search_filter(userid):
    """
        Search for posts, by author
    """
    vsearch = {}
    title = request.args.get('title')
    if not (title is None):
        vsearch['title'] = title

    cdate = request.args.get('cdate')
    if not (cdate is None):
        vsearch['creation_date'] = cdate

    vsearch['author_id'] = userid

    from ghostwriter.Post import Post, PostManager 
    pm = PostManager()
    
    posts = pm.filterPosts(**vsearch)
    
    if len(posts) <= 0:
        return jsonify({'error': 'No posts found'}), 404
 
    return jsonify(post_array_to_dictionary(posts))


# Admin interface
@app.route('/admin')
def show_admin_panel():
    return render_template('admin.html')

@app.route('/admin/login', methods=['POST'])
def do_login():
    username = request.form['username']
    password = request.form['password']

    from ghostwriter.User import User
    from ghostwriter.UserManager import UserManager, get_user_manager
    um = get_user_manager()
    u = um.getUserbyUsername(username)

    if u is None:
        flash('User does not exist')
        return render_template('admin.html'), 401

    if not u.login(password, um):
        flash('Invalid user or password')
        return render_template('admin.html'), 401

    login_user(u)
    return redirect(url_for('show_main_admin'))

@app.route('/admin/panel', methods=['GET'])
@login_required
def show_main_admin():
    return render_template('main.html', navlink='dashboard')

@app.route('/admin/users', methods=['GET'])
@login_required
def show_users():
    return render_template('users.html', navlink='users')

@app.route('/admin/users/create', methods=['GET'])
@login_required
def admin_create_user():
    return render_template('manage_user.html', navlink='users', action='create')

@app.route('/admin/users/edit/<int:id>/', methods=['GET'])
@login_required
def admin_edit_user(id):
    return render_template('manage_user.html', navlink='users', action='edit',
            userid=id)

@app.route('/admin/posts', methods=['GET'])
@login_required
def show_posts():
    return render_template('posts.html', navlink='posts')

@app.route('/admin/posts/create', methods=['GET'])
@login_required
def admin_create_post():
    return render_template('manage_post.html', navlink='posts', action='create')
    
@app.route('/admin/posts/edit/<int:id>/', methods=['GET'])
@login_required
def edit_post(id):
    return render_template('manage_post.html', navlink='posts',
            action='edit', postid=id)



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
        from ghostwriter.User import User
        from ghostwriter.UserManager import UserManager
        um = UserManager()
        um.addUser(User('admin', 'Administrator'), 'admin')

        app.logger.info('Database created')
    except Exception as e:
        app.logger.error('Error while creating database: {}'.format(e))

app.secret_key = 'B1Ad99013yX R~XHHHHHHHHHH/,?RT'
