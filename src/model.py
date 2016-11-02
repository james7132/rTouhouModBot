import os
from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import declarative_base

db_path = "/db/r_touhou_mod.db"

engine = create_engine('sqlite:///{0}'.format(db_path), echo=True)

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

db_dir = os.path.dirname(db_path)
if not os.path.exists(db_dir):
    os.makedirs(db_dir)
if not os.path.isfile(db_path):
    Base.metadata.create_all(engine)
