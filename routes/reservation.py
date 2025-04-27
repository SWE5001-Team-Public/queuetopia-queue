import asyncio
import logging
import os

import httpx
from fastapi import APIRouter, Depends, HTTPException
from fastapi.params import Query
from fastapi.responses import JSONResponse
from httpx import AsyncClient, RequestError, HTTPStatusError
from sqlalchemy.ext.asyncio import AsyncSession

import schemas
from config import load_environment, setup_logging
from db.database import get_db
from repository import reservation as crud

load_environment()
NOTIFICATION_URL = os.getenv("NOTIFICATION_URL")

router = APIRouter()

setup_logging()

logger = logging.getLogger(__name__)


async def send_notification(to: str, body: str):
  notification_data = {"to": to, "body": body}

  async with AsyncClient(timeout=10) as client:
    # 1) Try WhatsApp with up to 3 attempts + exponential backoff
    for i in range(3):
      try:
        resp = await client.post(f"{NOTIFICATION_URL}/send-whatsapp/", json=notification_data)
        resp.raise_for_status()
        return  # success
      except (RequestError, HTTPStatusError) as wa_err:
        if i < 2:
          await asyncio.sleep(0.5 * 2 ** i)
        else:
          last_wa_error = wa_err

    # 2) Fallback to SMS with the same retry logic
    for i in range(3):
      try:
        resp = await client.post(f"{NOTIFICATION_URL}/send-sms/", json=notification_data)
        resp.raise_for_status()
        return  # success
      except (RequestError, HTTPStatusError) as sms_err:
        if i < 2:
          await asyncio.sleep(0.5 * 2 ** i)
        else:
          last_sms_error = sms_err

    # 3) If both completely fail, raise a 502
    logger.error(msg={
      "message": "Both WhatsApp and SMS notifications failed.",
      "whatsapp_error": str(last_wa_error),
      "sms_error": str(last_sms_error),
    })


@router.post("/join")
async def create_reservation(request: schemas.CreateReservation, db: AsyncSession = Depends(get_db)):
  try:
    new_queue = await crud.create_reservation(db, request)

    if not new_queue:
      raise HTTPException(status_code=400, detail=f"Failed to create reservation")

    await send_notification(
      to=f"+65{request.mobile_no}",
      body=f"Hi {request.name}, your reservation is confirmed! Queue No: {new_queue.queue_no}"
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
    reservation = await crud.get_reservation(db, queue.id)
    if reservation is None:
      raise HTTPException(status_code=404, detail="Reservation not found")

    updated_reservation = await crud.call_reservation(db, queue.id)
    await send_notification(
      to=f"+65{reservation.mobile_no}",
      body=f"Hi {reservation.name}, your turn is up! Please proceed to the counter."
    )
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
