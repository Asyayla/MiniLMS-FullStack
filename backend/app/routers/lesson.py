from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.services import auth
from app.services import lesson_service # Servis katmanını bağlayacağız

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
            detail="Bu islem icin sadece ogretmen veya admin yetkilidir.",
        )

    # teacher_id gercekten var mi?
    teacher = db.query(models.User).filter(models.User.id == lesson_in.teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Ogretmen bulunamadi.")

    # teacher_id kullanicisi uygun rolde mi?
    if teacher.role not in ["teacher", "admin"]:
        raise HTTPException(
            status_code=400,
            detail="teacher_id ogretmen/admin rolunde bir kullanici olmalidir.",
        )

    # ayni ders kodu tekrar olusmasin
    existing_lesson = db.query(models.Lesson).filter(models.Lesson.code == lesson_in.code).first()
    if existing_lesson:
        raise HTTPException(status_code=400, detail="Bu ders kodu zaten kayitli.")

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
        raise HTTPException(status_code=404, detail="Ders bulunamadı")
    return lesson

@router.get("/{id}/success")
def get_lesson_success_stats(id: int, db: Session = Depends(get_db)):
    # Bu endpoint dersteki genel başarı istatistiklerini (ortalama vb.) döner
    stats = lesson_service.calculate_lesson_success(db, lesson_id=id)
    if not stats:
        raise HTTPException(status_code=404, detail="Ders istatistikleri hesaplanamadı")
    return stats