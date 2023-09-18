import local_db.db as db
latest_10_posts = db.fetch_latest_posts(10)
for post in latest_10_posts:
    print(post.title)