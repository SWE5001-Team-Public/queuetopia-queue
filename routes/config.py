from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

import schemas
from db.database import get_db
from repository import static as crud

router = APIRouter()


@router.get("/status", response_model=list[schemas.ConfigResponse])
async def get_status(db: AsyncSession = Depends(get_db)):
  """Retrieve a list of statuses"""
  queue_status = await crud.get_status(db)

  if not queue_status:
    raise HTTPException(status_code=404, detail="Static statuses not found")

  return queue_status
