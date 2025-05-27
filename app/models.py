from sqlalchemy import Column, Integer, String, UniqueConstraint
from database import Base

class Customer(Base):
    __tablename__ = "customer"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False, unique=True)

    __table_args__ = (UniqueConstraint('email', name='uix_email'),)
