"""Defines AboutHandler"""

from handlers.base import BaseHandler


class AboutHandler(BaseHandler):

    """This class serves responsive webpage"""

    def get(self):
        """This method gets the about page"""
        self.render('about.html')
