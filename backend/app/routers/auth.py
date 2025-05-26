from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.user import UserCreate, UserLogin, UserOut
from app.crud.user import get_user_by_username, create_user, get_user_by_email
from app.utilities.auth_utils import get_password_hash, verify_password, create_access_token, get_current_user
from app.utilities.logger import logger
from app.db.session import get_db
from fastapi.responses import JSONResponse

router = APIRouter()


@router.post("/register", response_model=UserOut)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    logger.info("Registration attempt: %s", user.username)

    # Check for duplicate username or email
    existing_user = await get_user_by_username(db, user.username)
    existing_email = await get_user_by_email(db, user.email)
    if existing_user or existing_email:
        if existing_user:
            logger.warning("Username already exists: %s", user.username)
            raise HTTPException(status_code=400, detail="Username already registered")
        if existing_email:
            logger.warning("Email already exists: %s", user.email)
            raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = get_password_hash(user.password)
    new_user = await create_user(db, user, hashed_password=hashed_password)
    logger.info("User created: %s", new_user.username)
    token_data = {"sub": new_user.username}
    token = create_access_token(token_data)
    logger.info("Registration successful, token created for user: %s", new_user.username)
    logger.debug("Token data: %s", token)
    return JSONResponse(content={"access_token": token, "token_type": "bearer"})


@router.post("/login")
async def login(user: UserLogin, db: AsyncSession = Depends(get_db)):
    db_user = await get_user_by_username(db, user.username)
    if not db_user:
        logger.warning("Login failed - user not found: %s", user.username)
        raise HTTPException(status_code=401, detail="Invalid username or password")

    if not verify_password(user.password, db_user.hashed_password):
        logger.warning("Login failed - bad password: %s", user.username)
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token_data = {"sub": db_user.username}
    token = create_access_token(token_data)
    logger.info("Login successful: %s", db_user.username)

    return JSONResponse(content={"access_token": token, "token_type": "bearer"})


@router.get("/me", response_model=UserOut)
async def read_users_me(current_user: UserOut = Depends(get_current_user)):
    return current_user
