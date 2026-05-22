# models.py
from database import Base
from sqlalchemy import Boolean, Column, Integer, String, Text

class Todo(Base):
    __tablename__ = "todos"
    id    = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    done  = Column(Boolean, default=False)

class Category(Base):
    __tablename__ = "categories"
    id   = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    slug = Column(String, unique=True, nullable=False, index=True)

# Thêm model mới cho blog posts
class Post(Base):
    __tablename__ = "posts"
    id        = Column(Integer, primary_key=True, index=True)
    type      = Column(String)           # text | photo | video | instagram
    title     = Column(String, nullable=True)
    body      = Column(Text, nullable=True)
    images    = Column(Text, nullable=True)  # lưu dạng JSON string
    caption   = Column(String, nullable=True)
    embed_url = Column(String, nullable=True)
    url       = Column(String, nullable=True)
    category  = Column(String, default="daily-life", index=True)
    date      = Column(String)