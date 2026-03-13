from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi.requests import Request
#from starlette.exceptions import HTTPException as StarletteHTTPException
import asyncpg


# из проекта
from db import db_url
from schemas import register, login
from security import hash_password, verify_password
from jwt_handler import create_access_token
from auth import get_user

app = FastAPI()

# <! GET-запросы !> #       (да, я просто теряю время на красивом оформлении комментариев)
@app.get("/")
def root():
    raise HTTPException(
        status_code=204,
        detail="Nothing to do here "
    )

@app.get("/subjects")
def get_subjects():
    return {"message": "В разработке..."}

@app.get("/info")
def get_info():
    return {
        "name": "Nolejje",
        "version": "alpha 0.2"
    }

@app.get("/students")
async def get_students(student_id: int):
    
    conn = await asyncpg.connect(db_url)
    
    rows = await conn.fetch("""SELECT users.name FROM students
                            JOIN users ON students.user_id = users.id
                            WHERE students.id = $1""", student_id)
    
    await conn.close()
    
    
    if rows is None:
        raise HTTPException(
            status_code=404,
            detail="No students in table :/"
        )
    return [dict(row) for row in rows]

@app.get("/users/me")
async def get_current_user(current_user = Depends(get_user)):
    return current_user

@app.get("/students/me")
async def get_current_student(current_user = Depends(get_user)):
    conn = await asyncpg.connect(db_url)
    rows = await conn.fetchrow("""
        SELECT * FROM students WHERE user_id = $1""", current_user["id"]
    )
    await conn.close()
    student_id = rows["id"]
    class_id = rows["class_id"]
    return {"student_id": student_id, "class_id": class_id}

# <! POST-запросы!> #

@app.post("/auth/register")
async def register(user: register):
    
    conn = await asyncpg.connect(db_url)
    
    existing_user = await conn.fetchrow(
        "SELECT id FROM users WHERE email = $1", user.email)
    
    if existing_user:
        await conn.close()
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    password_hash = hash_password(user.password)
    
    await conn.execute(
        """
        INSERT INTO users (name, email, passwd_hash, role)
        VALUES ($1, $2, $3, $4)
        """,
        user.name,
        user.email,
        password_hash,
        user.role
    )
    
    await conn.close()
    
    return {"message": "User created"}

@app.post("/auth/login")
async def login(user: login):
    
    conn = await asyncpg.connect(db_url)
    
    db_user = await conn.fetchrow(
        "SELECT * FROM users WHERE email = $1", user.email
    )
    
    await conn.close()
    
    if not db_user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )
    
    if not verify_password:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )
    
    token = create_access_token(
        {"user_id": db_user["id"]}
    )
    
    return {"access_token": token}

@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return JSONResponse(
        status_code=404,
        content={"error": "Not Found :("}
    )