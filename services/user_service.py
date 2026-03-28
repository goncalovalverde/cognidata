"""
User service for managing users and authentication
"""

from passlib.context import CryptContext
from database.connection import SessionLocal
from models import User, UserRole

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_user(username: str) -> User:
    """Get a user by username"""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == username).first()
        return user
    finally:
        db.close()


def create_user(username: str, password: str, full_name: str, role: UserRole) -> User:
    """Create a new user"""
    db = SessionLocal()
    try:
        # Check if user already exists
        existing = db.query(User).filter(User.username == username).first()
        if existing:
            raise ValueError(f"User {username} already exists")

        user = User(
            username=username,
            password_hash=hash_password(password),
            full_name=full_name,
            role=role,
            is_active=True
        )
        db.add(user)
        db.commit()
        return user
    finally:
        db.close()


def update_user(username: str, full_name: str = None, role: UserRole = None) -> User:
    """Update user details"""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == username).first()
        if not user:
            raise ValueError(f"User {username} not found")

        if full_name is not None:
            user.full_name = full_name
        if role is not None:
            user.role = role

        db.commit()
        return user
    finally:
        db.close()


def delete_user(username: str) -> bool:
    """Delete a user"""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == username).first()
        if not user:
            raise ValueError(f"User {username} not found")

        db.delete(user)
        db.commit()
        return True
    finally:
        db.close()


def get_all_users() -> list:
    """Get all users"""
    db = SessionLocal()
    try:
        users = db.query(User).order_by(User.username).all()
        return users
    finally:
        db.close()


def change_password(username: str, new_password: str) -> bool:
    """Change a user's password"""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == username).first()
        if not user:
            raise ValueError(f"User {username} not found")

        user.password_hash = hash_password(new_password)
        db.commit()
        return True
    finally:
        db.close()


def authenticate_user(username: str, password: str) -> User:
    """Authenticate a user with username and password"""
    user = get_user(username)
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    if not user.is_active:
        return None
    return user
