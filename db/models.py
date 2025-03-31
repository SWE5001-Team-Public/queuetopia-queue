import datetime
import uuid

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey

from db.base import Base


class StaticTable(Base):
  __tablename__ = 'static'

  key = Column(String(50), primary_key=True, index=True, nullable=False)
  value = Column(String(100), nullable=False)
  type = Column(String(100), nullable=False)


class ReservationTable(Base):
  __tablename__ = "reservation"

  id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
  queue_no = Column(Integer, nullable=False)
  name = Column(String, nullable=False)
  mobile_no = Column(String, nullable=False)
  pax = Column(Integer, nullable=False)
  status = Column(String, ForeignKey("static.key", onupdate="CASCADE"), default="Waiting", nullable=False)
  queue_id = Column(String, nullable=False)
  store_id = Column(String, nullable=False)
  created_at = Column(DateTime, default=datetime.datetime.now(), nullable=False)
  updated_at = Column(DateTime, default=datetime.datetime.now(), nullable=False)
  called_at = Column(DateTime, default=None, nullable=True)
