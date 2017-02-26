from models.post import PostEntity
from base import BaseHandler

class NewPostHandler(BaseHandler):

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
            post = PostEntity.create_post(title=title,
                                               content=format_content,
                                               author=self.user.username,
                                               created_by=self.user.key().id())
            PostEntity.commit_post(post)
            self.redirect('/post/{0}'.format(post.key().id()))
        else:
            self.render('newpost.html', error="Subject and content please!")
