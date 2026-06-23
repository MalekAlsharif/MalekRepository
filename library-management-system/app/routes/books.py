from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from ..database import SessionLocal
from .. import crud, schemas, auth

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=List[schemas.BookResponse])
def get_books(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    if search:
        return crud.search_books(db, search)
    return crud.get_books(db, skip=skip, limit=limit)

@router.get("/{isbn}", response_model=schemas.BookResponse)
def get_book(isbn: str, db: Session = Depends(get_db)):
    book = crud.get_book(db, isbn)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

@router.post("/", response_model=schemas.BookResponse)
def create_book(
    book: schemas.BookCreate,
    db: Session = Depends(get_db),
    current_user = Depends(auth.get_current_librarian)
):
    existing = crud.get_book(db, book.isbn)
    if existing:
        raise HTTPException(status_code=400, detail="Book already exists")
    return crud.create_book(db, book)

@router.put("/{isbn}", response_model=schemas.BookResponse)
def update_book(
    isbn: str,
    book_update: schemas.BookUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(auth.get_current_librarian)
):
    book = crud.update_book(db, isbn, book_update)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

@router.delete("/{isbn}")
def delete_book(
    isbn: str,
    db: Session = Depends(get_db),
    current_user = Depends(auth.get_current_admin)
):
    if not crud.delete_book(db, isbn):
        raise HTTPException(status_code=404, detail="Book not found")
    return {"message": "Book deleted successfully"}