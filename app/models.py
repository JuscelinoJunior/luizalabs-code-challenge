from sqlalchemy import Column, Integer, String, UniqueConstraint, ForeignKey
from sqlalchemy.orm import relationship, backref
from app.database import Base

class Wishlist(Base):
    __tablename__ = "wishlist"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(Integer, nullable=False)

    user = relationship("User", backref=backref("wishlist", lazy="select"))

    __table_args__ = (UniqueConstraint("user_id", "product_id", name="_user_product_uc"),)

class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)
    name = Column(String)
    hashed_password = Column(String)
    role = Column(String, default="customer")