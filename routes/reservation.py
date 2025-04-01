from fastapi import APIRouter, Depends, HTTPException
from fastapi.params import Query
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
      raise HTTPException(status_code=404, detail="Reservation not found")

    return reservation

  except Exception as e:
    await db.rollback()
    raise HTTPException(status_code=500, detail=f"Failed to get reservation details: {str(e)}")


@router.get("/waiting-time/{queueId}", response_model=float)
async def get_waiting_time(queueId: str, db: AsyncSession = Depends(get_db)):
  """Calculate waiting time for a queue by rolling up the last n reservations"""
  try:
    reservations = await crud.get_last_n_reservations(db, queueId)

    total_waiting_time = sum(
      (reservation.called_at - reservation.created_at).total_seconds() for reservation in reservations)

    if len(reservations) == 0:
      return 0.0

    return total_waiting_time / len(reservations)

  except Exception as e:
    await db.rollback()
    raise HTTPException(status_code=500, detail=f"Failed to get reservation details: {str(e)}")


@router.post("/status/edit")
async def edit_reservation_status(queue: schemas.ModifyReservationStatus, db: AsyncSession = Depends(get_db)):
  if queue.status == "Called":
    updated_reservation = await crud.call_reservation(db, queue.id)
  else:
    updated_reservation = await crud.edit_reservation_status(db, queue)

  if updated_reservation is None:
    raise HTTPException(status_code=404, detail="Reservation details not found")

  return JSONResponse(
    status_code=200,
    content={"message": "Reservation status updated successfully", "id": updated_reservation.id,
             "queueId": updated_reservation.queue_id, "status": updated_reservation.status}
  )


@router.get("/wait-list/{queueId}", response_model=list[schemas.ReservationResponse])
async def get_reservations_by_status(
  queueId: str,
  status: str = Query(default="Waiting"),
  db: AsyncSession = Depends(get_db)
):
  """
  Get reservations filtered by status for a specific queue.

  - queueId: The ID of the queue
  - status: List of statuses to filter by (defaults to ["Waiting"])
  """
  try:
    reservations = await crud.get_reservations_filter_status(db, queueId, status)

    if not reservations:
      return []

    return reservations

  except Exception as e:
    await db.rollback()
    raise HTTPException(
      status_code=500,
      detail=f"Failed to retrieve reservations: {str(e)}"
    )
