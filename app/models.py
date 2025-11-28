from sqlalchemy import Column, ForeignKey, Integer, String, Boolean
from .database import Base

class User(Base):
    """
    User model class
    """

    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String)

