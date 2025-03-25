import datetime
import logging

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from config import setup_logging
from db.models import VirtualQueueTable
from schemas import CreateQueueEntry

setup_logging()

logger = logging.getLogger(__name__)


async def create_queue_entry(db: AsyncSession, queue: CreateQueueEntry):
  try:
    today = datetime.datetime.now()
    latest_queue = await db.execute(
      select(func.max(VirtualQueueTable.queue_no))
      .filter(func.date(VirtualQueueTable.created_at) == today.date())
    )
    latest_number = latest_queue.scalar() or 0

    db_store = VirtualQueueTable(
      store_id=queue.store_id,
      name=queue.name,
      mobile_no=queue.mobile_no,
      pax=queue.pax,
      queue_no=latest_number + 1,
    )
    db.add(db_store)
    await db.commit()
    await db.refresh(db_store)
    return db_store

  except Exception as e:
    await db.rollback()
    logger.error(e)

