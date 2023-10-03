"""
The MIT License (MIT)
Copyright © 2023 Chris Wilson

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the “Software”), to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of
the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

from sqlalchemy import create_engine, Column, String, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Create a base class for declarative models
Base = declarative_base()

# Define the RedditPost model
class RedditPost(Base):
    """
    SQL Entity to store scraped reddit posts

    Attributes:
        id (str): The id of the post
        title (str): The title of the post
        url (str): The url of the post
        content (str): The content of the post
        created_utc (DateTime): The creation time of the post
        uploaded (bool): Whether the post has been uploaded or not
    """
    __tablename__ = 'reddit_posts'
    id = Column(String, primary_key=True)
    title = Column(String)
    url = Column(String)
    content = Column(Text)
    created_utc = Column(DateTime)
    uploaded = Column(Boolean, default = False)
    
# TODO: Add error handling for database connection
# Create a new engine instance
engine = create_engine('sqlite:///reddit_data.db')

# Create all tables in the engine
Base.metadata.create_all(engine)

# TODO: Check if these functions exist before exporting
# Export the RedditPost model and the data manipulation functions
__all__ = ["RedditPost", "store_data", "fetch_latest_posts"]

def store_data(submission):
    """
    Stores Reddit posts to the database.

    Args:
        submission (list[RedditPost]): The list of posts to store.

    Returns:
        None
    """
    # Create a new session
    Session = sessionmaker(bind = engine)
    session = Session()
    # Convert the creation time to a datetime object
    dt_object = datetime.fromtimestamp(submission.created_utc)    
    try:
        # Create a new post object and add it to the session
        post = RedditPost(id = submission.id, title = submission.title, url = submission.url, content = submission.selftext, created_utc = dt_object)
        session.add(post)
        session.commit()
    
    except Exception as e:
        print(f"Error while storing data: {e}")
    finally:
        session.close()
        
def fetch_data(post_id=None):
    """
    Fetches Reddit posts from the database.

    Args:
        post_id (str, optional): The ID of a specific post to fetch. If None, fetches all posts. Defaults to None.

    Returns:
        list[RedditPost]: List of RedditPost objects.
    """
    # Create a new session
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        if post_id:
            # Fetch a specific post by its ID.
            post = session.query(RedditPost).filter_by(id=post_id).first()
            return [post] if post else []

        else:
            # Fetch all posts.
            posts = session.query(RedditPost).all()
            return posts

    except Exception as e:
        print(f"Error while fetching data: {e}")
        return []

    finally:
        session.close()

def fetch_latest_posts(n):
    """
    Fetches the latest N Reddit posts from the database based on their creation date.

    Args:
        n (int): Number of latest posts to fetch.

    Returns:
        list[RedditPost]: List of N latest RedditPost objects.
    """
    # Create a new session
    Session = sessionmaker(bind=engine)
    session = Session()
    returnData = []
    try:
        # Fetch the latest N posts. (uploaded == false)
        posts = session.query(RedditPost).order_by(RedditPost.created_utc.desc()).limit(n).all()
        # Update uploaded field to True for the fetched posts. .filter(RedditPost.uploaded != True)
        for post in posts:
            post.uploaded = True
            returnData.append({"id" : post.id, "title": post.title, "content": post.content, "url": post.url, "created_utc": post.created_utc, "type": "reddit"})
         # Commit the changes to the database.
        session.commit()
        return returnData

    except Exception as e:
        print(f"Error while fetching data: {e}")
        return []

    finally:
        session.close()