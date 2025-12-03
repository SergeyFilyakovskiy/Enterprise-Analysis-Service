from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from starlette import status
from ..database import get_db
from ..models import User, UserRole
from ..schemas import UserResponse, ChangePasswordRequest, UpdateProfileRequest, UpdateRoleRequest, TokenData
from .auth import get_current_user, bcrypt_context

router = APIRouter(
    prefix="/users", 
    tags=["users"]
)

# ==========================================
# 1. Получить свой профиль
# ==========================================
@router.get("/me", response_model=UserResponse)
async def read_user_profile(
    db: AsyncSession = Depends(get_db),
    token_data: TokenData = Depends(get_current_user)
):

    result = await db.execute(select(User).where(User.id == token_data.id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="User not found")
        
    return user

# ==========================================
# 2. Изменить данные профиля
# ==========================================
@router.put("/edit", response_model=UserResponse)
async def update_user_profile(
    update_data: UpdateProfileRequest,
    db: AsyncSession = Depends(get_db),
    token_data: TokenData = Depends(get_current_user)
):

    result = await db.execute(select(User).where(User.id == token_data.id))
    user_in_db = result.scalar_one_or_none()
    
    if not user_in_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="User not found"
        )

    if update_data.email != user_in_db.email:
        email_check = await db.execute(select(User).where(User.email == update_data.email))
        if email_check.scalar_one_or_none():
             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                                 detail="Email already registered")
        user_in_db.email = update_data.email

    # 3. Обновление полей
    if update_data.first_name is not None:
        user_in_db.first_name = update_data.first_name
    
    if update_data.last_name is not None:
        user_in_db.last_name = update_data.last_name

    db.add(user_in_db)
    await db.commit()
    await db.refresh(user_in_db)
    return user_in_db

# ==========================================
# 3. Изменить пароль
# ==========================================
@router.put("/password", status_code=status.HTTP_200_OK)
async def change_password(
    password_data: ChangePasswordRequest,
    db: AsyncSession = Depends(get_db),
    token_data: TokenData = Depends(get_current_user)
):
 
    result = await db.execute(select(User).where(User.id == token_data.id))
    user_in_db = result.scalar_one_or_none()

    if not user_in_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="User not found")

    if not bcrypt_context.verify(password_data.old_password, 
                                 user_in_db.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="Invalid old password")
    
    user_in_db.hashed_password = bcrypt_context.hash(password_data.new_password)
    
    db.add(user_in_db)
    await db.commit()
    
    return {"message": "Password updated successfully"}

# ==========================================
# 4. Изменить роль (ТОЛЬКО АДМИН)
# ==========================================
@router.put("/{user_id}/role", response_model=UserResponse)
async def change_user_role(
    user_id: int,
    role_data: UpdateRoleRequest,
    db: AsyncSession = Depends(get_db),
    token_data: TokenData = Depends(get_current_user)
):

    if token_data.role != "admin": 
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail="Not authorized to change roles")

    result = await db.execute(select(User).where(User.id == user_id))
    target_user = result.scalar_one_or_none()
    
    if not target_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="User not found")

    target_user.role = role_data.role
    
    db.add(target_user)
    await db.commit()
    await db.refresh(target_user)
    
    return target_user

# ==========================================
# 5. Удалить аккаунт
# ==========================================
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    token_data: TokenData = Depends(get_current_user)
):

    if token_data.id != user_id and token_data.role != "admin":
         raise HTTPException(status_code=403,
                              detail="Not authorized to delete this user")

    result = await db.execute(select(User).where(User.id == user_id))
    user_to_delete = result.scalar_one_or_none()

    if not user_to_delete:
        raise HTTPException(status_code=404, 
                            detail="User not found")

    await db.delete(user_to_delete)
    await db.commit()