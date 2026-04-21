from sqlalchemy.orm import Session
from app import models


def get_lesson_by_id(db: Session, lesson_id: int):
    return db.query(models.Lesson).filter(models.Lesson.id == lesson_id).first()


def calculate_lesson_success(db: Session, lesson_id: int):
    # Grades tablosundan bu derse ait tüm notları çek
    grades = db.query(models.Grade).filter(models.Grade.lesson_id == lesson_id).all()

    if not grades:
        return None

    # Modelle uyumlu şekilde grade_value üzerinden hesapla
    total_score = sum([g.grade_value for g in grades])
    average = total_score / len(grades)

    return {
        "lesson_id": lesson_id,
        "average_score": round(average, 2),
        "student_count": len(grades)
    }