from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi.requests import Request
#from starlette.exceptions import HTTPException as StarletteHTTPException
import asyncpg


# из проекта
from db import create_pool, close_pool
import db
from schemas import Register, Login, GradePost
from security import hash_password, verify_password
from jwt_handler import create_access_token
from auth import get_user

app = FastAPI()

# <! Event handlers !> #

@app.on_event("startup")
async def startup():
    await create_pool()

@app.on_event("shutdown")
async def shutdown():
    await close_pool()

# <! GET-запросы !> #       (да, я просто теряю время на красивом оформлении комментариев)
@app.get("/")
def root():
    raise HTTPException(
        status_code=204,
        detail="Nothing to do here "
    )

@app.get("/students/me/subjects")
async def get_subjects(current_user = Depends(get_user)):
    
    async with db.pool.acquire() as conn:
        subjects = await conn.fetch(
        """SELECT subjects.id, subjects.name FROM subjects
        JOIN students ON students.class_id = subjects.class_id
        WHERE students.user_id = $1""",
        current_user["id"]
    )
    
    return [dict(row) for row in subjects]

@app.get("/info")
def get_info():
    
    return {
        "name": "Nolejje",
        "version": "alpha 0.2"
    }

@app.get("/students")
async def get_students(student_id: int):
    
    async with db.pool.acquire() as conn:
        students = await conn.fetch("""SELECT users.name FROM students
                            JOIN users ON students.user_id = users.id
                            WHERE students.id = $1""", student_id)
    
    if students is []:
        raise HTTPException(
            status_code=404,
            detail="No students in table :/"
        )
    return [dict(row) for row in students]

@app.get("/users/me")
async def get_current_user(current_user = Depends(get_user)):
    return current_user

@app.get("/students/me")
async def get_current_student(current_user = Depends(get_user)):
    
    async with db.pool.acquire() as conn:
        student = await conn.fetchrow("""
        SELECT * FROM students WHERE user_id = $1""", current_user["id"]
    )
    
    student_id = student["id"]
    class_id = student["class_id"]
    return {"student_id": student_id, "class_id": class_id}

@app.get("/students/me/homeworks")
async def get_homeworks (current_user = Depends(get_user)):
    
    async with db.pool.acquire() as conn:
        
        student = await conn.fetchrow("""
            SELECT * FROM students WHERE user_id = $1
            """,
            current_user["id"]
            )
        
        if not student:
            raise HTTPException(
                status_code=404,
                detail="Student not found :\\"
            )
        
        homeworks = await conn.fetch("""
            SELECT h.id, h.title, h.description, h.due_date FROM subjects
            JOIN homeworks h ON h.subject_id = subjects.id
            WHERE subjects.class_id = $1
            ORDER BY h.due_date ASC;
            """,
            student["class_id"]
            )
    
    return [dict(row) for row in homeworks]

@app.get("/homework")
async def get_homework (subject_id: int, current_user = Depends(get_user)):
    
    async with db.pool.acquire() as conn:
        
        class_id = await conn.fetchrow("""
            SELECT students.class_id FROM students WHERE user_id = $1
            """,
            current_user["id"]
            )
        
        subject_class_id = await conn.fetchrow("""
            SELECT class_id FROM subjects WHERE id = $1 
            """,
            subject_id
            )
        
        if class_id["class_id"] == subject_class_id["class_id"]:
            homework = await conn.fetchrow("""
                SELECT id, title, description, due_date FROM homeworks
                WHERE subject_id = $1
                ORDER BY due_date ASC
            """
            )
        else:
            raise HTTPException(
                status_code=403,
                detail="Forbidden \\:-|"
            )
    
    return homework

# <! POST-запросы!> #

@app.post("/auth/register")
async def register(user: Register):
    
    async with db.pool.acquire() as conn:
        existing_user = await conn.fetchrow(
        "SELECT id FROM users WHERE email = $1", user.email)
        
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="Email already registered"
            )

        password_hash = hash_password(user.password)

        id =await conn.fetchrow(
            """
            INSERT INTO users (name, email, passwd_hash, role)
            VALUES ($1, $2, $3, $4)
            RETURNING id
            """,
            user.name,
            user.email,
            password_hash,
            user.role
        )
        
        user_id = id["id"]
        
        if user.role == 'student':
            await conn.execute("""
                INSERT INTO students (user_id, class_id)
                VALUES ($1, $2)
                """,
                user_id,
                user.class_id
            )
        
        if user.role == 'teacher':
            await conn.execute("""
                INSERT INTO teachers (user_id)
                VALUES ($1)
                """,
                user_id
                )
    
    return {"message": "User created"}

@app.post("/auth/login")
async def login(user: Login):
    
    async with db.pool.acquire() as conn:
        db_user = await conn.fetchrow(
        "SELECT * FROM users WHERE email = $1", user.email
    )
    
    if not db_user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )
    
    if not verify_password(user.password, db_user["passwd_hash"]):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )
    
    token = create_access_token(
        {"user_id": db_user["id"]}
    )
    
    return {"access_token": token}

@app.post("/grades")
async def grades (grades: GradePost, current_user = Depends(get_user)):
    
    if current_user["role"] != "teacher":
        raise HTTPException(
            status_code=403,
            detail="Forbidden :|"
        )
    
    async with db.pool.acquire() as conn:
        await conn.execute(
        """
        INSERT INTO grades (student_id, subject_id, grade)
        VALUES ($1, $2, $3)
        """,
        grades.student_id,
        grades.subject_id,
        grades.grade
    )
    
    return {"status": "Successful"}

# <! Error Handlers !> #        my English is very well)

@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return JSONResponse(
        status_code=404,
        content={"error": "Not Found :("}
    )