import re
import common_utilities
import repo

# region Page handlers


class IndexHandler(common_utilities.BaseHandler):

    """This class provides content for index page"""

    # class members
    # How many posts per page
    per_page = 5

    # region Handler methods
    def get(self):
        # Get all posts
        all_posts = repo.PostEntity.execute_query(repo.SELECT_ALL_POSTS)

        # Get all posts by logged in user
        user_posts = self.user and all_posts and self.get_all_posts(
            self.user.key().id())
        if not user_posts:
            user_posts = []

        # Make pages
        if all_posts:
            result = self.make_pages(all_posts)
        else:
            result = [[], 0, 1]

        self.render('index.html',
                    posts=result[0],
                    posts_len=result[1],
                    pages=result[2],
                    user_posts=user_posts,
                    likes_error=PostHandler.likes_error())

    def make_pages(self, all_posts):
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
    def valid_username(self, username):
        return username and RegisterHandler.USER_RE.match(username)

    def valid_password(self, password):
        return password and RegisterHandler.PASS_RE.match(password)

    def valid_email(self, email):
        return not email or RegisterHandler.EMAIL_RE.match(email)

    # region Handler methods
    def get(self):
        if not self.user:
            self.render('register.html')
        else:
            self.redirect('/')

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')
        verify = self.request.get('verify')
        email = self.request.get('email')

        params = dict(username=username,
                      email=email)
        have_error = False

        if not self.valid_username(username):
            params['error_username'] = "That's not a valid username."
            have_error = True

        if not self.valid_password(password):
            params['error_password'] = "That wasn't a valid password."
            have_error = True
        elif password != verify:
            params['error_verify'] = "Your passwords didn't match."
            have_error = True

        if not self.valid_email(email):
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
                pw = common_utilities.SecurityProvider.make_secure_password(
                    username, password)
                new_user = repo.UserEntity.register(username, pw, email)
                repo.UserEntity.commit_user(new_user)
                self.create_login_cookie(new_user)
                self.redirect('/welcome')


class LoginHandler(common_utilities.BaseHandler):

    """This class provides content for login page with validation"""

    # region Handler methods
    def get(self):
        if not self.user:
            self.render('login.html')
        else:
            self.redirect('/')

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')
        u = self.login(username, password)
        if u:
            self.create_login_cookie(u)
            self.redirect('/welcome')
        else:
            self.render('login.html', error="Invalid username or password")

    # region functions
    def login(self, name, pw):
        user = repo.UserEntity.by_name(name)

        # If user exists, check the password with saved hash
        if user and common_utilities.SecurityProvider.check_secure_password(name, pw, user.password):
            return user


class LogoutHandler(common_utilities.BaseHandler):

    """This class handles logout request"""

    # region Handler methods
    def get(self):
        self.logout()
        self.reset_return_url()
        self.redirect('/')


class NewPostHandler(common_utilities.BaseHandler):

    """This class handles new post requests"""

    # region Handler methods
    def get(self):
        # Check if user is logged in
        if self.user:
            self.reset_return_url()
            self.render('/newpost.html')
        else:
            # If user is not logged in, redirect to login page
            # And set return-url to show the url that the user
            # was trying to access
            self.set_secure_cookie('return-url', '/newpost')
            self.redirect('/login')

    def post(self):
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

    # region class members
    _likes_error = " "

    # region class methods
    @classmethod
    def likes_error(cls):
        return cls._likes_error

    # region Handler methods
    def get(self, pid):
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
        if not self.user:
            return self.redirect('/login')

        post = repo.PostEntity.by_id(int(pid))
        if post:
            post.delete()
            self.redirect('/')
        else:
            self.error(404)

    def like_post(self, pid):
        if not self.user:
            return self.redirect('/login')

        post = repo.PostEntity.by_id(int(pid))

        # Check if the user has already liked this post
        if post and not self.user.check_likes(pid):
            self.user.liked_posts = str(pid)
            post.likes += 1
            repo.UserEntity.commit_user(self.user)
            repo.PostEntity.commit_post(post)
            PostHandler._likes_error = ""
        else:
            PostHandler._likes_error = "You can only like once"

        self.redirect('/')

    def unlike_post(self, pid):
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
            PostHandler._likes_error = ""
        else:
            PostHandler._likes_error = "You can only unlike once"

        self.redirect('/')

    def add_comment(self, pid):
        if self.user:
            post = repo.PostEntity.by_id(int(pid))
            comment_content = self.request.get('comment')
            if post and comment_content:
                comment = repo.CommentEntity.register(post=post,
                                                      comment_by=self.user.username,
                                                      comment_by_id=str(
                                                          self.user.key().id()),
                                                      comment=comment_content)
                repo.CommentEntity.commit_comment(comment)
                return self.redirect('/{0}/{1}'.format('post',
                                                       post.key().id()))

        self.redirect('/login')


class UserInfoHandler(common_utilities.BaseHandler):

    """This class handles user information"""

    def welcome(self):
        if self.user:
            return self.render('welcome.html')
        self.redirect('/register')

    def add_about(self, uid):
        if self.user and uid == str(self.user.key().id()):
            about = self.request.get('about')
            if about:
                self.user.about = about
                repo.UserEntity.commit_user(self.user)

        self.redirect('/')

    def about_user(self, username, uid):
        userA = repo.UserEntity.by_id(int(uid))
        if userA:
            user_posts = self.get_all_posts(userA.key().id())
            if not user_posts:
                user_posts = []
            self.render('user_info.html', userA=userA, user_posts=user_posts)


class AboutHandler(common_utilities.BaseHandler):

    """This class serves responsive webpage"""

    def get(self):
        self.render('about.html')
