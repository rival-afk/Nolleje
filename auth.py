from jose import jwt
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from jwt_handler import SECRET_KEY, ALGORITHM
from db import db_url
import asyncpg

auth_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

async def get_user (token = Depends(auth_scheme)):
  decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
  user_id = decoded_token["user_id"]
  conn = await asyncpg.connect(db_url)
  rows = await conn.fetchrow("""
    SELECT * FROM users WHERE id = $1""",
    user_id)
  if not rows:
    raise HTTPException(
      status_code=401,
      detail="Invalid token"
    )
  await conn.close()
  return rows