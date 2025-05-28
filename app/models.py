from sqlalchemy import Column, Integer, String, UniqueConstraint, ForeignKey
from sqlalchemy.orm import relationship, backref
from database import Base

class Customer(Base):
    __tablename__ = "customer"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False, unique=True)

    __table_args__ = (UniqueConstraint('email', name='uix_email'),)

class Wishlist(Base):
    __tablename__ = "wishlist"
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customer.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(Integer, nullable=False)

    customer = relationship("Customer", backref=backref("wishlist", lazy="select"))

    __table_args__ = (UniqueConstraint("customer_id", "product_id", name="_customer_product_uc"),)
