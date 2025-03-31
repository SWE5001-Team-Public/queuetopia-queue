from datetime import datetime

from pydantic import BaseModel
from humps import camelize


def to_camel(string: str) -> str:
  return camelize(string)


class ConfigResponse(BaseModel):
  key: str
  value: str


class CreateReservation(BaseModel):
  name: str
  mobile_no: str
  pax: int
  queue_id: str
  store_id: str


class ReservationResponse(BaseModel):
  id: str
  queue_no: int
  name: str
  mobile_no: str
  pax: int
  status: str
  queue_id: str
  store_id: str
  created_at: datetime
  updated_at: datetime

  class Config:
    alias_generator = to_camel
    populate_by_name = True
    from_attributes = True


class ModifyReservationStatus(BaseModel):
  id: str
  status: str
