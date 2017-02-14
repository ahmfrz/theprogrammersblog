import webapp2
import page_handlers

app = webapp2.WSGIApplication([
    ('/', page_handlers.IndexHandler),
    ('/register', 'page_handlers.RegisterHandler'),
    ('/login', 'page_handlers.LoginHandler'),
    ('/logout', 'page_handlers.LogoutHandler'),
    ('/newpost', 'page_handlers.NewPostHandler'),
    ('/post/([0-9]+)', 'page_handlers.PostHandler'),
    ('/about', 'page_handlers.AboutHandler'),
    webapp2.Route(
        r'/welcome',
        'page_handlers.UserInfoHandler:welcome'),
    webapp2.Route(
        r'/editpost/<:[0-9]+>',
        'page_handlers.PostHandler:edit_post'),
    webapp2.Route(
        r'/deletepost/<:[0-9]+>',
        'page_handlers.PostHandler:delete_post'),
    webapp2.Route(
        r'/likepost/<:[0-9]+>',
        'page_handlers.PostHandler:like_post'),
    webapp2.Route(
        r'/unlikepost/<:[0-9]+>',
        'page_handlers.PostHandler:unlike_post'),
    webapp2.Route(
        r'/post/addComment/<:[0-9]+>',
        'page_handlers.PostHandler:add_comment'),
    webapp2.Route(
        r'/editComment/<:[0-9]+>/<:[0-9]+>',
        'page_handlers.PostHandler:edit_comment'),
    webapp2.Route(
        r'/deleteComment/<:[0-9]+>/<:[0-9]+>',
        'page_handlers.PostHandler:delete_comment'),
    webapp2.Route(
        r'/addAbout/<:[0-9]+>',
        'page_handlers.UserInfoHandler:add_about'),
    webapp2.Route(
        r'/<:[a-zA-Z0-9]+>/<:[0-9]+>',
        'page_handlers.UserInfoHandler:about_user')
],
    debug=False)
