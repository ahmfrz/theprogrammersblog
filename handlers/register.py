import re
from models.user import UserEntity
from infrastructure.security import SecurityProvider
from base import BaseHandler

class RegisterHandler(BaseHandler):

    """This class provides content for registeration page with validation"""

    # region regex
    USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
    PASS_RE = re.compile(r"^.{3,20}$")
    EMAIL_RE = re.compile(r'^[\S]+@[\S]+\.[\S]+$')

    # region functions
    @classmethod
    def valid_username(cls, username):
        """This method validates given username with regex

        Args:
            username: The username to match

        Returns:
            Success: True
            Failure: None
        """
        return username and RegisterHandler.USER_RE.match(username)

    @classmethod
    def valid_password(cls, password):
        """This method validates given password with regex

        Args:
            password: The password to match

        Returns:
            Success: True
            Failure: None
        """
        return password and RegisterHandler.PASS_RE.match(password)

    @classmethod
    def valid_email(cls, email):
        """This method validates given email with regex

         Args:
            email: The email to match

        Returns:
            Success: True
            Failure: None
        """
        return not email or RegisterHandler.EMAIL_RE.match(email)

    # region Handler methods
    def get(self):
        """This method gets the register page"""
        if not self.user:
            self.render('register.html')
        else:
            self.redirect('/')

    def post(self):
        """This method posts to the register page"""
        username = self.request.get('username')
        password = self.request.get('password')
        verify = self.request.get('verify')
        email = self.request.get('email')

        params = dict(username=username,
                      email=email)
        have_error = False

        if not RegisterHandler.valid_username(username):
            params['error_username'] = "That's not a valid username."
            have_error = True

        if not RegisterHandler.valid_password(password):
            params['error_password'] = "That wasn't a valid password."
            have_error = True
        elif password != verify:
            params['error_verify'] = "Your passwords didn't match."
            have_error = True

        if not RegisterHandler.valid_email(email):
            params['error_email'] = "That's not a valid email."
            have_error = True

        # In case of error re-render the register page
        if have_error:
            self.render('register.html', **params)
        else:
            if UserEntity.by_name(username):
                self.render(
                    'register.html', error_username="User already exists")
            else:
                # Create hash for password for security
                hashed_password = SecurityProvider.make_secure_password(
                    username, password)
                new_user = UserEntity.register(
                    username, hashed_password, email)
                UserEntity.commit_user(new_user)
                self.create_login_cookie(new_user)
                self.redirect('/welcome')