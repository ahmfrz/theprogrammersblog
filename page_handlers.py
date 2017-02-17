"""This module defines page handlers for multiuser blog"""

import re
import common_utilities
from common_utilities import SecurityProvider
import repo

__author__ = "Ahmed Faraz Ansari"
__copyright__ = "Copyright 2017 (c) ahmfrz"

__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Ahmed Faraz Ansari"
__email__ = "af.ahmfrz@gmail.com"
__status__ = "Production"

# region Page handlers


class IndexHandler(common_utilities.BaseHandler):

    """This class provides content for index page"""

    # class members
    # How many posts per page
    per_page = 5

    # region Handler methods
    def get(self, *args):
        """This method gets the index page

        args:
            The post id in case there is any error
        """
        # Get all posts
        all_posts = repo.PostEntity.execute_query(repo.SELECT_ALL_POSTS)

        # Get all posts by logged in user
        user_posts = self.user and all_posts and IndexHandler.get_all_posts(
            self.user.key().id())
        if not user_posts:
            user_posts = []

        # Make pages
        if all_posts:
            result = self.make_pages(all_posts)
        else:
            # If there are no posts, render with min values
            result = [[], 0, 1]

        pid = 0
        error = ""
        if len(args) == 1:
            pid = args[0]
            error = "You can only Like/Unlike once"

        self.render('index.html',
                    posts=result[0],
                    posts_len=result[1],
                    pages=result[2],
                    user_posts=user_posts,
                    post_id=int(pid),
                    likes_error=error)

    def make_pages(self, all_posts):
        """This method provides pagination for index page

        Args:
            all_posts: all posts in the datastore

        Returns:
            tuple[0]: Posts
            tuple[1]: Number of posts
            tuple[2]: Number of pages
        """
        page = self.request.get('page')

        # In case page is not specified, set it to 1
        if not page:
            page = 1

        # Get total number of posts
        total_posts = len(all_posts)
        if total_posts % IndexHandler.per_page > 0:
            # Add one page for less than per_page posts
            pages = (total_posts/IndexHandler.per_page) + 1
        else:
            pages = (total_posts/IndexHandler.per_page)

        # Calculate the start index
        start_index = (int(page) - 1) * IndexHandler.per_page

        # Select posts for one page
        posts = all_posts[start_index:start_index + IndexHandler.per_page]
        posts_len = len(posts[:])
        return [posts, posts_len, pages]


class RegisterHandler(common_utilities.BaseHandler):

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
            if repo.UserEntity.by_name(username):
                self.render(
                    'register.html', error_username="User already exists")
            else:
                # Create hash for password for security
                hashed_password = SecurityProvider.make_secure_password(
                    username, password)
                new_user = repo.UserEntity.register(
                    username, hashed_password, email)
                repo.UserEntity.commit_user(new_user)
                self.create_login_cookie(new_user)
                self.redirect('/welcome')


class LoginHandler(common_utilities.BaseHandler):

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
        user = repo.UserEntity.by_name(name)

        # If user exists, check the password with saved hash
        if user and SecurityProvider.check_secure_password(name, password, user.password):
            return user


class LogoutHandler(common_utilities.BaseHandler):

    """This class handles logout request"""

    # region Handler methods
    def get(self):
        """This method logs the user out and redirects to index page"""
        self.logout()
        self.redirect('/')


class NewPostHandler(common_utilities.BaseHandler):

    """This class handles new post requests"""

    # region Handler methods
    def get(self):
        """This method gets the new post page"""
        # Check if user is logged in
        if self.user:
            self.render('/newpost.html')
        else:
            # If user is not logged in, redirect to login page
            self.redirect('/login')

    def post(self):
        """This method posts to the new post page"""
        if not self.user:
            return self.redirect('/login')

        title = self.request.get('title')
        content = self.request.get('content')

        if title and content:
            # Format the content for display
            format_content = content.replace('\n', '<br>')
            post = repo.PostEntity.create_post(title=title,
                                               content=format_content,
                                               author=self.user.username,
                                               created_by=self.user.key().id())
            repo.PostEntity.commit_post(post)
            self.redirect('/post/{0}'.format(post.key().id()))
        else:
            self.render('newpost.html', error="Subject and content please!")


