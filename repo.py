"""This module defines all datastore related operations for multiuser blog"""

from google.appengine.ext import db

__author__ = "Ahmed Faraz Ansari"
__copyright__ = "Copyright 2017 (c) ahmfrz"

__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Ahmed Faraz Ansari"
__email__ = "af.ahmfrz@gmail.com"
__status__ = "Production"

# region global functions


def users_key(group='default'):
    """This function returns db key for users"""
    return db.Key.from_path('users', group)


def post_key(group='default'):
    """This function returns db key for posts"""
    return db.Key.from_path('posts', group)


def comment_key(group='default'):
    """This function returns db key for comments"""
    return db.Key.from_path('comments', group)


# region Queries
SELECT_ALL_POSTS = "SELECT * FROM PostEntity ORDER BY created_date DESC"
SELECT_ALL_POSTS_BY = "SELECT * FROM PostEntity WHERE created_by = {0} ORDER BY created_date DESC"

# region Entities


class UserEntity(db.Model):

    """ This class provides functionality for storage and
    retrieval of user data"""

    # region columns
    username = db.StringProperty(required=True)
    password = db.StringProperty(required=True)
    email = db.StringProperty()
    about = db.TextProperty()
    liked_posts = db.StringProperty()

    # region class functions
    @classmethod
    def by_name(cls, name):
        """This function gets the user with the given username

        Args:
            name: The username

        Returns:
            UserEntity with given username
        """
        return cls.all().filter('username = ', name).get()

    @classmethod
    def by_id(cls, uid):
        """This function gets user with the given userid

        Args:
            uid: The user id

        Returns:
            UserEntity with given userid
        """
        return cls.get_by_id(uid, parent=users_key())

    @classmethod
    def register(cls, name, password, email=None):
        """This function registers user with given values

        Args:
            name: The username
            password: The password
            email: The email

        Returns:
            New UserEntity instance
        """
        return cls(parent=users_key(),
                   username=name,
                   password=password,
                   email=email)

    @classmethod
    def commit_user(cls, user):
        """This function commits the passed user to the datastore

        Args:
            user: The UserEntity to commit
        """
        user.put()

    # region class methods
    def check_likes(self, pid):
        """This function checks likes for a given post

        Args:
            pid: The post id

        Returns:
            Success: True
            Failure: None
        """
        return self.all().filter('liked_posts = ', pid).get()


class PostEntity(db.Model):

    """ This class provides functionality for storage and
    retrieval of post data"""

    # region columns
    title = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    author = db.StringProperty(required=True)
    created_by = db.IntegerProperty(required=True, indexed=True)
    created_date = db.DateTimeProperty(auto_now_add=True, indexed=True)
    modified_date = db.DateTimeProperty(auto_now=True)
    likes = db.IntegerProperty()

    # region class methods
    @classmethod
    def by_id(cls, pid):
        """This function returns post with given post id

        Args:
            pid: The post id

        Returns:
            PostEntity with given post id
        """
        return cls.get_by_id(pid, parent=post_key())

    @classmethod
    def create_post(cls, title, content, author, created_by):
        """This function creates post with given values

        Args:
            title: The post title
            content: The post content
            author: The post author
            created_by: The user id of the author

        Returns:
            New PostEntity instance
        """
        return cls(parent=post_key(),
                   title=title,
                   content=content,
                   author=author,
                   created_by=created_by,
                   likes=0)

    @classmethod
    def execute_query(cls, query):
        """This function executes the given query

        Args:
            query: The formatted query string

        Returns:
            The query result
        """
        return db.GqlQuery(query).fetch(1000)

    @classmethod
    def commit_post(cls, post):
        """This function commits the given post to the datastore

        Args:
            post: The post
        """
        post.put()

    # region functions
    def get_all_comments(self):
        """This function gets the first 5000 comments for a given post

        Returns:
            First 500 comments for the given PostEntity
        """
        return self.post_comments.order('-created_date').fetch(500)


class CommentEntity(db.Model):

    """ This class provides functionality for storage and
    retrieval of comments"""

    # region columns
    comment_by = db.StringProperty()
    comment_by_id = db.IntegerProperty()
    created_date = db.DateTimeProperty(auto_now_add=True)
    comment = db.TextProperty(required=True)
    post = db.ReferenceProperty(PostEntity, collection_name='post_comments')

    # region class functions
    @classmethod
    def register(cls, post, comment_by, comment_by_id, comment):
        """This function register a comment with given values

        Args:
            post: The PostEntity on which the comment is made
            comment_by: The user name of the comment author
            comment_by_id: The user id of the comment author
            comment: The comment content

        Returns:
            New CommentEntity instance
        """
        return cls(parent=comment_key(),
                   post=post,
                   comment_by=comment_by,
                   comment_by_id=comment_by_id,
                   comment=comment)

    @classmethod
    def by_id(cls, cid):
        """This function gets comment with given comment id

        Args:
            cid: The comment id

        Returns:
            CommentEntity with given comment id
        """
        return cls.get_by_id(cid, parent=comment_key())

    @ classmethod
    def commit_comment(cls, comment):
        """This function commits the given comment to the datastore

        Args:
            comment: The CommentEntity instance
        """
        comment.put()
