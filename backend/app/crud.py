#bu dosya db islemlerini(repository) yonetir ve logic.py deki kurallari uygular
#dbye git su veriyi kaydet veya sunu getir diyen ham sorguların oldugu yer.
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from . import models, schemas
from app.services import logic #logic.py icindeki kurallari buraya cagiriyoruz

#1. ogrenciyi dbye kaydetme(POST /ogrenci icin)
def create_student(db: Session, student: schemas.StudentCreate):
    #kural1: kullanici var mi?
    user = db.query(models.User).filter(models.User.id == student.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Belirtilen user_id icin kullanici bulunamadi.")

    #kural2: email benzersiz mi?
    existing_email = db.query(models.Student).filter(models.Student.email == student.email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Bu email adresi zaten kayitli.")

    #kural3: ogrenci numarasi benzersiz mi?
    existing_number = db.query(models.Student).filter(models.Student.student_number == student.student_number).first()
    if existing_number:
        raise HTTPException(status_code=400, detail="Bu ogrenci numarasi zaten kayitli.")

    db_student = models.Student(
        name=student.name,
        surname=student.surname,
        student_number=student.student_number,
        user_id=student.user_id,
        email=student.email
    )
    db.add(db_student) # SQL: insert into students...
    try:
        db.commit() #degisiklikleri kaydet
        db.refresh(db_student) #dbnin verdigi id yi geri al
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Ogrenci kaydi yapilamadi. user_id/email/student_number degerlerini kontrol edin.",
        )
    return db_student

#2. Id ile ogrenci getirme(GET /ogrenci/{id} icin)
def get_student(db: Session, student_id: int):
    """Id ile ogrenci bilgilerini getirir."""
    return db.query(models.Student).filter(models.Student.id == student_id).first()

#3. Not girisi
def create_grade(db: Session, grade_in: schemas.GradeCreate):
    """Is kurallarini denetleyerek not girisi yapar."""
    # kural1: not degeri 0-100 arasinda mi
    logic.validate_grade_value(grade_in.grade_value)

    # kural1b: devamsizlik %30 limiti asilmis mi
    if logic.check_absenteeism_limit(grade_in.absenteeism_count):
        raise HTTPException(
            status_code=400,
            detail="Devamsizlik sayisi %30 limiti asmis. Bu derste otomatik kalacaktir."
        )

    #kural2: ogrenci sistemde var mi
    student = db.query(models.Student).filter(models.Student.id == grade_in.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Ogrenci bulunamadi.")

    #kural3: ders sistemde var mi
    lesson = db.query(models.Lesson).filter(models.Lesson.id == grade_in.lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Ders bulunamadi.")

    #kural4: ayni tip not var mi
    existing_grade = db.query(models.Grade).filter(
        models.Grade.student_id == grade_in.student_id,
        models.Grade.lesson_id == grade_in.lesson_id,
        models.Grade.grade_type == grade_in.grade_type
    ).first()

    if existing_grade:
        raise HTTPException(status_code=400, detail="Bu tur icin notlandirma zaten var!")

    # kural5: aynı derste diğer notlarda devamsizlik > 30 mu
    other_grades = db.query(models.Grade).filter(
        models.Grade.student_id == grade_in.student_id,
        models.Grade.lesson_id == grade_in.lesson_id,
    ).all()
    for existing in other_grades:
        if logic.check_absenteeism_limit(existing.absenteeism_count):
            raise HTTPException(
                status_code=400,
                detail=f"Bu derste daha onceki notlarda devamsizlik %30 limiti asilmis ({existing.grade_type}: {existing.absenteeism_count}). Otomatik kalacaktir."
            )

    #kayit islemi
    db_grade = models.Grade(
        student_id=grade_in.student_id,
        lesson_id=grade_in.lesson_id,
        grade_value=grade_in.grade_value,
        grade_type=grade_in.grade_type,
        absenteeism_count=grade_in.absenteeism_count
    )
    db.add(db_grade)
    try:
        db.commit()
        db.refresh(db_grade)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=404,
            detail="Ogrenci veya ders bulunamadi.",
        )
    return db_grade

#4. not guncelleme (PUT /grades/{id})
def update_grade(db: Session, grade_id: int, grade_update: schemas.GradeUpdate):
    db_grade = db.query(models.Grade).filter(models.Grade.id == grade_id).first()
    if not db_grade:
        return None

    #guncelleme sirasinda da 0-100 kurali onemli
    if grade_update.grade_value is not None:
        logic.validate_grade_value(grade_update.grade_value)
        db_grade.grade_value = grade_update.grade_value

    if grade_update.absenteeism_count is not None:
        # devamsizlik %30 limiti kontrol et
        if logic.check_absenteeism_limit(grade_update.absenteeism_count):
            raise HTTPException(
                status_code=400,
                detail="Devamsizlik sayisi %30 limiti asmis. Bu derste otomatik kalacaktir."
            )
        db_grade.absenteeism_count = grade_update.absenteeism_count

    db.commit()
    db.refresh(db_grade)
    return db_grade

#5. transcript ve basari durumu
def get_student_transcript(db: Session, student_id: int):
    #ogrencinin notlarini ders isimleriyle birlikte cekmek icin join kullaniyoruz.
    results = db.query(models.Grade, models.Lesson).join(
        models.Lesson, models.Grade.lesson_id == models.Lesson.id
    ).filter(models.Grade.student_id == student_id).all()

    transcript_data = []
    for grade, lesson in results:
        #business logic: devamsizlik %30 fazla ise otomatik kalir.
        #toplam ders saati 100 uzerinden hesaplanmistir
        is_absent = logic.check_absenteeism_limit(grade.absenteeism_count, total_hours=100)

        if is_absent:
            status = "Failed (Absenteeism)"
        elif grade.grade_value >= 50:
            status = "Passed"
        else:
            status = "Failed"

        #dokumanda beklenen tum bilgileri listeye ekliyoruz
        transcript_data.append({
            "lesson_code": lesson.code,
            "lesson_name": lesson.name,
            "grade_value": grade.grade_value,
            "absenteeism": grade.absenteeism_count,
            "status": status
        })

    return transcript_data
