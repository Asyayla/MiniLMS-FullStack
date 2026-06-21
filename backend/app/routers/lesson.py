from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.services import auth
from app.services import lesson_service 

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
    """
    Creates a new lesson entry in the system.
    Restricted to admin and teacher accounts. Ensures unique lesson codes.
    """
    # Enforce role-based permission tracking
    if current_user.role not in ["teacher", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only teachers or administrators are authorized to perform this action.",
        )

    # Validate that the assigned teacher actually exists in the database
    teacher = db.query(models.User).filter(models.User.id == lesson_in.teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found.")

    # Validate that the assigned user profile holds a proper teaching/admin role
    if teacher.role not in ["teacher", "admin"]:
        raise HTTPException(
            status_code=400,
            detail="teacher_id must be a user with the role of teacher or admin.",
        )

    # Enforce uniqueness constraint on the lesson code schema
    existing_lesson = db.query(models.Lesson).filter(models.Lesson.code == lesson_in.code).first()
    if existing_lesson:
        raise HTTPException(status_code=400, detail="This lesson code is already registered.")

    # Initialize and commit the new lesson instance
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
    """
    Fetches details of a specific lesson using its unique ID identifier.
    """
    lesson = lesson_service.get_lesson_by_id(db, lesson_id=id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found.")
    return lesson

@router.get("/{id}/success")
def get_lesson_success_stats(id: int, db: Session = Depends(get_db)):
    """
    Calculates overall success, fail rates, and averages for a specific lesson container.
    """
    stats = lesson_service.calculate_lesson_success(db, lesson_id=id)
    if not stats:
        raise HTTPException(status_code=404, detail="Lesson statistics could not be calculated.")
    return stats

@router.get("/", response_model=list[schemas.LessonResponse])   
def list_all_lessons(
    db: Session = Depends(get_db),
    current_user: schemas.TokenData = Depends(auth.get_current_user)
):
    """
    Lists all available lessons. Admins see everything, teachers see their assigned courses.
    """
    print(f"Debug: Logged-in user id: {current_user.user_id}, Role: {current_user.role}")

    # Return full directory listings for administrators
    if current_user.role == "admin":
        return db.query(models.Lesson).all()
    
    # Filter specific lesson directory mappings assigned to the requesting instructor
    if current_user.role == "teacher":
        return db.query(models.Lesson).filter(models.Lesson.teacher_id == current_user.user_id).all()

    # Fallback default boundary mapping rule
    return db.query(models.Lesson).all()

@router.post("/{lesson_id}/enroll", status_code=status.HTTP_201_CREATED)
def enroll_in_lesson(
    lesson_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.TokenData = Depends(auth.get_current_user),
):
    """
    Enrolls an authenticated student user into a given course using an initial reference token.
    """
    # Restrict course registration logic to student roles exclusively
    if current_user.role not in ["student"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can register for the course.",
        )

    # Ensure target lesson structure exists safely
    lesson = db.query(models.Lesson).filter(models.Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found.")

    # Locate underlying student relational metadata profile mapping
    student = db.query(models.Student).filter(models.Student.user_id == current_user.user_id).first()
    if not student:
        raise HTTPException(
            status_code=404, 
            detail="Student profile not found. Please contact the system administrator."
        )

    # Guard clause against processing redundant enrollment tracking paths
    existing_enrollment = db.query(models.Grade).filter(
        models.Grade.student_id == student.id,
        models.Grade.lesson_id == lesson_id
    ).first()
    
    if existing_enrollment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are already enrolled in this lesson."
        )

    # Create initial placeholder index mapping using an 'Enrollment' grade transaction archetype
    enrollment = models.Grade(
        student_id=student.id,
        lesson_id=lesson_id,
        grade_value=0.0,  
        grade_type="Enrollment",
        absenteeism_count=0
    )
    
    db.add(enrollment)
    db.commit()
    db.refresh(enrollment)
    
    return {"message": "You have successfully registered for the course!", "enrollment_id": enrollment.id}

@router.get("/{lesson_id}/students")
def get_lesson_students(
    lesson_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.TokenData = Depends(auth.get_current_user),
):
    """
    Lists all enrolled student records associated with a specific lesson ID context.
    Instructors can only view data from their matching course maps.
    """
    lesson = db.query(models.Lesson).filter(models.Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found.")

    # Implement domain access boundaries between separate teaching assignments
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

    # Perform a join query across Grade and Student schemas to filter matching results
    grades = db.query(models.Grade, models.Student).join(
        models.Student, models.Grade.student_id == models.Student.id
    ).filter(
        models.Grade.lesson_id == lesson_id
    ).all()

    # Flatten nested ORM entities down into normalized dictionaries
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

@router.put("/{lesson_id}", response_model=schemas.LessonResponse)
def update_lesson(
    lesson_id: int,
    lesson_in: schemas.LessonCreate,
    db: Session = Depends(get_db),
    current_user: schemas.TokenData = Depends(auth.get_current_user),
):
    """
    Updates operational lesson parameters safely. Access level: Admin only.
    """
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

@router.delete("/{lesson_id}")
def delete_lesson(
    lesson_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.TokenData = Depends(auth.get_current_user),
):
    """
    Cascades removal of structural lesson components alongside child relational mapping profiles. Admin only.
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only administrators can delete lessons.")
        
    lesson = db.query(models.Lesson).filter(models.Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found.")
        
    # Prune dependencies cleanly before dropping principal entity bindings
    db.query(models.Grade).filter(models.Grade.lesson_id == lesson_id).delete()
    db.delete(lesson)
    db.commit()
    return {"message": "Lesson deleted successfully."}

@router.delete("/{lesson_id}/enroll")
def unenroll_from_lesson(
    lesson_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.TokenData = Depends(auth.get_current_user),
):
    """
    Allows an authenticated student account to securely cancel registration ties on a distinct course map.
    """
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Only students can unenroll from lessons.")
    
    student = db.query(models.Student).filter(models.Student.user_id == current_user.user_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found.")
    
    # Locate all grade history bindings corresponding to this specific structural configuration map
    enrollments = db.query(models.Grade).filter(
        models.Grade.student_id == student.id,
        models.Grade.lesson_id == lesson_id
    ).all()
    
    if not enrollments:
        raise HTTPException(status_code=404, detail="You are not enrolled in this lesson.")
    
    # Erase enrollment maps entirely
    for enrollment in enrollments:
        db.delete(enrollment)
    
    db.commit()
    return {"message": "Successfully unenrolled from the lesson."}