class PostHandler(common_utilities.BaseHandler):

    """This class handles blog post modifications"""

    # region Handler methods
    def get(self, pid):
        """This method gets the post page of given post id for logged in users

        Args:
            pid: The post id
        """
        if not self.user:
            return self.redirect('/login')

        post = repo.PostEntity.by_id(int(pid))
        if post:
            post_comments = post.get_all_comments()
            if not post_comments:
                post_comments = []
            return self.render('post.html', post=post, post_comments=post_comments)

        self.redirect('/')

    def edit_post(self, pid):
        """This method edits the post with given post id for logged in users

        Args:
            pid: The post id
        """
        if not self.user:
            return self.redirect('/login')

        title = self.request.get('post_title')
        content = self.request.get('post_content')

        if title and content:
            post = repo.PostEntity.by_id(int(pid))
            post.title = title

            # Format the content before saving
            post.content = content.replace('\n', '<br>')
            repo.PostEntity.commit_post(post)

        self.redirect('/{0}/{1}'.format('post', pid))

    def delete_post(self, pid):
        """This method deletes the post with given post id for logged in users

        Args:
            pid: The post id
        """
        if not self.user:
            return self.redirect('/login')

        post = repo.PostEntity.by_id(int(pid))
        if post:
            post.delete()
            self.redirect('/')
        else:
            self.error(404)

    def like_post(self, pid):
        """This method adds likes for the post with given post id

        Args:
            pid: The post id
        """
        if not self.user:
            return self.redirect('/login')

        post = repo.PostEntity.by_id(int(pid))

        # Check if the user has already liked this post
        if post and not self.user.check_likes(pid):
            self.user.liked_posts = str(pid)
            post.likes += 1
            repo.UserEntity.commit_user(self.user)
            repo.PostEntity.commit_post(post)
        elif post:
            return self.redirect('/{0}'.format(pid))

        self.redirect('/')

    def unlike_post(self, pid):
        """This method reduces likes for the post with given post id

        Args:
            pid: The post id
        """
        if not self.user:
            return self.redirect('/login')

        post = repo.PostEntity.by_id(int(pid))

        # Check if the user has already unliked this post
        if post and self.user.check_likes(pid):
            self.user.liked_posts = ""

            # Likes should not be negative
            if post.likes > 0:
                post.likes -= 1
            else:
                post.likes = 0
            repo.UserEntity.commit_user(self.user)
            repo.PostEntity.commit_post(post)
        elif post:
            return self.redirect('/{0}'.format(pid))

        self.redirect('/')

    def add_comment(self, pid):
        """This method adds comment for the post with given post id

        Args:
            pid: The post id
        """
        if self.user:
            post = repo.PostEntity.by_id(int(pid))
            comment_content = self.request.get('comment')
            if post and comment_content:
                comment = repo.CommentEntity.register(post=post,
                                                      comment_by=self.user.username,
                                                      comment_by_id=self.user.key().id(),
                                                      comment=comment_content)
                repo.CommentEntity.commit_comment(comment)
                return self.redirect('/{0}/{1}'.format('post',
                                                       post.key().id()))

        self.redirect('/login')

    def edit_comment(self, cid, pid):
        """This method edits comment with for the given post and given comment id

        Args:
            cid: The comment id
            pid: The post id
        """
        if self.user:
            comment_object = repo.CommentEntity.by_id(int(cid))
            comment_content = self.request.get('post_comment')
            if comment_object and comment_content:
                comment_object.comment = comment_content
                repo.CommentEntity.commit_comment(comment_object)
                return self.redirect('/{0}/{1}'.format('post',
                                                       pid))

        self.redirect('/login')

    def delete_comment(self, cid, pid):
        """This method deletes the comment for given post with given comment id

        Args:
            cid: The comment id
            pid: The post id
        """
        if self.user:
            comment = repo.CommentEntity.by_id(int(cid))
            if comment:
                comment.delete()
                return self.redirect('/{0}/{1}'.format('post',
                                                       pid))

        self.redirect('/login')


class UserInfoHandler(common_utilities.BaseHandler):

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
                repo.UserEntity.commit_user(self.user)

        self.redirect('/')

    def about_user(self, *args):
        """This method gets the about page for a given user

        Args:
            args[0]: The username(unused, added for more readability of route)
            args[1]: The user id
        """
        user_for_about = len(args) == 2 and repo.UserEntity.by_id(int(args[1]))
        if user_for_about:
            user_posts = UserInfoHandler.get_all_posts(
                user_for_about.key().id())
            if not user_posts:
                user_posts = []
            return self.render(
                'user_info.html', userA=user_for_about, user_posts=user_posts)

        self.redirect("/")


class AboutHandler(common_utilities.BaseHandler):

    """This class serves responsive webpage"""

    def get(self):
        """This method gets the about page"""
        self.render('about.html')
