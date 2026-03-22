from typing import Optional
from pydantic import BaseModel

class Register(BaseModel):
  name: str
  email: str
  password: str
  role: str
  class_id: Optional[int]

class Login(BaseModel):
  email: str
  password: str

class GradePost(BaseModel):
  student_id: int
  subject_id: int
  grade: int