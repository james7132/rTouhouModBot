import os
from util import *
from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import declarative_base

db_path = "/db/r_touhou_mod.db"

engine = create_engine('sqlite:///{0}'.format(db_path))

Session = sessionmaker(bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(String, primary_key=True, autoincrement=False)

class Post(Base):
    __tablename__ = 'posts'

    id = Column(String, primary_key=True, autoincrement=False)
    date = Column(DateTime)
    status = Column(Enum(Decision))
    author_id = Column(String, ForeignKey('users.id'))

Post.author = relationship('User', back_populates='posts')
User.posts = relationship('Post', order_by=Post.date, back_populates='author')

db_dir = os.path.dirname(db_path)
if not os.path.exists(db_dir):
    os.makedirs(db_dir)
if not os.path.isfile(db_path):
    Base.metadata.create_all(engine)
