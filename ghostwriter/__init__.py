#  GhostWriter main file 
#  Copyright (C) 2017 Arthur M
#


from flask import Flask, request;

app = Flask("ghostwriter");

# Test route
@app.route('/')
def test_run():
    return 'Ghostwriter 0.0.1 installed successfully<br/> ' + 
        'Please disable this route in the setup (not existent yet)'


# REST interfaces
@app.route('/api/post/<int:id>/content', methods=['GET', 'PUT']):
def post_get(id):
    if request.method == 'GET':
        return 'Got post content for {}'.format(id)

    if request.method == 'PUT':
        return 'Put post content for {}'.format(id)

@app.route('/api/post/<int:id>/', methods=['GET']):
def post_get(id):
    return 'Got post {}'.format(id)

@app.route('/api/post/create/', methods=['POST']):
    return 'Post created'


# Admin interface
@app.route('/admin')
def show_admin_panel():
    return 'admin'
