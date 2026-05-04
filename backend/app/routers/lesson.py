from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.services import auth
from app.services import lesson_service # Servis katmanini baglayacagiz

router = APIRouter(
    prefix="/lessons",
    tags=["Lesson Operations"],
)

@router.post("/", response_model=schemas.LessonResponse, status_code=status.HTTP_201_CREATED)
def create_lesson(
    lesson_in: schemas.LessonCreate,
    db: Session = Depends(get_db),
    current_user: schemas.TokenData = Depends(auth.get_current_user),
):
    # Sadece ogretmen/admin ders olusturabilir
    if current_user.role not in ["teacher", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only teachers or administrators are authorized to perform this action.",
        )

    # teacher_id gercekten var mi?
    teacher = db.query(models.User).filter(models.User.id == lesson_in.teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found.")

    # teacher_id kullanicisi uygun rolde mi?
    if teacher.role not in ["teacher", "admin"]:
        raise HTTPException(
            status_code=400,
            detail="teacher_id must be a user with the role of teacher or admin.",
        )

    # ayni ders kodu tekrar olusmasin
    existing_lesson = db.query(models.Lesson).filter(models.Lesson.code == lesson_in.code).first()
    if existing_lesson:
        raise HTTPException(status_code=400, detail="This lesson code is already registered.")

    lesson = models.Lesson(
        name=lesson_in.name,
        code=lesson_in.code,
        teacher_id=lesson_in.teacher_id,
    )
    db.add(lesson)
    db.commit()
    db.refresh(lesson)
    return lesson

@router.get("/{id}")
def get_lesson_details(id: int, db: Session = Depends(get_db)):
    lesson = lesson_service.get_lesson_by_id(db, lesson_id=id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found.")
    return lesson

@router.get("/{id}/success")
def get_lesson_success_stats(id: int, db: Session = Depends(get_db)):
    # Bu endpoint dersteki genel basari istatistiklerini (ortalama vb.) doner
    stats = lesson_service.calculate_lesson_success(db, lesson_id=id)
    if not stats:
        raise HTTPException(status_code=404, detail="Lesson statistics could not be calculated.")
    return stats

# Tum dersleri listeleyen endpoint
@router.get("/", response_model=list[schemas.LessonResponse])   
def list_all_lessons(
    db: Session = Depends(get_db),
    current_user: schemas.TokenData = Depends(auth.get_current_user)
):
    print(f"Debug: Logged-in user id: {current_user.user_id}, Role: {current_user.role}")

    #admin ise her seyi gorsun
    if current_user.role == "admin":
        return db.query(models.Lesson).all()
    
    #ogretmen ise sadece kendi derslerini gorsun
    if current_user.role == "teacher":
        return db.query(models.Lesson).filter(models.Lesson.teacher_id == current_user.user_id).all()

    #ogrenci ise sadece kayitli oldugu dersleri gorsun
    return db.query(models.Lesson).all()

# ogrencinin bir derse kayit olmasi
@router.post("/{lesson_id}/enroll", status_code=status.HTTP_201_CREATED)
def enroll_in_lesson(
    lesson_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.TokenData = Depends(auth.get_current_user),
):
    # Sadece ogrenciler kayit olabilir
    if current_user.role not in ["student"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can register for the course.",
        )

    # Ders var mi?
    lesson = db.query(models.Lesson).filter(models.Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found.")

    # ogrenci profilini bul (user_id'den student_id'yi al)
    student = db.query(models.Student).filter(models.Student.user_id == current_user.user_id).first()
    if not student:
        raise HTTPException(
            status_code=404, 
            detail="Student profile not found. Please contact the system administrator."
        )

    # Zaten kayitli mi kontrol et
    existing_enrollment = db.query(models.Grade).filter(
        models.Grade.student_id == student.id,
        models.Grade.lesson_id == lesson_id
    ).first()
    
    if existing_enrollment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are already enrolled in this lesson."
        )

    # Yeni kayit olustur (Grade tablosunda başlangic degerleri ile)
    enrollment = models.Grade(
        student_id=student.id,
        lesson_id=lesson_id,
        grade_value=0.0,  # Baslangıc notu
        grade_type="Enrollment",
        absenteeism_count=0
    )
    
    db.add(enrollment)
    db.commit()
    db.refresh(enrollment)
    
    return {"message": "You have successfully registered for the course!", "enrollment_id": enrollment.id}

# Derse kayitli ogrencileri listele (ogretmen icin)
@router.get("/{lesson_id}/students")
def get_lesson_students(
    lesson_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.TokenData = Depends(auth.get_current_user),
):
    # Ders var mi?
    lesson = db.query(models.Lesson).filter(models.Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found.")

    # Yetki kontrolu: Dersin ogretmeni veya admin olmali
    if current_user.role == "teacher" and lesson.teacher_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to view students for this lesson."
        )
    elif current_user.role not in ["teacher", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You must be a teacher or administrator to perform this action."
        )

    # Derse kayitli ogrencileri getir
    grades = db.query(models.Grade, models.Student).join(
        models.Student, models.Grade.student_id == models.Student.id
    ).filter(
        models.Grade.lesson_id == lesson_id
    ).all()

    result = []
    for grade, student in grades:
        result.append({
            "student_id": student.id,
            "name": student.name,
            "surname": student.surname,
            "email": student.email,
            "grade_type": grade.grade_type,
            "grade_value": grade.grade_value,
            "absenteeism_count": grade.absenteeism_count,
        })

    return {
        "lesson_id": lesson_id,
        "lesson_name": lesson.name,
        "student_count": len(result),
        "students": result
    }


# Ders guncelleme (PUT /lessons/{id}) - Admin only
@router.put("/{lesson_id}", response_model=schemas.LessonResponse)
def update_lesson(
    lesson_id: int,
    lesson_in: schemas.LessonCreate,
    db: Session = Depends(get_db),
    current_user: schemas.TokenData = Depends(auth.get_current_user),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only administrators can update lessons.")
    lesson = db.query(models.Lesson).filter(models.Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found.")
    lesson.name = lesson_in.name
    lesson.code = lesson_in.code
    lesson.teacher_id = lesson_in.teacher_id
    db.commit()
    db.refresh(lesson)
    return lesson

# Ders silme (DELETE /lessons/{id}) - Admin only
@router.delete("/{lesson_id}")
def delete_lesson(
    lesson_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.TokenData = Depends(auth.get_current_user),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only administrators can delete lessons.")
    lesson = db.query(models.Lesson).filter(models.Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found.")
    db.query(models.Grade).filter(models.Grade.lesson_id == lesson_id).delete()
    db.delete(lesson)
    db.commit()
    return {"message": "Lesson deleted successfully."}

# Dersten ayrilma (DELETE /lessons/{lesson_id}/enroll)
@router.delete("/{lesson_id}/enroll")
def unenroll_from_lesson(
    lesson_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.TokenData = Depends(auth.get_current_user),
):
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Only students can unenroll from lessons.")
    
    student = db.query(models.Student).filter(models.Student.user_id == current_user.user_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found.")
    
    enrollments = db.query(models.Grade).filter(
        models.Grade.student_id == student.id,
        models.Grade.lesson_id == lesson_id
    ).all()
    
    if not enrollments:
        raise HTTPException(status_code=404, detail="You are not enrolled in this lesson.")
    
    for enrollment in enrollments:
        db.delete(enrollment)
    
    db.commit()
    return {"message": "Successfully unenrolled from the lesson."}