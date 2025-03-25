from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from repository import account as crud
from db.database import get_db

router = APIRouter()


@router.get("/profile/{email}")
async def get_profile(email: str, db: AsyncSession = Depends(get_db)):
  user = await crud.get_user_by_email(db, email)
  if not user:
    raise HTTPException(status_code=404, detail="User not found")

  return JSONResponse(
    status_code=200,
    content={"id": user.id, "email": user.email, "first_name": user.first_name, "last_name": user.last_name}
  )
