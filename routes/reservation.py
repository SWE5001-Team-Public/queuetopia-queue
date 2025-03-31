from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import get_db
from repository import reservation as crud
import schemas

router = APIRouter()


@router.post("/join")
async def create_reservation(request: schemas.CreateReservation, db: AsyncSession = Depends(get_db)):
  try:
    new_queue = await crud.create_reservation(db, request)

    if not new_queue:
      raise HTTPException(status_code=400, detail=f"Failed to create reservation")

    return JSONResponse(
      status_code=201,
      content={"id": new_queue.id, "queue_no": new_queue.queue_no, "store_id": new_queue.store_id}
    )

  except Exception as e:
    await db.rollback()
    raise HTTPException(status_code=500, detail=f"Failed to create reservation: {str(e)}")


@router.get("/status/{id}", response_model=schemas.ReservationResponse)
async def get_reservation(id: str, db: AsyncSession = Depends(get_db)):
  try:
    reservation = await crud.get_reservation(db, id)

    if not reservation:
      raise HTTPException(status_code=404, detail="Queue not found")

    return reservation

  except Exception as e:
    await db.rollback()
    raise HTTPException(status_code=500, detail=f"Failed to get reservation details: {str(e)}")


@router.post("/status/edit")
async def edit_reservation_status(queue: schemas.ModifyReservationStatus, db: AsyncSession = Depends(get_db)):
  updated_reservation = await crud.edit_reservation_status(db, queue)

  if updated_reservation is None:
    raise HTTPException(status_code=404, detail="Reservation details not found")

  return JSONResponse(
    status_code=200,
    content={"message": "Reservation status updated successfully", "id": updated_reservation.id,
             "queueId": updated_reservation.queue_id, "status": updated_reservation.status}
  )
