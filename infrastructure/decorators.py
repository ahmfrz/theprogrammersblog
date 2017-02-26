"""Defines decorators"""

from models.post import PostEntity
from models.comment import CommentEntity

# region decorators


def post_exists(function):
    """Decorator to check if post exists"""
    def wrapper(self, pid, *args):
        """Wrapper for the function"""
        post = PostEntity.by_id(int(pid))
        if post:
            return function(self, post, *args)
        else:
            return self.error(404)
    return wrapper


def comment_exists(function):
    """Decorator to check if comment exists"""
    def wrapper(self, pid, cid):
        """Wrapper for the function"""
        post = PostEntity.by_id(int(pid))
        comment = CommentEntity.by_id(int(cid))
        if post and comment:
            return function(self, comment, pid)
        else:
            return self.error(404)
    return wrapper


def user_owns_post(function):
    """Decorator to check if user owns post"""
    def wrapper(self, post):
        """Wrapper for the function"""
        if post.user.key().id() == self.user.key().id():
            return function(self, post)
        else:
            return self.error(404)
    return wrapper


def user_owns_comment(function):
    """Decorator to check if user owns comment"""
    def wrapper(self, comment_object, pid):
        """Wrapper for the function"""
        if comment_object.user.key().id() == self.user.key().id():
            return function(self, comment_object, pid)
        else:
            return self.error(404)
    return wrapper
