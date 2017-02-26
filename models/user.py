from google.appengine.ext import db

def users_key(group='default'):
    """This function returns db key for users"""
    return db.Key.from_path('users', group)

class UserEntity(db.Model):

    """ This class provides functionality for storage and
    retrieval of user data"""

    # region columns
    username = db.StringProperty(required=True)
    password = db.StringProperty(required=True)
    email = db.StringProperty()
    about = db.TextProperty()
    liked_posts = db.ListProperty(int)

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
            Failure: False
        """
        return pid in self.liked_posts
