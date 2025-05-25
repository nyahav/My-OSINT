# app/crud/user.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.db.models.user import User
from app.schemas.user import UserCreate, UserOut 
from typing import Optional, List
from datetime import datetime

# Function to get a user by username
async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
    """
    Retrieves a single user from the database by their username.
    """
    result = await db.execute(select(User).filter(User.username == username))
    return result.scalars().first()

# Function to get a user by ID
async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
    """
    Retrieves a single user from the database by their ID.
    """
    result = await db.execute(select(User).filter(User.id == user_id))
    return result.scalars().first()

# Function to get multiple users (e.g., for an admin view)
async def get_users(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[User]:
    """
    Retrieves a list of users from the database with pagination.
    """
    result = await db.execute(select(User).offset(skip).limit(limit))
    return list(result.scalars().all())

# Function to create a new user
async def create_user(db: AsyncSession, user: UserCreate, hashed_password: str) -> User:
    """
    Creates a new user record in the database.
    """
    # Populate user model from UserCreate schema and hashed_password
    # `is_active` and `is_admin` have defaults in the model, but can be overridden if provided by schema
    # `created_date` and `updated_date` have defaults in the User model
    db_user = User(
        username=user.username,
        hashed_password=hashed_password,
        email=user.email,
        first_name=user.first_name,       # Passed from schema (Optional)
        last_name=user.last_name,         # Passed from schema (Optional)
        is_active=user.is_active,         # Passed from schema (with default)
        created_by=user.username,         # Set creator to the username for initial creation
        updated_by=user.username,         # Set updater to the username for initial creation
    )
    db.add(db_user)
    await db.commit()       # Commit the transaction
    await db.refresh(db_user) # Refresh the instance to load any database-generated values (like 'id', timestamps)
    return db_user

# Function to update an existing user (optional, but good practice)
async def update_user(db: AsyncSession, user_id: int, user_update: UserOut) -> Optional[User]:
    """
    Updates an existing user's details in the database.
    """
    # Using the ORM update feature with await db.execute
    # This directly updates without loading the object first, which can be more efficient
    stmt = (
        update(User)
        .where(User.id == user_id)
        .values(
            **user_update.model_dump(exclude_unset=True), # Use model_dump for Pydantic v2
            updated_date=datetime.now() # Manually update timestamp
        )
    )
    await db.execute(stmt)
    await db.commit()
    # After update, fetch the updated user to return it
    return await get_user_by_id(db, user_id)

# Function to delete a user (optional)
async def delete_user(db: AsyncSession, user_id: int) -> bool:
    """
    Deletes a user from the database by their ID.
    """
    user = await get_user_by_id(db, user_id)
    if user:
        await db.delete(user)
        await db.commit()
        return True
    return False