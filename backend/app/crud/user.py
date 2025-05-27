
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.db.models.user import User
from app.schemas.user import UserCreate, UserOut 
from typing import Optional, List
from datetime import datetime

async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
    """
    Retrieves a single user from the database by their username.
    """
    result = await db.execute(select(User).filter(User.username == username))
    return result.scalars().first()

async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
    """
    Retrieves a single user from the database by their ID.
    """
    result = await db.execute(select(User).filter(User.id == user_id))
    return result.scalars().first()

async def get_users(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[User]:
    """
    Retrieves a list of users from the database with pagination.
    """
    result = await db.execute(select(User).offset(skip).limit(limit))
    return list(result.scalars().all())

async def create_user(db: AsyncSession, user: UserCreate, hashed_password: str) -> User:
    """
    Creates a new user record in the database.
    """
  
    db_user = User(
        username=user.username,
        hashed_password=hashed_password,
        email=user.email,
        is_active=user.is_active,        
        created_by=user.username,        
        updated_by=user.username,         
    )
    db.add(db_user)
    await db.commit()       
    await db.refresh(db_user) 
    return db_user


async def update_user(db: AsyncSession, user_id: int, user_update: UserOut) -> Optional[User]:
    """
    Updates an existing user's details in the database.
    """
 
    stmt = (
        update(User)
        .where(User.id == user_id)
        .values(
            **user_update.model_dump(exclude_unset=True), 
            updated_date=datetime.now() 
        )
    )
    await db.execute(stmt)
    await db.commit()
   
    return await get_user_by_id(db, user_id)


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

async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    result = await db.execute(select(User).filter(User.email == email))
    return result.scalars().first()