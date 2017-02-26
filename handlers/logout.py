"""Defines LogoutHandler"""

from handlers.base import BaseHandler


class LogoutHandler(BaseHandler):

    """This class handles logout request"""

    # region Handler methods
    def get(self):
        """This method logs the user out and redirects to index page"""
        self.logout()
        self.redirect('/')
