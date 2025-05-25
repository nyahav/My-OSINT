from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession # <--- Changed import to AsyncSession
from app.crud.user import get_user_by_username, create_user
from app.schemas.user import UserCreate, UserOut
from app.utilities.auth_utils import get_password_hash, verify_password
from app.utilities.logger import logger
from app.db.session import get_db

router = APIRouter()

@router.post("/register", response_model=UserOut)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)): 
    logger.info("Received registration request for username: %s", user.username)
    db_user = await get_user_by_username(db, user.username)
    if db_user:
        logger.warning("Username already exists: %s", user.username)
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = get_password_hash(user.password)
    logger.info("User created successfully: %s", user.username)
    return await create_user(db, user, hashed_password=hashed_password)

@router.post("/login", response_model=UserOut)
async def login(user: UserCreate, db: AsyncSession = Depends(get_db)): 
    db_user = await get_user_by_username(db, user.username)
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    return db_user