from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
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
engine = create_engine('sqlite:///twitter_data.db')

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

def fetch_latest_posts(n = 50):
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
        posts = session.query(TwitterPost).order_by(TwitterPost.created_at.desc()).limit(n).all()
        # Update uploaded field to True for the fetched posts. .filter(TwitterPost.uploaded != True)
        for post in posts:
            post.uploaded = True
            returnData.append({"id" : post.id, "text": post.text, "url": post.url, "url_hash": post.url_hash, "created_at": post.created_at, "type": "twitter"})
        # Commit the changes to the database.
        session.commit()
        return returnData
    # TODO: Add specific exceptions for better error handling
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
    # TODO: Add specific exceptions for better error handling
    except Exception as e:
        print(f"Error while fetching data by URL: {e}")
        return None
    finally:
        session.close()
