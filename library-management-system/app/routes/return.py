from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import SessionLocal
from .. import crud, schemas, auth

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/")
def return_book(
    return_request: schemas.ReturnRequest,
    db: Session = Depends(get_db),
    current_user = Depends(auth.get_current_user)
):
    # Check if user exists
    user = crud.get_user(db, return_request.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Return the book
    borrow_record = crud.return_book(db, return_request.user_id, return_request.isbn)
    if not borrow_record:
        raise HTTPException(status_code=404, detail="Borrow record not found or already returned")
    
    return {"message": "Book returned successfully"}