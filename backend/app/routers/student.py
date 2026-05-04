#logic: is kurallari, projenin beyni.
#bu beyni dis dunyaya baglayan da main ve routers.
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import crud, schemas, database
from app.services import auth
from typing import List


router = APIRouter(
    prefix="/students",
    tags=["Student Operations"],
)

#db baglantisini her istekte acip kapatan yardimci fonksiyon
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

#1. yeni ogrenci olusturma(POST /ogrenci)
@router.post("/", response_model=schemas.StudentResponse)
def create_student(student: schemas.StudentCreate, db: Session = Depends(get_db)):
    return crud.create_student(db=db, student=student)

#2. id ile ogrenci getirme(GET /student{id})
@router.get("/{id}", response_model=schemas.StudentResponse)
def read_student(id: int, db: Session = Depends(get_db)): #dependency injection
    db_student = crud.get_student(db, student_id=id)
    if db_student is None:
        raise HTTPException(status_code=404, detail="Student not found.")
    return db_student

#3. Get Student Transaction (GET /student/{id}/transcript)
@router.get("/{id}/transcript")
def read_student_transcript(id: int, db: Session = Depends(get_db)):
    from app import models
    # once user_id ile student profilini bul
    student = db.query(models.Student).filter(models.Student.user_id == id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found.")
    transcript = crud.get_student_transcript(db, student_id=student.id)
    if not transcript:
        raise HTTPException(status_code=404, detail="Transcript or grades not found.")
    return transcript

    
# 4. Get all students (GET /students/)
@router.get("/", response_model=list[schemas.StudentResponse])
def get_all_students(db: Session = Depends(get_db)):
    from app import models
    return db.query(models.Student).all()

# 5. Get all users (GET /students/users/all) - Admin only
@router.get("/users/all")
def get_all_users(
    db: Session = Depends(get_db),
    current_user: schemas.TokenData = Depends(auth.get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only administrators can access this endpoint.")
    from app import models
    users = db.query(models.User).all()
    return [
        {
            "id": u.id,
            "username": u.username,
            "role": u.role,
        }
        for u in users
    ]

# 6. Delete user (DELETE /students/users/{id}) - Admin only
@router.delete("/users/{id}")
def delete_user(
    id: int,
    db: Session = Depends(get_db),
    current_user: schemas.TokenData = Depends(auth.get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only administrators can delete users.")
    from app import models
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    if user.id == current_user.user_id:
        raise HTTPException(status_code=400, detail="You cannot delete your own account.")
    
    # Bagli student profilini ve grade kayitlarini sil
    student = db.query(models.Student).filter(models.Student.user_id == id).first()
    if student:
        db.query(models.Grade).filter(models.Grade.student_id == student.id).delete()
        db.delete(student)
    
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully."}


# 7. Update user role (PUT /students/users/{id}) - Admin only
@router.put("/users/{id}")
def update_user_role(
    id: int,
    role_data: dict,
    db: Session = Depends(get_db),
    current_user: schemas.TokenData = Depends(auth.get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only administrators can update users.")
    from app import models
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    user.role = role_data.get("role", user.role)
    db.commit()
    return {"message": "User updated successfully.", "id": user.id, "username": user.username, "role": user.role}