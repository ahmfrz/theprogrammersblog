from google.appengine.ext import db

# region global functions


def users_key(group='default'):
    return db.Key.from_path('users', group)


def post_key(group='default'):
    return db.Key.from_path('posts', group)


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

    # region class methods
    @classmethod
    def by_name(cls, name):
        return cls.all().filter('username = ', name).get()

    @classmethod
    def by_id(cls, uid):
        return cls.get_by_id(uid, parent=users_key())

    @classmethod
    def register(cls, name, pw, email=None):
        return cls(parent=users_key(),
                   username=name,
                   password=pw,
                   email=email)

    @classmethod
    def commit_user(cls, user):
        user.put()

    # region functions
    def check_likes(self, pid):
        if self.all().filter('liked_posts = ', pid).get():
            return True
        else:
            return False


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
        return cls.get_by_id(pid, parent=post_key())

    @classmethod
    def create_post(cls, title, content, author, created_by):
        return cls(parent=post_key(),
                   title=title,
                   content=content,
                   author=author,
                   created_by=created_by,
                   likes=0)

    @classmethod
    def execute_query(cls, query):
        return db.GqlQuery(query).fetch(1000)

    @classmethod
    def commit_post(cls, post):
        post.put()

    # region functions
    def get_all_comments(self):
        return self.post_comments.order('-created_date')


class CommentEntity(db.Model):

    """ This class provides functionality for storage and
    retrieval of comments"""

    # region columns
    comment_by = db.StringProperty()
    comment_by_id = db.StringProperty()
    created_date = db.DateTimeProperty(auto_now_add=True)
    comment = db.TextProperty(required=True)
    post = db.ReferenceProperty(PostEntity, collection_name='post_comments')

    # region class methods
    @classmethod
    def register(cls, post, comment_by, comment_by_id, comment):
        return cls(post=post,
                   comment_by=comment_by,
                   comment_by_id=comment_by_id,
                   comment=comment)

    @ classmethod
    def commit_comment(cls, comment):
        comment.put()
