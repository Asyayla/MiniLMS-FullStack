from sqlalchemy.orm import Session
from app import models


def get_lesson_by_id(db: Session, lesson_id: int):
    """
    Queries the database layer to locate a single unique lesson record by its ID.
    """
    return db.query(models.Lesson).filter(models.Lesson.id == lesson_id).first()


def calculate_lesson_success(db: Session, lesson_id: int):
    """
    Aggregates full grade entry metrics associated with a lesson to calculate 
    the cumulative statistical average score and absolute student count.
    """
    # Fetch all grade transaction records mapping to the specific target lesson
    grades = db.query(models.Grade).filter(models.Grade.lesson_id == lesson_id).all()

    # Guard clause against processing empty datasets to prevent ZeroDivisionError paths
    if not grades:
        return None

    # Calculate global mathematical mean across accumulated grade vectors
    total_score = sum([g.grade_value for g in grades])
    average = total_score / len(grades)

    return {
        "lesson_id": lesson_id,
        "average_score": round(average, 2),
        "student_count": len(grades)
    }