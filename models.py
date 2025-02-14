from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base, engine


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True)

    parent = relationship("Category", remote_side=[id], backref="subcategories")


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True)
    post_id = Column(String, unique=True, index=True)
    user_handle = Column(String)
    username = Column(String)
    datetime = Column(String)
    content = Column(String)
    replies = Column(Integer)
    reposts = Column(Integer)
    likes = Column(Integer)
    views = Column(Integer)
    post_url = Column(String)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)

    category = relationship("Category", backref="posts")


def init_db():
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_db()
