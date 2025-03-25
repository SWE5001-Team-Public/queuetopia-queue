from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from db.models import StaticTable


async def get_status(db: AsyncSession):
  """Get all statuses from static table."""
  result = await db.execute(select(StaticTable).filter(StaticTable.type == "Status"))
  return result.scalars().all()
