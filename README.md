# Ghostwriter

Ghostwriter is a software for those that want a platform for article/blog 
editing and management, but don't want a predefined way to display it, 
with limited choice for themes, complicated APIs and a difficult configuration

This software gives *you* the control of how the posts are shown, offering
a simple REST API for creating and showing them, along a simple interface 
for managing them. We don't offer a way to show them, we let you do it at
your way.

**THIS SOFTWARE IS UNDER DEVELOPMENT**

This software is licensed under the MIT License

## Installing

 - Clone this repository
 - Create a virtualenv and enter it
 - Run `pip install -e . `
 - Run `FLASK_APP=ghostwriter flask initdb`. This will create the database and 
   the needed tables

## Running

To test, simply run flask with the `FLASK_APP` environment variable as `ghostwriter`. 

You may want to run ghostwriter in a WSGI environment. Although isn't supported yet, I'd love some testing.

The '/' route contains a test message. In the future, that message will be removable
