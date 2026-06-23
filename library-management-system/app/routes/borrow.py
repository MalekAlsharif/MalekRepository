from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..database import SessionLocal
from .. import crud, schemas, auth

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=schemas.BorrowResponse)
def borrow_book(
    borrow: schemas.BorrowRequest,
    db: Session = Depends(get_db),
    current_user = Depends(auth.get_current_user)
):
    # Check if user exists
    user = crud.get_user(db, borrow.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if book exists and is available
    book = crud.get_book(db, borrow.isbn)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    if book.available_copies <= 0:
        # Create reservation
        reservation = crud.create_reservation(db, borrow.user_id, borrow.isbn)
        if reservation:
            raise HTTPException(status_code=400, detail="Book unavailable. Reservation created.")
        raise HTTPException(status_code=400, detail="Book unavailable")
    
    # Borrow the book
    borrow_record = crud.borrow_book(db, borrow.user_id, borrow.isbn)
    if not borrow_record:
        raise HTTPException(status_code=400, detail="Could not borrow book")
    
    return borrow_record

@router.get("/user/{user_id}", response_model=List[schemas.BorrowResponse])
def get_user_borrows(
    user_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(auth.get_current_user)
):
    if current_user.id != user_id and current_user.role not in ["admin", "librarian"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    return crud.get_user_borrows(db, user_id)