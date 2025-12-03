"""

Authenfication router

"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from fastapi import APIRouter, Depends, HTTPException
from datetime import timedelta, timezone, datetime
from pydantic import BaseModel, Field
from passlib.context import CryptContext
from typing import Annotated
from starlette import status
from jose import jwt, JWTError
from fastapi.security import (OAuth2PasswordRequestForm, OAuth2PasswordBearer)
from ..models import User
from ..schemas import UserSchema, TokenData
from ..database import db_dependency, get_db
from ..config import SECRET_KEY, ALGORITHM


router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

bcrypt_context = CryptContext(
    schemes=['bcrypt'], 
    deprecated = 'auto'
)
oauth2_brearer = OAuth2PasswordBearer(
    tokenUrl="auth/token"
)

class CreteUserRequest(BaseModel):
    username: str = Field(min_length=2, max_length=30)
    first_name: str = Field(min_length=2, max_length=30)
    last_name: str = Field(min_length=2, max_length=30)
    email: str
    password: str = Field(min_length=3, max_length=30)
    role: str 

class Token(BaseModel):
    access_token: str
    token_type: str

async def authenticate_user(
        username: str,
        password: str,
        db : AsyncSession = Depends(get_db)
):
    stmt = select(User).where(User.username == username)
    result = await db.execute(statement=stmt)
    user = result.scalar_one_or_none()
    if user is None:
        return False
    user_dto = UserSchema.model_validate(user)
    if not bcrypt_context.verify(password, user_dto.hashed_password):
        return False
    return user_dto

def crate_access_token (
        username: str,
        user_id: int, 
        role: str,
        expires_delta: timedelta
):
    expires = datetime.now(timezone.utc) + expires_delta
    encode = {'sub': username, 'id': user_id, 'role': role, 'exp': expires}
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: Annotated[str, Depends(oauth2_brearer)])-> TokenData:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get('sub')
        user_id = payload.get('id')
        user_role = payload.get('role')

        if username is None or user_id is None or user_role is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail= "Could not validate user."
                )
        return TokenData(id=user_id, username=username, role=user_role)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Could not validate user."
            )
    
@router.post("/", status_code=status.HTTP_201_CREATED) 
async def create_user (
    db: db_dependency,
    create_user_request: CreteUserRequest
):
    new_user = User(
        email = create_user_request.email,
        username = create_user_request.username,
        first_name = create_user_request.first_name,
        last_name = create_user_request.last_name,
        role = create_user_request.role,
        hashed_password = bcrypt_context.hash(create_user_request.password)
    )
    
    db.add(new_user)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this username or email already exists"
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code= status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail= "Something went wrong"
        )
    return {"status": "User created successfully"}


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm,Depends()],
    db: db_dependency    
):
    user = await authenticate_user(
        form_data.username,
        form_data.password,
        db
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Could not validate user."
        )
    token = crate_access_token(
        user.username,
        user.id,
        user.role,
        timedelta(hours=1)
    )
    return{'access_token':token, 'token_type': 'bearer'}