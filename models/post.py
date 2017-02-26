from google.appengine.ext import db
from user import UserEntity

def post_key(group='default'):
    """This function returns db key for posts"""
    return db.Key.from_path('posts', group)

class PostEntity(db.Model):

    """ This class provides functionality for storage and
    retrieval of post data"""

    # region columns
    title = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    user = db.ReferenceProperty(UserEntity, collection_name = 'posts')
    created_date = db.DateTimeProperty(auto_now_add=True, indexed=True)
    modified_date = db.DateTimeProperty(auto_now=True)

    #region properties
    @property
    def likes(self):
        return UserEntity.gql("WHERE liked_posts = :1", self.key().id()).count()

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
    def create_post(cls, title, content, user):
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
                   user = user)

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
