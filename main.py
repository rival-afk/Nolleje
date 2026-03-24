from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from fastapi.middleware.cors import CORSMiddleware
#from starlette.exceptions import HTTPException as StarletteHTTPException
import time

# из проекта
from db import create_pool, close_pool
import db
from schemas import Register, Login, GradePost
from security import hash_password, verify_password
from jwt_handler import create_access_token
from auth import get_user

app = FastAPI()

# <! Middlewares !> #       (пока можно все. добавляю только ради обхода CORS)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# <! Functions !> #         (для функций не связанных с эндпоинтами)

async def get_current_student(current_user=Depends(get_user)):
    async with db.pool.acquire() as conn:
        student = await conn.fetchrow("SELECT * FROM students WHERE user_id=$1", current_user["id"])
        
        if student == None:
            raise HTTPException(
                status_code=404,
                detail="Not Found"
            )
        
        if not student:
            raise HTTPException(status_code=404, detail="Мы перерыли всю бд, но так его и не нашли :(")
    return student

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
        detail="Nothing to do here"
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
        "version": "beta 4.7.0"         #(начал вести учет версий)
    }

@app.get("/students")
async def get_students(student_id: int):
    
    async with db.pool.acquire() as conn:
        students = await conn.fetch("""SELECT users.name FROM students
                            JOIN users ON students.user_id = users.id
                            WHERE students.id = $1""", student_id)
    
    if students == []:
        raise HTTPException(
            status_code=404,
            detail="No students in table :/"
        )
    return [dict(row) for row in students]

@app.get("/users/me")
async def get_current_user(current_user = Depends(get_user)):
    return current_user

@app.get("/students/me")
async def get_current_student(student = Depends(get_current_student)):
    student_id = student["id"]
    class_id = student["class_id"]
    return {"student_id": student_id, "class_id": class_id}

@app.get("/students/me/homeworks")
async def get_homeworks (student = Depends(get_current_student)):
    
    async with db.pool.acquire() as conn:
        
        if not student:
            raise HTTPException(
                status_code=404,
                detail="Student not found :\\"
            )
        
        homeworks = await conn.fetch("""
            SELECT h.id, h.title, h.due_date, su.name as subject_name FROM students st
            JOIN classes c ON st.class_id = c.id
            JOIN subjects su ON c.id = su.class_id
            LEFT JOIN homeworks h ON h.subject_id = su.id
            WHERE st.class_id = $1
            ORDER BY h.due_date ASC;
            """,
            student["class_id"]
            )
    
    return [dict(row) for row in homeworks]

@app.get("/homework")
async def get_homework (subject_id: int, current_user = Depends(get_user)):
    
    async with db.pool.acquire() as conn:
        
        class_id = await conn.fetchrow("""
            SELECT class_id FROM students WHERE user_id = $1
            """,
            current_user["id"]
            )
        
        if class_id == None:
            raise HTTPException(
                status_code=404,
                detail="Not Found"
            )
        
        subject_class_id = await conn.fetchrow("""
            SELECT class_id FROM subjects WHERE id = $1 
            """,
            subject_id
            )
        
        if subject_class_id == None:
            raise HTTPException(
                status_code=404,
                detail="Not Found"
            )
        
        if class_id["class_id"] == subject_class_id["class_id"]:
            homework = await conn.fetchrow("""
                SELECT id, title, description, due_date FROM homeworks
                WHERE subject_id = $1
                ORDER BY due_date ASC
            """, subject_id
            )
        else:
            raise HTTPException(
                status_code=403,
                detail="Forbidden \\:-|"
            )
    
    return homework

@app.get("/ping")
async def get_ping():
    
    before = time.time_ns()
    
    after = time.time_ns()
    
    difference = after - before
    
    diff_sec = difference / 1000000
    
    rounded_ds = round(diff_sec)
    return {
        "message": "Pong!",
        "ping": rounded_ds
    }

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
                INSERT INTO teachers (user_id, class_id)
                VALUES ($1, $2)
                """,
                user_id,
                user.class_id
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
        
        teacher_id = await conn.fetchrow("""
            SELECT id FROM teachers
            WHERE user_id = $1
            """,
            current_user["id"]
            )
        
        if teacher_id == None:
            raise HTTPException(
                status_code=403,
                detail="Forbidden. You aren't a teacher"
            )
        
        subject_teacher_class_id = await conn.fetchrow("""
            SELECT class_id, teacher_id FROM subjects WHERE id = $1
            """,
            grades.subject_id
            )
        
        if subject_teacher_class_id == None:
            raise HTTPException(
                status_code=404,
                detail="Not Found"
            )
        
        if teacher_id["id"] != subject_teacher_class_id["teacher_id"]:
            raise HTTPException(
                status_code=403,
                detail="Forbidden :|"
            )
        
        student_class_id = await conn.fetchrow("""
            SELECT class_id FROM students WHERE id = $1
            """,
            grades.student_id
            )
        
        if student_class_id == None:
            raise HTTPException(
                status_code=404,
                detail="Not Found"
            )
        
        if subject_teacher_class_id["class_id"] != student_class_id["class_id"]:
            raise HTTPException(
                status_code=403,
                detail="Forbidden :|"
            )
        
        await conn.execute(
        """
        INSERT INTO grades (student_id, subject_id, grade, date)
        VALUES ($1, $2, $3, $4)
        """,
        grades.student_id,
        grades.subject_id,
        grades.grade,
        grades.date
    )
    
    return {"status": "Successful"}

# <! Error Handlers !> #        my English is very well)

@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return JSONResponse(
        status_code=404,
        content={"error": "Not Found :("}
    )