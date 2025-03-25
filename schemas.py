from pydantic import BaseModel
from humps import camelize


def to_camel(string: str) -> str:
  return camelize(string)


class User(BaseModel):
  email: str
  first_name: str
  last_name: str
  password: str

  class Config:
    alias_generator = to_camel
    populate_by_name = True  # Allows using both snake_case and camelCase
    from_attributes = True  # Needed for ORM models


class LoginRequest(BaseModel):
  email: str
  password: str
