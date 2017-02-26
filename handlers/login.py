"""Defines LoginHandler"""

from models.user import UserEntity
from infrastructure.security import SecurityProvider
from handlers.base import BaseHandler


class LoginHandler(BaseHandler):

    """This class provides content for login page with validation"""

    # region Handler methods
    def get(self):
        """This method gets the login page"""
        if not self.user:
            self.render('login.html')
        else:
            self.redirect('/')

    def post(self):
        """This method posts to the login page"""
        username = self.request.get('username')
        password = self.request.get('password')
        user = LoginHandler.login(username, password)
        if user:
            self.create_login_cookie(user)
            self.redirect('/welcome')
        else:
            self.render('login.html', error="Invalid username or password")

    # region functions
    @classmethod
    def login(cls, name, password):
        """This function checks given username and password and returns the user if it exists

        Args:
            name: The user name
            password: The password

        Returns:
            Success: The user entity
            Failure: None
        """
        user = UserEntity.by_name(name)

        # If user exists, check the password with saved hash
        if user and SecurityProvider.check_secure_password(name, password, user.password):
            return user
