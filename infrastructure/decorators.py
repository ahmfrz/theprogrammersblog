import logging
from models.post import PostEntity
from models.comment import CommentEntity

# region decorators
def post_exists(function):
    def wrapper(self, pid, *args):
        post = PostEntity.by_id(int(pid))
        if post:
            return function(self, post, *args)
        else:
            return self.error(404)
    return wrapper

def comment_exists(function):
    def wrapper(self, pid, cid):
        post = PostEntity.by_id(int(pid))
        comment = CommentEntity.by_id(int(cid))
        if post and comment:
            return function(self, comment, pid)
        else:
            return self.error(404)
    return wrapper

def user_owns_post(function):
    def wrapper(self, post):
        if post.user.key().id() == self.user.key().id():
            return function(self, post)
        else:
            return self.error(404)
    return wrapper

def user_owns_comment(function):
    def wrapper(self, comment_object, pid):
        if comment_object.user.key().id() == self.user.key().id():
            return function(self, comment_object, pid)
        else:
            return self.error(404)
    return wrapper