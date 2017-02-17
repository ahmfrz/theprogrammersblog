"""This module defines common functionalities for other modules"""

import hashlib
import os
from string import letters
import random
import webapp2
import jinja2
import repo
#import bcrypt

__author__ = "Ahmed Faraz Ansari"
__copyright__ = "Copyright 2017 (c) ahmfrz"

__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Ahmed Faraz Ansari"
__email__ = "af.ahmfrz@gmail.com"
__status__ = "Production"

# region global variables
TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'templates')
JINJA_ENV = jinja2.Environment(loader=jinja2.FileSystemLoader(TEMPLATE_DIR),
                               autoescape=True)

SECRET = "lwkDwe234sdfnA@fdsd..aw"


class SecurityProvider(object):

    """This class provides functionality for user security"""

    # region functions
    @classmethod
    def make_salt(cls, length=15):
        """This function creates a random salt of the specified length

        Args:
            length: The length of the salt

        Returns:
            Random salt of the given length
        """
        return ''.join(random.choice(letters) for x in xrange(length))

    @classmethod
    def make_secure_cookie(cls, cookie_val):
        """This function creates a secure cookie value

        Args:
            cookie_val: The cookie value

        Returns:
            The original cookie value and hash separated by pipe(|)
        """
        calculated_hash = hashlib.sha256(cookie_val + SECRET).hexdigest()
        return '{0}|{1}'.format(cookie_val, calculated_hash)

    @classmethod
    def check_valid_cookie(cls, cookie_hashed):
        """This function validates the given cookie value

        Args:
            cookie_hashed: The hashed cookie

        Returns:
            Success: The cookie value
            Failure: None
        """
        cookie_val = cookie_hashed.split('|')[0]
        if cookie_hashed == cls.make_secure_cookie(cookie_val):
            return cookie_val

    @classmethod
    # bcrypt.gensalt(15)):
    def make_secure_password(cls, username, password, salt=None):
        """This function creates hashed password

        Args:
            username: The username
            password: The password
            salt: Salt for hashing

        Returns:
            The calculated hash and salt separated by pipe(|)
        """
        if not salt:
            salt = cls.make_salt(length=5)
        # bcrypt.hashpw(password, salt), salt)
        calculated_hash = hashlib.sha256(
            username + password + salt).hexdigest()
        return "{0}|{1}".format(calculated_hash, salt)

    @classmethod
    def check_secure_password(cls, username, password, password_hashed):
        """This function validates given password against hashed password

        Args:
            username: The entered username
            password: The entered password
            password_hashed: The stored password from datastore

        Returns:
            Success: True
            Failure: None
        """
        salt = password_hashed.split("|")[1]
        retrieved_pw = cls.make_secure_password(username, password, salt)
        if password_hashed == retrieved_pw:
            return True


class BaseHandler(webapp2.RequestHandler):

    """This class provides common functionality for all handlers"""

    # region functions
    @classmethod
    def get_all_posts(cls, uid):
        """This function gets all posts by the given user id

        Args:
            uid: The user id

        Returns:
            List of posts by the given user
        """
        return repo.PostEntity.execute_query(repo.SELECT_ALL_POSTS_BY.format(uid))

    # region methods
    def write(self, *args, **kwargs):
        """This method abstracts writing to webapp2 response

        Args:
            *args: The args
            **kwargs: The keyworded args
        """
        self.response.out.write(*args, **kwargs)

    def render_str(self, template_name, **kwargs):
        """This method gets and calls render on jinja template with given name

        Args:
            template_name: The name of the jinja template to render
            **kwargs: The keyworded args to pass to the template

        Returns:
            The template string for rendering
        """
        template = JINJA_ENV.get_template(template_name)
        kwargs['user'] = self.user
        return template.render(kwargs)

    def render(self, template_name, **kwargs):
        """This method abstracts jinja2 template rendering

        Args:
            template_name: The template name
            **kwargs: The keyworded args to pass to jinja template

        Returns:
            Response
        """
        return self.write(self.render_str(template_name, **kwargs))

    def initialize(self, *args, **kwargs):
        """This method overrides RequestHandler initialize method to read cookie value

        Args:
            *args: The args
            **kwargs: The keyworded args
        """
        webapp2.RequestHandler.initialize(self, *args, **kwargs)
        uid = self.read_secure_cookie('user-id')
        self.user = uid and repo.UserEntity.by_id(int(uid))

    def read_secure_cookie(self, cookie_name):
        """This method reads cookie value from the request

        Args:
            cookie_name: The name of the cookie to read

        Returns:
            Success: The cookie value
            Failure: None
        """
        cookie_val = self.request.cookies.get(cookie_name)
        return cookie_val and SecurityProvider.check_valid_cookie(cookie_val)

    def set_secure_cookie(self, cookie_name, cookie_val=None):
        """This method sets hashed cookie value in response header

        Args:
            cookie_name: The name of the cookie
            cookie_val: The value of the cookie
        """
        cookie_hashed = SecurityProvider.make_secure_cookie(cookie_val)
        self.response.out.headers.add_header(
            'Set-Cookie',
            '{0}={1};Path=/'.format(cookie_name, cookie_hashed))

    def create_login_cookie(self, user):
        """This method creates user cookie

        Args:
            user: The UserEntity object
        """
        self.set_secure_cookie('user-id', str(user.key().id()))

    def logout(self):
        """This method clears user cookie"""
        self.response.out.headers.add_header(
            'Set-Cookie',
            'user-id=;return-url=/;Path=/')
