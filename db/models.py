from sqlalchemy import Column, String, Integer, Sequence, Boolean
import uuid

from sqlalchemy.ext.hybrid import hybrid_property

from db.database import Base


class UserTable(Base):
  __tablename__ = "users"

  id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
  u_id = Column(Integer, Sequence('user_u_id_seq'), index=True, autoincrement=True, nullable=False)
  email = Column(String, unique=True, index=True, nullable=False)
  first_name = Column(String, nullable=False)
  last_name = Column(String, nullable=False)
  password = Column(String, nullable=False)
  deactivated = Column(Boolean, default=False)

  @hybrid_property
  def display_id(self):
    return f"U{self.u_id}"
