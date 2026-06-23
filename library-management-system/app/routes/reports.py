from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from ..database import SessionLocal
from .. import crud, auth

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/most-borrowed")
def get_most_borrowed(
    limit: int = 5,
    db: Session = Depends(get_db),
    current_user = Depends(auth.get_current_librarian)
):
    results = crud.get_most_borrowed_books(db, limit)
    return [
        {
            "isbn": r.isbn,
            "title": r.title,
            "borrow_count": r.borrow_count
        }
        for r in results
    ]

@router.get("/overdue")
def get_overdue(
    db: Session = Depends(get_db),
    current_user = Depends(auth.get_current_librarian)
):
    results = crud.get_overdue_books(db)
    return [
        {
            "user_id": r.user_id,
            "isbn": r.isbn,
            "borrow_date": r.borrow_date,
            "due_date": r.due_date
        }
        for r in results
    ]

@router.get("/active-users")
def get_active_users(
    limit: int = 5,
    db: Session = Depends(get_db),
    current_user = Depends(auth.get_current_admin)
):
    results = crud.get_active_users(db, limit)
    return [
        {
            "user_id": r.id,
            "username": r.username,
            "borrow_count": r.borrow_count
        }
        for r in results
    ]

@router.get("/monthly")
def get_monthly_stats(
    db: Session = Depends(get_db),
    current_user = Depends(auth.get_current_librarian)
):
    from sqlalchemy import func
    from ..models import BorrowTransaction
    
    results = db.query(
        func.strftime('%Y-%m', BorrowTransaction.borrow_date).label('month'),
        func.count(BorrowTransaction.id).label('count')
    ).group_by('month').order_by('month').all()
    
    return [{"month": r.month, "count": r.count} for r in results]