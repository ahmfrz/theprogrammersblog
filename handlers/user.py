"""Defines UserInfoHandler"""

from models.user import UserEntity
from handlers.base import BaseHandler


class UserInfoHandler(BaseHandler):

    """This class handles user information"""

    def welcome(self):
        """This method gets the welcome page"""
        if self.user:
            return self.render('welcome.html')
        self.redirect('/register')

    def add_about(self, uid):
        """This method adds about info for the logged in user

        Args:
            uid: The user id
        """
        if self.user and uid == str(self.user.key().id()):
            about = self.request.get('about')
            if about:
                self.user.about = about
                UserEntity.commit_user(self.user)

        self.redirect('/')

    def about_user(self, *args):
        """This method gets the about page for a given user

        Args:
            args[0]: The username(unused, added for more readability of route)
            args[1]: The user id
        """
        user_for_about = len(args) == 2 and UserEntity.by_id(int(args[1]))
        if user_for_about:
            user_posts = UserInfoHandler.get_all_posts(
                user_for_about.key().id())
            if not user_posts:
                user_posts = []
            return self.render(
                'user_info.html', userA=user_for_about, user_posts=user_posts)

        self.redirect("/")
