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
# from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import  sessionmaker
from datetime import datetime
import hashlib

# Create a base class for declarative models
Base = declarative_base()

# Define the TwitterPost model
class TwitterPost(Base):
    """
    SQL Entity to store scraped twitter posts

    Attributes:
        url_hash (str): The hash of the post url, used as primary key
        id (str): The id of the post
        url (str): The url of the post
        text (str): The content of the post
        created_at (DateTime): The creation time of the post
        uploaded (Boolean): Flag to check if the post has been uploaded or not
    """
    __tablename__ = 'twitter_posts'
    url_hash = Column(String, primary_key=True)
    id = Column(String)
    url = Column(String)
    text = Column(Text)
    created_at = Column(DateTime)
    uploaded = Column(Boolean, default = False)

# Create a SQLite engine for the database
engine = create_engine('sqlite:///./twitter_data.db')

# Create all tables in the engine
Base.metadata.create_all(engine)

# TODO: Check if the following functions are required in the current context
__all__ = ["TwitterPost", "store_data", "fetch_latest_posts"]

def store_data(twitterPost):
    """
    Stores Twitter posts to the database.

    Args:
        twitterPost (dict): The post data to store.

    Returns:
        None
    """
    Session = sessionmaker(bind = engine)
    session = Session()
    try:
        hash_object = hashlib.sha256()
        # Generate url from twitter post id
        url = f"https://twitter.com/iamthecosmos888/status/{twitterPost['id']}"
        hash_object.update(url.encode())
        # Generate hash from url (primary key)
        hex_dig = hash_object.hexdigest()
        dt_object = datetime.strptime(twitterPost['created_at'], "%Y-%m-%dT%H:%M:%S.%fZ")  
        post = TwitterPost(id = twitterPost['id'], text = twitterPost['text'], url = url, url_hash = hex_dig, created_at = dt_object)
        # Add and commit
        session.add(post)
        session.commit()
    # TODO: Add specific exceptions for better error handling
    except Exception as e:
        print(f"Error while storing data: {e}")
    finally:
        session.close()

def fetch_latest_posts(n = None):
    """
    Fetches the latest N Twitter posts from the database based on their creation date.

    Args:
        n (int): Number of latest posts to fetch.

    Returns:
        list[dict]: List of N latest TwitterPost objects.
    """
    Session = sessionmaker(bind=engine)
    session = Session()
    returnData = []
    try:
        # Fetch the latest N posts. (uploaded == false)
        if n is None:
            posts = session.query(TwitterPost).filter(TwitterPost.uploaded != True).order_by(TwitterPost.created_at.desc()).all()
        else:
            posts = session.query(TwitterPost).filter(TwitterPost.uploaded != True).order_by(TwitterPost.created_at.desc()).limit(n).all()
        # Filter out even rows to only keep odd rows
        posts = posts[::2]
        print(f"half posts{posts}")
        # Update uploaded field to True for the fetched posts. .filter(TwitterPost.uploaded != True)
        for post in posts:
            post.uploaded = True
            returnData.append({"id" : post.id, "text": post.text, "url": post.url, "url_hash": post.url_hash, "created_at": post.created_at, "type": "twitter"})
        # Commit the changes to the database.
        session.commit()
        return returnData
    except Exception as e:
        print(f"Error while fetching data: {e}")
        return []
    finally:
        session.close()
def find_by_url_hash(url_hash):
    """
    Fetches the Twitter post from the database based on the URL hash.

    Args:
        url_hash (str): The hash of the post url to fetch.

    Returns:
        dict: The TwitterPost object if found, else None.
    """
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        # Query the database for a post with the given url_hash
        post = session.query(TwitterPost).filter_by(url_hash=url_hash).first()
        return {"id" : post.id, "url": post.url, "url_hash": post.url_hash, "text": post.text, "created_at": post.created_at}
    except Exception as e:
        print(f"Error while fetching data by URL: {e}")
        return None
    finally:
        session.close()

# Make uploaded column of all the rows in twitter_data.db False
def reset_uploaded():
    """
    Resets the uploaded column of all the rows in the database to False.

    Args:
        None

    Returns:
        None
    """
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        # Query the database for all posts
        posts = session.query(TwitterPost).all()
        # Set uploaded field to False for all the posts
        for post in posts:
            post.uploaded = False
        # Commit the changes to the database.
        session.commit()
    except Exception as e:
        print(f"Error while resetting uploaded column: {e}")
    finally:
        session.close()
