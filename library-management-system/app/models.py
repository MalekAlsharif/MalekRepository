from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Text, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base
import enum

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    LIBRARIAN = "librarian"
    STUDENT = "student"

class BookStatus(str, enum.Enum):
    AVAILABLE = "available"
    BORROWED = "borrowed"
    RESERVED = "reserved"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(Enum(UserRole), default=UserRole.STUDENT)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    borrows = relationship("BorrowTransaction", back_populates="user")
    reservations = relationship("Reservation", back_populates="user")

class Book(Base):
    __tablename__ = "books"
    
    isbn = Column(String, primary_key=True, index=True)
    title = Column(String, index=True)
    author = Column(String)
    publisher = Column(String)
    publication_year = Column(Integer)
    available_copies = Column(Integer, default=1)
    status = Column(Enum(BookStatus), default=BookStatus.AVAILABLE)
    
    borrows = relationship("BorrowTransaction", back_populates="book")
    reservations = relationship("Reservation", back_populates="book")

class BorrowTransaction(Base):
    __tablename__ = "borrow_transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    isbn = Column(String, ForeignKey("books.isbn"))
    borrow_date = Column(DateTime, default=datetime.utcnow)
    due_date = Column(DateTime)
    return_date = Column(DateTime, nullable=True)
    status = Column(String, default="borrowed")  # borrowed, returned, overdue
    
    user = relationship("User", back_populates="borrows")
    book = relationship("Book", back_populates="borrows")

class Reservation(Base):
    __tablename__ = "reservations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    isbn = Column(String, ForeignKey("books.isbn"))
    reservation_date = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="active")  # active, fulfilled, cancelled
    
    user = relationship("User", back_populates="reservations")
    book = relationship("Book", back_populates="reservations")