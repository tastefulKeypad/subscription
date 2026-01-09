from sqlalchemy import Column, Integer, Integer, String, DateTime, Boolean, Date
from .database import Base

class User(Base):
    __tablename__ = "users"
    id       = Column(Integer, primary_key=True, index=True)
    name     = Column(String, nullable=False)
    email    = Column(String, nullable=False)
    password = Column(String, nullable=False)
    isAdmin  = Column(Boolean, nullable=False)

class Product(Base):
    __tablename__ = "products"
    id    = Column(Integer, primary_key=True, index=True)
    name  = Column(String, nullable=False)
    price = Column(Integer, nullable=False)
    
class Promo(Base):
    __tablename__ = "promos"
    name      = Column(String, primary_key=True, nullable=False)
    productId = Column(Integer, nullable=False)
    discount  = Column(Integer, nullable=False)
    expDate   = Column(Date, nullable=False)

class Transaction(Base):
    __tablename__ = "transactions"
    id          = Column(Integer, primary_key=True, index=True)
    userId      = Column(Integer, nullable=False)
    productId   = Column(Integer, nullable=False)
    promoName   = Column(String, nullable=False)
    action      = Column(String, nullable=False)
    dateTime    = Column(DateTime, nullable=False)
    status      = Column(String, nullable=False)
    bankChange  = Column(Integer, nullable=False)

class Subs(Base):
    __tablename__ = "subs"
    id = Column(Integer, primary_key=True, index=True)
    userId      = Column(Integer, nullable=False)
    productId   = Column(Integer, nullable=False)
    price       = Column(Integer, nullable=False)
    status      = Column(String, nullable=False)
    dateTime    = Column(DateTime, nullable=False)
