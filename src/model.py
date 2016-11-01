from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:///:memory:', echo=True)

Session = sessionmaker(bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    fullname = Column(String, primary_key=True)

class Post(Base):
    __tablename__ = 'posts'

    fullname = Column(String, primary_key=True)
    date = Column(DateTime)
    is_image = Column(Boolean)
    author_fullname = Column(String, ForeignKey('users.fullname'))

Post.author = relationship('User', back_populates='posts')
User.posts = relationship('Post', order_by=Post.date, back_populates='author')
