from datetime import datetime

from pydantic import BaseModel
from humps import camelize


def to_camel(string: str) -> str:
  return camelize(string)


class ConfigResponse(BaseModel):
  key: str
  value: str


class CreateQueueEntry(BaseModel):
  name: str
  mobile_no: str
  pax: int
  store_id: str


class QueueEntryResponse(BaseModel):
  id: str
  queue_no: int
  name: str
  mobile_no: str
  pax: int
  status: str
  store_id: str
  created_at: datetime
  updated_at: datetime

  class Config:
    alias_generator = to_camel
    populate_by_name = True
    from_attributes = True
