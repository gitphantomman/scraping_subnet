from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
import hashlib
Base = declarative_base()

class TwitterPost(Base):
    """_SQL Entity to store scraped twitter posts_

    Args:
    
    """
    __tablename__ = 'twitter_posts'
    url_hash = Column(String, primary_key=True)
    id = Column(String)
    url = Column(String)
    text = Column(Text)
    created_at = Column(DateTime)
    uploaded = Column(Boolean, default = False)
    

engine = create_engine('sqlite:///twitter_data.db')

Base.metadata.create_all(engine)

__all__ = ["TwitterPost", "store_data", "fetch_latest_posts"]

def store_data(twitterPost):
    """Stores Reddit posts to the database.

    Args:
        tweet (lsit[TwitterPost]): The list of posts to store.

    Returns:

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
    
    except Exception as e:
        print(f"Error while storing data: {e}")
    finally:
        session.close()
        


def fetch_latest_posts(n = 50):
    """Fetches the latest N Twitter posts from the database based on their creation date.

    Args:
        n (int): Number of latest posts to fetch.

    Returns:
        list[TwitterPost]: List of N latest RedditPost objects.
    """
    Session = sessionmaker(bind=engine)
    session = Session()
    returnData = []
    try:
        # Fetch the latest N posts. (uploaded == false)
        posts = session.query(TwitterPost).order_by(TwitterPost.created_at.desc()).limit(n).all()
        # Update uploaded field to True for the fetched posts. .filter(RedditPost.uploaded != True)
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