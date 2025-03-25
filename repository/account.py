from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from schemas import User
from db.models import UserTable


async def create_user(db: AsyncSession, user: User):
  db_user = UserTable(
    email=user.email,
    first_name=user.first_name,
    last_name=user.last_name,
    password=user.password
  )
  db.add(db_user)
  await db.commit()
  await db.refresh(db_user)
  return db_user


async def get_user_by_email(db: AsyncSession, email: str):
  """Retrieve a user by email."""
  result = await db.execute(select(UserTable).filter(UserTable.email == email, UserTable.deactivated == False))
  return result.scalar_one_or_none()
