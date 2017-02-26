from post import PostEntity
from google.appengine.ext import db

def comment_key(group='default'):
    """This function returns db key for comments"""
    return db.Key.from_path('comments', group)

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
