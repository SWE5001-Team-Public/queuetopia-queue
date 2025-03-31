import datetime
import logging

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from config import setup_logging
from db.models import ReservationTable
from schemas import CreateReservation, ModifyReservationStatus

setup_logging()

logger = logging.getLogger(__name__)


async def create_reservation(db: AsyncSession, queue: CreateReservation):
  try:
    today = datetime.datetime.now()
    latest_queue = await db.execute(
      select(func.max(ReservationTable.queue_no))
      .filter(func.date(ReservationTable.created_at) == today.date())
    )
    latest_number = latest_queue.scalar() or 0

    db_store = ReservationTable(
      store_id=queue.store_id,
      name=queue.name,
      mobile_no=queue.mobile_no,
      pax=queue.pax,
      queue_id=queue.queue_id,
      queue_no=latest_number + 1,
    )
    db.add(db_store)
    await db.commit()
    await db.refresh(db_store)
    return db_store

  except Exception as e:
    await db.rollback()
    logger.error(e)


async def get_reservation(db: AsyncSession, id: str):
  try:
    db_queue = await db.execute(
      select(ReservationTable).filter(ReservationTable.id == id)
    )
    return db_queue.scalar()

  except Exception as e:
    await db.rollback()
    logger.error(e)


async def edit_reservation_status(db: AsyncSession, queue: ModifyReservationStatus):
  """Edit reservation status by its ID."""
  result = await db.execute(select(ReservationTable).filter(ReservationTable.id == queue.id))
  db_queue = result.scalars().first()

  if db_queue is None:
    return None

  db_queue.status = queue.status
  db_queue.updated_at = datetime.datetime.now()

  await db.commit()
  await db.refresh(db_queue)

  return db_queue


async def call_reservation(db: AsyncSession, id: str):
  """Edit reservation status to "Called" by its ID."""
  result = await db.execute(select(ReservationTable).filter(ReservationTable.id == id))
  db_queue = result.scalars().first()

  if db_queue is None:
    return None

  db_queue.status = "Called"
  db_queue.updated_at = datetime.datetime.now()
  db_queue.called_at = datetime.datetime.now()

  await db.commit()
  await db.refresh(db_queue)

  return db_queue
