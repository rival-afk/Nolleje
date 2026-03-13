from pydantic import BaseModel

class register(BaseModel):
  name: str
  email: str
  password: str
  role: str