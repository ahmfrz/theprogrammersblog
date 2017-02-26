#!/usr/bin/env python

"""This module creates a webapp2 application and defines all routes with their
handlers"""

import webapp2
import handlers

__author__ = "Ahmed Faraz Ansari"
__copyright__ = "Copyright 2017 (c) ahmfrz"

__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Ahmed Faraz Ansari"
__email__ = "af.ahmfrz@gmail.com"
__status__ = "Production"

BLOG = webapp2.WSGIApplication([
    ('/', handlers.index.IndexHandler),
    ('/register', 'handlers.register.RegisterHandler'),
    ('/login', 'handlers.login.LoginHandler'),
    ('/logout', 'handlers.logout.LogoutHandler'),
    ('/newpost', 'handlers.newpost.NewPostHandler'),
    ('/post/([0-9]+)', 'handlers.post.PostHandler'),
    ('/about', 'handlers.about.AboutHandler'),
    webapp2.Route(
        r'/<:[0-9]+>',
        'handlers.index.IndexHandler'),
    webapp2.Route(
        r'/welcome',
        'handlers.user.UserInfoHandler:welcome'),
    webapp2.Route(
        r'/editpost/<:[0-9]+>',
        'handlers.post.PostHandler:edit_post'),
    webapp2.Route(
        r'/deletepost/<:[0-9]+>',
        'handlers.post.PostHandler:delete_post'),
    webapp2.Route(
        r'/likepost/<:[0-9]+>',
        'handlers.post.PostHandler:like_post'),
    webapp2.Route(
        r'/unlikepost/<:[0-9]+>',
        'handlers.post.PostHandler:unlike_post'),
    webapp2.Route(
        r'/post/addComment/<:[0-9]+>',
        'handlers.post.PostHandler:add_comment'),
    webapp2.Route(
        r'/editComment/<:[0-9]+>/<:[0-9]+>',
        'handlers.post.PostHandler:edit_comment'),
    webapp2.Route(
        r'/deleteComment/<:[0-9]+>/<:[0-9]+>',
        'handlers.post.PostHandler:delete_comment'),
    webapp2.Route(
        r'/addAbout/<:[0-9]+>',
        'handlers.user.UserInfoHandler:add_about'),
    webapp2.Route(
        r'/<:[a-zA-Z0-9]+>/<:[0-9]+>',
        'handlers.user.UserInfoHandler:about_user')
], debug=False)
