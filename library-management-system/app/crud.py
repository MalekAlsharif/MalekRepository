from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from . import models, schemas
from .auth import get_password_hash

# User CRUD
def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        role=user.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

# Book CRUD
def create_book(db: Session, book: schemas.BookCreate):
    db_book = models.Book(**book.model_dump())
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

def get_book(db: Session, isbn: str):
    return db.query(models.Book).filter(models.Book.isbn == isbn).first()

def get_books(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Book).offset(skip).limit(limit).all()

def search_books(db: Session, query: str):
    return db.query(models.Book).filter(
        models.Book.title.contains(query) | 
        models.Book.author.contains(query) | 
        models.Book.isbn.contains(query)
    ).all()

def update_book(db: Session, isbn: str, book_update: schemas.BookUpdate):
    db_book = get_book(db, isbn)
    if not db_book:
        return None
    for key, value in book_update.model_dump(exclude_unset=True).items():
        setattr(db_book, key, value)
    db.commit()
    db.refresh(db_book)
    return db_book

def delete_book(db: Session, isbn: str):
    db_book = get_book(db, isbn)
    if not db_book:
        return False
    db.delete(db_book)
    db.commit()
    return True

# Borrow CRUD
def borrow_book(db: Session, user_id: int, isbn: str):
    book = get_book(db, isbn)
    if not book or book.available_copies <= 0:
        return None
    
    book.available_copies -= 1
    if book.available_copies == 0:
        book.status = models.BookStatus.BORROWED
    
    borrow = models.BorrowTransaction(
        user_id=user_id,
        isbn=isbn,
        due_date=datetime.utcnow() + timedelta(days=14)
    )
    db.add(borrow)
    db.commit()
    db.refresh(borrow)
    return borrow

def return_book(db: Session, user_id: int, isbn: str):
    borrow = db.query(models.BorrowTransaction).filter(
        models.BorrowTransaction.user_id == user_id,
        models.BorrowTransaction.isbn == isbn,
        models.BorrowTransaction.status == "borrowed"
    ).first()
    
    if not borrow:
        return None
    
    borrow.return_date = datetime.utcnow()
    borrow.status = "returned"
    
    book = get_book(db, isbn)
    if book:
        book.available_copies += 1
        book.status = models.BookStatus.AVAILABLE
    
    db.commit()
    return borrow

def get_user_borrows(db: Session, user_id: int):
    return db.query(models.BorrowTransaction).filter(
        models.BorrowTransaction.user_id == user_id
    ).all()

# Reservation CRUD
def create_reservation(db: Session, user_id: int, isbn: str):
    existing = db.query(models.Reservation).filter(
        models.Reservation.user_id == user_id,
        models.Reservation.isbn == isbn,
        models.Reservation.status == "active"
    ).first()
    
    if existing:
        return None
    
    reservation = models.Reservation(user_id=user_id, isbn=isbn)
    db.add(reservation)
    db.commit()
    db.refresh(reservation)
    return reservation

# Reports
def get_most_borrowed_books(db: Session, limit: int = 5):
    from sqlalchemy import func
    return db.query(
        models.BorrowTransaction.isbn,
        models.Book.title,
        func.count(models.BorrowTransaction.id).label('borrow_count')
    ).join(models.Book).group_by(
        models.BorrowTransaction.isbn
    ).order_by(
        func.count(models.BorrowTransaction.id).desc()
    ).limit(limit).all()

def get_overdue_books(db: Session):
    return db.query(models.BorrowTransaction).filter(
        models.BorrowTransaction.due_date < datetime.utcnow(),
        models.BorrowTransaction.status == "borrowed"
    ).all()

def get_active_users(db: Session, limit: int = 5):
    from sqlalchemy import func
    return db.query(
        models.User.id,
        models.User.username,
        func.count(models.BorrowTransaction.id).label('borrow_count')
    ).join(models.BorrowTransaction).group_by(
        models.User.id
    ).order_by(
        func.count(models.BorrowTransaction.id).desc()
    ).limit(limit).all()