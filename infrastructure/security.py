"""Defines Security related functionalities"""

from string import letters
import random
import hashlib

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
