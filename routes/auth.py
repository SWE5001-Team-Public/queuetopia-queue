from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

import schemas
from repository import account as crud
from db.database import get_db

router = APIRouter()


@router.post("/register")
async def register(user: schemas.User, db: AsyncSession = Depends(get_db)):
  existing_user = await crud.get_user_by_email(db, user.email)
  if existing_user:
    raise HTTPException(status_code=400, detail="User already exists")

  new_user = await crud.create_user(db, user)
  return JSONResponse(
    status_code=201,
    content={"message": "User registered successfully", "user": new_user.email}
  )


@router.post("/login")
async def login(login_data: schemas.LoginRequest, db: AsyncSession = Depends(get_db)):
  user = await crud.get_user_by_email(db, login_data.email)
  if user and user.password == login_data.password:
    return JSONResponse(
      status_code=200,
      content={"message": "Login successful", "user": user.email}
    )
  raise HTTPException(status_code=401, detail="Invalid credentials")
