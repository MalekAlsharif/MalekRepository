from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    LIBRARIAN = "librarian"
    STUDENT = "student"

# User Schemas
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: Optional[UserRole] = UserRole.STUDENT

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# Book Schemas
class BookCreate(BaseModel):
    isbn: str
    title: str
    author: str
    publisher: str
    publication_year: int
    available_copies: int = 1

class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    publisher: Optional[str] = None
    publication_year: Optional[int] = None
    available_copies: Optional[int] = None

class BookResponse(BaseModel):
    isbn: str
    title: str
    author: str
    publisher: str
    publication_year: int
    available_copies: int
    status: str
    
    class Config:
        from_attributes = True

# Borrow Schemas
class BorrowRequest(BaseModel):
    user_id: int
    isbn: str

class ReturnRequest(BaseModel):
    user_id: int
    isbn: str

class BorrowResponse(BaseModel):
    id: int
    user_id: int
    isbn: str
    borrow_date: datetime
    due_date: datetime
    return_date: Optional[datetime]
    status: str
    
    class Config:
        from_attributes = True

# Reservation Schemas
class ReservationRequest(BaseModel):
    user_id: int
    isbn: str

class ReservationResponse(BaseModel):
    id: int
    user_id: int
    isbn: str
    reservation_date: datetime
    status: str
    
    class Config:
        from_attributes = True

# Report Schemas
class ReportResponse(BaseModel):
    report_type: str
    data: List[dict]