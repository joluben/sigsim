"""
API dependencies
"""
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db


def get_current_user():
    """Get current authenticated user (placeholder for future implementation)"""
    # TODO: Implement authentication
    return {"id": "default-user", "username": "default"}


def get_db_session(db: Session = Depends(get_db)) -> Session:
    """Get database session dependency"""
    return db