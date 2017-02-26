"""Defines BaseHandler"""

import os
import jinja2
import webapp2
from models.post import PostEntity
from models.user import UserEntity
from infrastructure import gql_queries
from infrastructure.security import SecurityProvider

# region global variables
TEMPLATE_DIR = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), 'templates')
JINJA_ENV = jinja2.Environment(loader=jinja2.FileSystemLoader(TEMPLATE_DIR),
                               autoescape=True)


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
        return PostEntity.execute_query(gql_queries.SELECT_ALL_POSTS_BY.format(uid))

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
        self.user = uid and UserEntity.by_id(int(uid))

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
