import csv
import os
from sqlalchemy.orm import Session
from models import Post
from database import engine

CSV_FILE = "scraped_tweets.csv"


def ingest_csv():
    if not os.path.exists(CSV_FILE):
        print(f"{CSV_FILE} not found.")
        return

    session = Session(bind=engine)

    with open(CSV_FILE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            post_id = row["Post ID"]
            existing_post = session.query(Post).filter_by(post_id=post_id).first()
            if not existing_post:
                new_post = Post(
                    post_id=row["Post ID"],
                    user_handle=row["User Handle"],
                    username=row["Username"],
                    datetime=row["Datetime"],
                    content=row["Content"],
                    replies=row.get("Replies", 0),
                    reposts=row.get("Reposts", 0),
                    likes=row.get("Likes", 0),
                    views=row.get("Views", 0),
                    post_url=row["Post URL"],
                    # category_id=None, by default
                )
                session.add(new_post)

    session.commit()
    session.close()
    print("CSV ingestion complete!")


if __name__ == "__main__":
    ingest_csv()
