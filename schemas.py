import datetime

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
