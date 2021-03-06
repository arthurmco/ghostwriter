# Ghostwriter

[![travis-badge](https://api.travis-ci.org/arthurmco/ghostwriter.svg?branch=master)](https://travis-ci.org/arthurmco/ghostwriter)
[![Coverage Status](https://coveralls.io/repos/github/arthurmco/ghostwriter/badge.svg?branch=master)](https://coveralls.io/github/arthurmco/ghostwriter?branch=master)

Ghostwriter is a software for those that want a platform for article/blog 
editing and management, but don't want a predefined way to display it, 
with limited choice for themes (that never fit with your site), complicated
APIs and a difficult configuration

This software gives *you* the control of how the posts are shown, offering
a simple REST API for creating and showing them, along with a simple interface 
for managing them. We don't offer a way to show them, we let you do it at
your way.

**THIS SOFTWARE IS UNDER DEVELOPMENT**

However, contributions are welcome :smile:

This software is licensed under the MIT License

## Installing

 - Clone this repository
 - Create a virtualenv and enter it
 - Run `pip install -e . `
 - Set the `GHOSTWRITER_CONFIG` environment variable to a configuration file. See 'Configuration' for more details
 - Run `FLASK_APP=ghostwriter flask initdb`. This will create the database and 
   the needed tables

## Running

To test, simply run flask with the `FLASK_APP` environment variable as `ghostwriter`. 

You may want to run ghostwriter in a WSGI environment. Although isn't supported yet, I'd love some testing.

The '/' route contains a test message. In the future, that message will be removable

The default login is 'admin' with password 'admin'. 

The login page is in the '/admin' entry point (usually `localhost:5000/admin` )

## Configuration

You can configure Ghostwriter options through a configuration file. 

A sample named ghostwriter.cfg is located in the project folder, but it's name is controlled by the envvar `GHOSTWRITER_CONFIG`, and it's relative to the ghostwriter folder in this package. Recognized options are:

 - `GHOSTWRITER_DATABASE`: The database connection string
