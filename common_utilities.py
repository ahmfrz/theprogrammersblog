import hashlib
import jinja2
import os
import random
from string import letters
import repo
import webapp2
#import bcrypt

# region global variables
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                               autoescape=True)

SECRET = "lwkDwe234sdfnA@fdsd..aw"


class SecurityProvider():

    """This class provides functionality for user security"""

    # region class methods
    @classmethod
    def make_salt(cls, length=15):
        return ''.join(random.choice(letters) for x in xrange(length))

    @classmethod
    def make_secure_cookie(cls, cookie_val):
        calculated_hash = hashlib.sha256(cookie_val + SECRET).hexdigest()
        return '{0}|{1}'.format(cookie_val, calculated_hash)

    @classmethod
    def check_valid_cookie(cls, cookie_hashed):
        cookie_val = cookie_hashed.split('|')[0]
        if cookie_hashed == cls.make_secure_cookie(cookie_val):
            return cookie_val

    @classmethod
    # bcrypt.gensalt(15)):
    def make_secure_password(cls, username, password, salt=None):
        if not salt:
            salt = cls.make_salt(length=5)
        # bcrypt.hashpw(password, salt), salt)
        calculated_hash = hashlib.sha256(
            username + password + salt).hexdigest()
        return "{0}|{1}".format(calculated_hash, salt)

    @classmethod
    def check_secure_password(cls, username, password, password_hashed):
        salt = password_hashed.split("|")[1]
        retrieved_pw = cls.make_secure_password(username, password, salt)
        if password_hashed == retrieved_pw:
            return True


class BaseHandler(webapp2.RequestHandler):

    """This class provides common functionality for all handlers"""

    # region functions
    def write(self, *args, **kwargs):
        self.response.out.write(*args, **kwargs)

    def render_str(self, template_name, **kwargs):
        template = jinja_env.get_template(template_name)
        kwargs['user'] = self.user
        return template.render(kwargs)

    def render(self, template_name, **kwargs):
        return self.write(self.render_str(template_name, **kwargs))

    def initialize(self, *args, **kwargs):
        webapp2.RequestHandler.initialize(self, *args, **kwargs)
        uid = self.read_secure_cookie('user-id')
        self.user = uid and repo.UserEntity.by_id(int(uid))

    def read_secure_cookie(self, cookie_name):
        cookie_val = self.request.cookies.get(cookie_name)
        return cookie_val and SecurityProvider.check_valid_cookie(cookie_val)

    def set_secure_cookie(self, cookie_name, cookie_val=None):
        cookie_hashed = SecurityProvider.make_secure_cookie(cookie_val)
        self.response.out.headers.add_header(
            'Set-Cookie',
            '{0}={1};Path=/'.format(cookie_name, cookie_hashed))

    def create_login_cookie(self, user):
        self.set_secure_cookie('user-id', str(user.key().id()))

    def logout(self):
        self.response.out.headers.add_header(
            'Set-Cookie',
            'user-id=;return-url=/;Path=/')

    def reset_return_url(self):
        self.response.out.headers.add_header(
            'Set-Cookie',
            'return-url=/;Path=/')

    def get_all_posts(self, uid):
        return repo.PostEntity.execute_query(repo.SELECT_ALL_POSTS_BY.format(uid))
