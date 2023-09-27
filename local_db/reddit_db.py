from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime

Base = declarative_base()

class RedditPost(Base):
    """_SQL Entity to store scraped reddit posts_

    Args:
    
    """
    __tablename__ = 'reddit_posts'
    id = Column(String, primary_key=True)
    title = Column(String)
    url = Column(String)
    content = Column(Text)
    created_utc = Column(DateTime)
    uploaded = Column(Boolean, default = False)
    

engine = create_engine('sqlite:///reddit_data.db')

Base.metadata.create_all(engine)

__all__ = ["RedditPost", "store_data", "fetch_latest_posts"]

def store_data(submission):
    """Stores Reddit posts to the database.

    Args:
        submission (lsit[RedditPost]): The list of posts to store.

    Returns:

    """
    Session = sessionmaker(bind = engine)
    session = Session()
    dt_object = datetime.fromtimestamp(submission.created_utc)    
    try:
        post = RedditPost(id = submission.id, title = submission.title, url = submission.url, content = submission.selftext, created_utc = dt_object)
        # Add and commit
        session.add(post)
        session.commit()
    
    except Exception as e:
        print(f"Error while storing data: {e}")
    finally:
        session.close()
        
def fetch_data(post_id=None):
    """Fetches Reddit posts from the database.

    Args:
        post_id (str, optional): The ID of a specific post to fetch. If None, fetches all posts. Defaults to None.

    Returns:
        list[RedditPost]: List of RedditPost objects.
    """
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
    """Fetches the latest N Reddit posts from the database based on their creation date.

    Args:
        n (int): Number of latest posts to fetch.

    Returns:
        list[RedditPost]: List of N latest RedditPost objects.
    """
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