from pydantic import BaseModel,Field


class Signup(BaseModel):
    first_name: str = Field(...)
    last_name: str = Field(...)
    email: str = Field(...)
    phone_number: str = Field(...)
    password: str = Field(...)
