"""Defines IndexHandler"""

from handlers.base import BaseHandler
from infrastructure import gql_queries
from models.post import PostEntity


class IndexHandler(BaseHandler):

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
        all_posts = PostEntity.execute_query(gql_queries.SELECT_ALL_POSTS)

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
