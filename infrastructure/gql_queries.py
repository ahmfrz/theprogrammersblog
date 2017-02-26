"""Defines GQL queries"""

# region Queries
SELECT_ALL_POSTS = "SELECT * FROM PostEntity ORDER BY created_date DESC"
SELECT_ALL_POSTS_BY = "SELECT * FROM PostEntity WHERE created_by = {0} ORDER BY created_date DESC"
