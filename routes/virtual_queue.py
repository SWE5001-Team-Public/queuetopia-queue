from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import get_db
from repository import virtual_queue as crud
import schemas

router = APIRouter()


@router.post("/join")
async def create_queue_entry(request: schemas.CreateQueueEntry, db: AsyncSession = Depends(get_db)):
  try:
    new_queue = await crud.create_queue_entry(db, request)

    if not new_queue:
      raise HTTPException(status_code=400, detail=f"Failed to join virtual queue")

    return JSONResponse(
      status_code=201,
      content={"id": new_queue.id, "queue_no": new_queue.queue_no, "store_id": new_queue.store_id}
    )

  except Exception as e:
    await db.rollback()
    raise HTTPException(status_code=500, detail=f"Failed to create virtual queue entry: {str(e)}")


@router.get("/status/{id}", response_model=schemas.QueueEntryResponse)
async def get_queue_entry(id: str, db: AsyncSession = Depends(get_db)):
  try:
    queue_entry = await crud.get_queue_entry(db, id)

    if not queue_entry:
      raise HTTPException(status_code=404, detail="Queue not found")

    return queue_entry

  except Exception as e:
    await db.rollback()
    raise HTTPException(status_code=500, detail=f"Failed to get virtual queue entry: {str(e)}")
