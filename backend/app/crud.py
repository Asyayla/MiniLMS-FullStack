from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from . import models, schemas
from app.services import logic 

def create_student(db: Session, student: schemas.StudentCreate):
    """
    Validates constraints and registers a new student profile in the database.
    Ensures unique constraint compliance for user_id, email, and student_number.
    """
    # Verify that the underlying user account entity exists before registration
    user = db.query(models.User).filter(models.User.id == student.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="No user was found for the specified user_id.")

    # Enforce uniqueness constraint checking on the email resource mapping
    existing_email = db.query(models.Student).filter(models.Student.email == student.email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="This email address is already registered.")

    # Enforce uniqueness constraint checking on the student identification number
    existing_number = db.query(models.Student).filter(models.Student.student_number == student.student_number).first()
    if existing_number:
        raise HTTPException(status_code=400, detail="This student number is already registered.")

    # Instantiate and bind the model entity mapping
    db_student = models.Student(
        name=student.name,
        surname=student.surname,
        student_number=student.student_number,
        user_id=student.user_id,
        email=student.email
    )
    db.add(db_student) 
    try:
        db.commit() 
        db.refresh(db_student) 
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Failed to register student. Please check the user_id/email/student_number values.",
        )
    return db_student

def get_student(db: Session, student_id: int):
    """
    Fetches a single student metadata record from the directory using its unique ID.
    """
    return db.query(models.Student).filter(models.Student.id == student_id).first()

def create_grade(db: Session, grade_in: schemas.GradeCreate):
    """
    Submits an evaluation grade record after verifying all systemic institutional 
    business logic guidelines and boundaries.
    """
    # Enforce numeric boundary value checks (0-100) safely
    logic.validate_grade_value(grade_in.grade_value)

    # Prevent processing if the candidate entry parameters violate attendance guidelines
    if logic.check_absenteeism_limit(grade_in.blackbox_absenteeism_count if hasattr(grade_in, 'blackbox_absenteeism_count') else grade_in.absenteeism_count):
        raise HTTPException(
            status_code=400,
            detail="Absence count has exceeded the 30% limit. This student will automatically fail this course."
        )

    # Validate structural existence properties of student and lesson contexts
    student = db.query(models.Student).filter(models.Student.id == grade_in.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found.")

    lesson = db.query(models.Lesson).filter(models.Lesson.id == grade_in.lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found.")

    # Guard against duplicate evaluations for identical evaluation types
    existing_grade = db.query(models.Grade).filter(
        models.Grade.student_id == grade_in.student_id,
        models.Grade.lesson_id == grade_in.lesson_id,
        models.Grade.grade_type == grade_in.grade_type
    ).first()

    if existing_grade:
        raise HTTPException(status_code=400, detail="This type of grade already exists!")

    # Verify cumulative historical attendance tracks to check against limit bounds
    other_grades = db.query(models.Grade).filter(
        models.Grade.student_id == grade_in.student_id,
        models.Grade.lesson_id == grade_in.lesson_id,
    ).all()
    for existing in other_grades:
        if logic.check_absenteeism_limit(existing.absenteeism_count):
            raise HTTPException(
                status_code=400,
                detail=f"Your absence count has exceeded the 30% limit in this course ({existing.grade_type}: {existing.absenteeism_count}). You will automatically fail this course."
            )

    # Persist the transactional grade schema structure maps
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
            detail="Student or lesson not found.",
        )
    return db_grade

def update_grade(db: Session, grade_id: int, grade_update: schemas.GradeUpdate):
    """
    Updates operational grade parameters or updates attendance tracking fields safely.
    """
    db_grade = db.query(models.Grade).filter(models.Grade.id == grade_id).first()
    if not db_grade:
        return None

    # Dynamically update the grade score properties if provided
    if grade_update.grade_value is not None:
        logic.validate_grade_value(grade_update.grade_value)
        db_grade.grade_value = grade_update.grade_value

    # Dynamically evaluate and update absenteeism indicators if provided
    if grade_update.absenteeism_count is not None:
        if logic.check_absenteeism_limit(grade_update.absenteeism_count):
            raise HTTPException(
                status_code=400,
                detail="Your absence count has exceeded the 30% limit. You will automatically fail this course."
            )
        db_grade.absenteeism_count = grade_update.absenteeism_count

    db.commit()
    db.refresh(db_grade)
    return db_grade

def get_student_transcript(db: Session, student_id: int):
    """
    Compiles a comprehensive, aggregated student grade transcript report mapping 
    across course collections using relational database joins.
    """
    # Execute join query linking Grade records cleanly with Lesson properties vectors
    results = db.query(models.Grade, models.Lesson).join(
        models.Lesson, models.Grade.lesson_id == models.Lesson.id
    ).filter(models.Grade.student_id == student_id).all()

    transcript_data = []
    for grade, lesson in results:
        # Enforce corporate attendance policy logic: auto-fail if absences > 30%
        is_absent = logic.check_absenteeism_limit(grade.absenteeism_count, total_hours=100)

        # Map programmatic statuses derived from grade evaluation parameters
        if is_absent:
            status_text = "Failed (Absenteeism)"
        elif grade.grade_value >= 50:
            status_text = "Passed"
        else:
            status_text = "Failed"

        # Structural response assembly mapping block
        transcript_data.append({
            "lesson_id": lesson.id,
            "lesson_code": lesson.code,
            "lesson_name": lesson.name,
            "grade_type": grade.grade_type,
            "grade_value": grade.grade_value,
            "absenteeism": grade.absenteeism_count,
            "status": status_text 
        })

    return transcript_data