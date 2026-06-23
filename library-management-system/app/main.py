from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime
import pandas as pd
import os

from .database import SessionLocal, engine, Base
from . import models, schemas, crud, auth
from .routes import books, users, borrow, return_router, reports

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Library Management System", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Include routers
app.include_router(books.router, prefix="/books", tags=["Books"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(borrow.router, prefix="/borrow", tags=["Borrow"])
app.include_router(return_router.router, prefix="/return", tags=["Return"])
app.include_router(reports.router, prefix="/reports", tags=["Reports"])

@app.on_event("startup")
def load_initial_data():
    db = SessionLocal()
    # Check if books exist
    if db.query(models.Book).count() == 0:
        csv_path = "data/books.csv"
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            for _, row in df.iterrows():
                try:
                    book = models.Book(
                        isbn=str(row.get('isbn', '')),
                        title=str(row.get('title', 'Unknown')),
                        author=str(row.get('authors', 'Unknown')),
                        publisher=str(row.get('publisher', 'Unknown')),
                        publication_year=int(row.get('published_year', 2000)),
                        available_copies=1
                    )
                    db.add(book)
                except:
                    continue
            db.commit()
    db.close()

@app.get("/")
def root():
    return {
        "message": "Library Management System API",
        "docs": "/docs",
        "version": "1.0.0"
    }

@app.post("/auth/register", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_user(db, user)

@app.post("/auth/login")
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, user.username)
    if not db_user or not auth.verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = auth.create_access_token({"sub": db_user.username})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user_id": db_user.id,
        "role": db_user.role
    }