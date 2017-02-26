from models.user import UserEntity
from models.post import PostEntity
from models.comment import CommentEntity
from infrastructure import decorators
from base import BaseHandler


class PostHandler(BaseHandler):

    """This class handles blog post modifications"""

    # region Handler methods
    @decorators.post_exists
    def get(self, post):
        """This method gets the post page of given post id for logged in users

        Args:
            pid: The post id
            post: The post object
        """
        if not self.user:
            return self.redirect('/login')

        post_comments = post.get_all_comments()
        if not post_comments:
            post_comments = []
        return self.render('post.html', post=post, post_comments=post_comments)

        self.redirect('/')

    @decorators.post_exists
    @decorators.user_owns_post
    def edit_post(self, post):
        """This method edits the post with given post id for logged in users

        Args:
            pid: The post id
        """
        if not self.user:
            return self.redirect('/login')

        title = self.request.get('post_title')
        content = self.request.get('post_content')

        if title and content:
            post.title = title

            # Format the content before saving
            post.content = content.replace('\n', '<br>')
            PostEntity.commit_post(post)

        self.redirect('/{0}/{1}'.format('post', post.key().id()))

    @decorators.post_exists
    @decorators.user_owns_post
    def delete_post(self, post):
        """This method deletes the post with given post id for logged in users

        Args:
            post: The post
        """
        if not self.user:
            return self.redirect('/login')

        post.delete()
        self.redirect('/')

    @decorators.post_exists
    def like_post(self, post):
        """This method adds likes for the given post

        Args:
            post: The post
        """
        if not self.user:
            return self.redirect('/login')

        # Check if the user has already liked this post
        pid = post.key().id()
        if not self.user.check_likes(pid):
            self.user.liked_posts = str(pid)
            post.likes += 1
            UserEntity.commit_user(self.user)
            PostEntity.commit_post(post)
        elif post:
            return self.redirect('/{0}'.format(pid))

        self.redirect('/')

    @decorators.post_exists
    def unlike_post(self, post):
        """This method reduces likes for the post with given post id

        Args:
            pid: The post id
        """
        if not self.user:
            return self.redirect('/login')

        # Check if the user has already unliked this post
        pid = post.key().id()
        if self.user.check_likes(pid):
            self.user.liked_posts = ""

            # Likes should not be negative
            if post.likes > 0:
                post.likes -= 1
            else:
                post.likes = 0
            UserEntity.commit_user(self.user)
            PostEntity.commit_post(post)
        elif post:
            return self.redirect('/{0}'.format(pid))

        self.redirect('/')

    @decorators.post_exists
    def add_comment(self, post):
        """This method adds comment for the post with given post id

        Args:
            post: The post
        """
        if self.user:
            comment_content = self.request.get('comment')
            if comment_content:
                comment = CommentEntity.register(post=post,
                                                      comment_by=self.user.username,
                                                      comment_by_id=self.user.key().id(),
                                                      comment=comment_content)
                CommentEntity.commit_comment(comment)
                return self.redirect('/{0}/{1}'.format('post',
                                                       post.key().id()))

        self.redirect('/login')

    @decorators.comment_exists
    @decorators.user_owns_comment
    def edit_comment(self, comment_object, pid):
        """This method edits comment with for the given post and given comment id

        Args:
            comment_object: The comment
            pid: The post id
        """
        if self.user:
            comment_content = self.request.get('post_comment')
            if comment_content:
                comment_object.comment = comment_content
                CommentEntity.commit_comment(comment_object)
                return self.redirect('/{0}/{1}'.format('post',
                                                       pid))

        self.redirect('/login')

    @decorators.comment_exists
    @decorators.user_owns_comment
    def delete_comment(self, comment_object, pid):
        """This method deletes the comment for given post with given comment id

        Args:
            comment_object: The comment
            pid: The post id
        """
        if self.user:
            comment_object.delete()
            return self.redirect('/{0}/{1}'.format('post',
                                                   pid))

        self.redirect('/login')
