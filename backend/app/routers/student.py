from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import crud, schemas, database
from app.services import auth
from typing import List


router = APIRouter(
    prefix="/students",
    tags=["Student Operations"],
)

def get_db():
    """
    Helper dependency that opens and closes the database connection 
    context cleanly for each incoming request lifecycle.
    """
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=schemas.StudentResponse)
def create_student(student: schemas.StudentCreate, db: Session = Depends(get_db)):
    """
    Registers a new student record profile into the system directory.
    """
    return crud.create_student(db=db, student=student)


@router.get("/{id}", response_model=schemas.StudentResponse)
def read_student(id: int, db: Session = Depends(get_db)):
    """
    Fetches a single student metadata profile structure by its unique ID.
    Utilizes dependency injection for secure transactional database sessions.
    """
    db_student = crud.get_student(db, student_id=id)
    if db_student is None:
        raise HTTPException(status_code=404, detail="Student not found.")
    return db_student


@router.get("/{id}/transcript")
def read_student_transcript(id: int, db: Session = Depends(get_db)):
    """
    Retrieves the comprehensive grade transcript report using the associated user identity map.
    """
    from app import models

    # Locate structural student profile associated with the user account frame
    student = db.query(models.Student).filter(models.Student.user_id == id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found.")
        
    transcript = crud.get_student_transcript(db, student_id=student.id)
    if not transcript:
        raise HTTPException(status_code=404, detail="Transcript or grades not found.")
    return transcript

    
@router.get("/", response_model=list[schemas.StudentResponse])
def get_all_students(db: Session = Depends(get_db)):
    """
    Returns a list summary of all registered student profiles present in the catalog.
    """
    from app import models
    return db.query(models.Student).all()


@router.get("/users/all")
def get_all_users(
    db: Session = Depends(get_db),
    current_user: schemas.TokenData = Depends(auth.get_current_user)
):
    """
    Lists credentials profiles for administrative management tasks. Access level: Admin only.
    """
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


@router.delete("/users/{id}")
def delete_user(
    id: int,
    db: Session = Depends(get_db),
    current_user: schemas.TokenData = Depends(auth.get_current_user)
):
    """
    Performs a cascading deletion of user entities, tracking child profiles and constraints cleanly. Admin only.
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only administrators can delete users.")
        
    from app import models
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    if user.id == current_user.user_id:
        raise HTTPException(status_code=400, detail="You cannot delete your own account.")
    
    # Prune associated child tables to prevent foreign key constraint violations
    student = db.query(models.Student).filter(models.Student.user_id == id).first()
    if student:
        db.query(models.Grade).filter(models.Grade.student_id == student.id).delete()
        db.delete(student)
    
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully."}


@router.put("/users/{id}")
def update_user_role(
    id: int,
    role_data: dict,
    db: Session = Depends(get_db),
    current_user: schemas.TokenData = Depends(auth.get_current_user)
):
    """
    Updates the system authorizations level role of a given user account record framework. Admin only.
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only administrators can update users.")
        
    from app import models
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
        
    user.role = role_data.get("role", user.role)
    db.commit()
    return {"message": "User updated successfully.", "id": user.id, "username": user.username, "role": user.role}


@router.get("/{id}/comment")
def get_student_ai_comment(
    id: int,
    db: Session = Depends(get_db),
    current_user: schemas.TokenData = Depends(auth.get_current_user)
):
    """
    Returns an automated, AI-generated analytical performance evaluation summary 
    for the student based on current transcript metrics.
    """
    from app import models
    from app.services.ai_service import generate_student_comment

    # Resolve core identity maps
    student = db.query(models.Student).filter(models.Student.user_id == id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found.")

    # Retrieve context foundation structure from the session cache
    transcript = crud.get_student_transcript(db, student_id=student.id)
    if not transcript:
        raise HTTPException(status_code=404, detail="No grade data found for this student.")

    # Synthesize transcript metrics safely via LLM abstraction layers
    full_name = f"{student.name} {student.surname}"
    comment = generate_student_comment(transcript_data=transcript, student_name=full_name)

    return {"student_id": id, "comment": comment}


@router.get("/{id}/recommendations")
def get_student_ai_recommendations(
    id: int,
    db: Session = Depends(get_db),
    current_user: schemas.TokenData = Depends(auth.get_current_user)
):
    """
    Generates a personalized, actionable study planner strategy derived from 
    weak course performance signals and absenteeism tracking flags.
    """
    from app import models
    from app.services.ai_service import generate_student_recommendations

    student = db.query(models.Student).filter(models.Student.user_id == id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found.")

    transcript = crud.get_student_transcript(db, student_id=student.id)
    if not transcript:
        raise HTTPException(status_code=404, detail="No grade data found for this student.")

    full_name = f"{student.name} {student.surname}"
    recommendations = generate_student_recommendations(
        transcript_data=transcript,
        student_name=full_name
    )

    return {"student_id": id, "recommendations": recommendations}


@router.post("/ai-query")
def ai_query_students(
    query_data: dict,
    db: Session = Depends(get_db),
    current_user: schemas.TokenData = Depends(auth.get_current_user)
):
    """
    NLP Natural Language Processing search gateway. Compiles text queries into structured 
    SQL filter parameters and executes safely via SQLAlchemy ORM logic patterns.
    """
    if current_user.role not in ("admin", "teacher"):
        raise HTTPException(status_code=403, detail="Only admins or teachers can use this feature.")

    from app import models
    from app.services.ai_service import parse_natural_language_query
    from sqlalchemy import func

    user_query = query_data.get("query")
    if not user_query:
        raise HTTPException(status_code=400, detail="'query' field is required.")

    # Parse plain narrative sentences into programmatic filters maps safely
    parsed = parse_natural_language_query(user_query)
    action = parsed.get("action")

    # --- ACTION 1: Cumulative GPA Evaluation and Sorting ---
    if action == "list_students":
        order = parsed.get("order", "desc")
        limit = parsed.get("limit", 10)

        if not isinstance(limit, int) or limit <= 0:
            limit = 10
        limit = min(limit, 100)

        # Build dynamic aggregated mathematical average query bounds
        gpa_subquery = (
            db.query(
                models.Grade.student_id,
                func.avg(models.Grade.grade_value).label("gpa")
            )
            .group_by(models.Grade.student_id)
            .subquery()
        )

        query_builder = (
            db.query(models.Student, gpa_subquery.c.gpa)
            .join(gpa_subquery, models.Student.id == gpa_subquery.c.student_id)
        )

        if order == "asc":
            query_builder = query_builder.order_by(gpa_subquery.c.gpa.asc())
        else:
            query_builder = query_builder.order_by(gpa_subquery.c.gpa.desc())

        results = query_builder.limit(limit).all()

        return {
            "action": action,
            "parsed_filter": parsed,
            "results": [
                {
                    "student_id": student.id,
                    "name": student.name,
                    "surname": student.surname,
                    "student_number": student.student_number,
                    "gpa": round(gpa, 2)
                }
                for student, gpa in results
            ]
        }

    # --- ACTION 2: Absenteeism Operational Threshold Tracking ---
    elif action == "filter_absenteeism":
        lesson_name = parsed.get("lesson_name")
        threshold = parsed.get("threshold")
        operator = parsed.get("operator", "gt")

        if lesson_name is None or threshold is None:
            raise HTTPException(status_code=400, detail="AI could not extract valid filters.")

        try:
            threshold = int(threshold)
        except (ValueError, TypeError):
            raise HTTPException(status_code=400, detail="Invalid threshold value from AI output.")

        op_map = {
            "gt": models.Grade.absenteeism_count > threshold,
            "lt": models.Grade.absenteeism_count < threshold,
            "gte": models.Grade.absenteeism_count >= threshold,
            "lte": models.Grade.absenteeism_count <= threshold,
        }
        condition = op_map.get(operator, models.Grade.absenteeism_count > threshold)

        results = (
            db.query(models.Student, models.Grade, models.Lesson)
            .join(models.Grade, models.Student.id == models.Grade.student_id)
            .join(models.Lesson, models.Grade.lesson_id == models.Lesson.id)
            .filter(models.Lesson.name == lesson_name)
            .filter(condition)
            .all()
        )

        return {
            "action": action,
            "parsed_filter": parsed,
            "results": [
                {
                    "student_id": student.id,
                    "name": student.name,
                    "surname": student.surname,
                    "lesson_name": lesson.name,
                    "absenteeism": grade.absenteeism_count
                }
                for student, grade, lesson in results
            ]
        }
        
    # --- ACTION 3: Course Evaluation Grade Performance Filtration ---
    elif action == "filter_grade":
        lesson_name = parsed.get("lesson_name")
        threshold = parsed.get("threshold")
        operator = parsed.get("operator", "gt")

        if lesson_name is None or threshold is None:
            raise HTTPException(status_code=400, detail="AI could not extract valid filters.")

        op_map = {
            "gt": models.Grade.grade_value > threshold,
            "lt": models.Grade.grade_value < threshold,
            "gte": models.Grade.grade_value >= threshold,
            "lte": models.Grade.grade_value <= threshold,
        }
        condition = op_map.get(operator, models.Grade.grade_value > threshold)

        results = (
            db.query(models.Student, models.Grade, models.Lesson)
            .join(models.Grade, models.Student.id == models.Grade.student_id)
            .join(models.Lesson, models.Grade.lesson_id == models.Lesson.id)
            .filter(models.Lesson.name == lesson_name)
            .filter(condition)
            .all()
        )

        return {
            "action": action,
            "parsed_filter": parsed,
            "results": [
                {
                    "student_id": student.id,
                    "name": student.name,
                    "surname": student.surname,
                    "lesson_name": lesson.name,
                    "grade_value": grade.grade_value,
                    "grade_type": grade.grade_type
                }
                for student, grade, lesson in results
            ]
        }

    # --- FALLBACK: Unresolved NLP Query Parameters ---
    else:
        return {
            "action": "unknown",
            "parsed_filter": parsed,
            "results": [],
            "message": "Could not understand the query. Please try phrasing like 'top 5 students by GPA'."
        }
    

@router.post("/chat")
def student_chat(
    body: dict,
    db: Session = Depends(get_db),
    current_user: schemas.TokenData = Depends(auth.get_current_user)
):
    """
    Student-facing AI Mentor assistant built on a secure Context Injection interface layout.
    Loads transcript snapshots from storage maps to feed real-time conversational responses.
    """
    from app import models
    from app.services.ai_service import generate_chatbot_response

    # Enforce clear identity tier usage limits
    if current_user.role != "student":
        raise HTTPException(
            status_code=403,
            detail="This endpoint is only available for students."
        )

    user_message = body.get("message", "").strip()
    if not user_message:
        raise HTTPException(status_code=400, detail="'message' field cannot be empty.")

    # Match system reference maps using current auth tokens tokens data maps
    student = db.query(models.Student).filter(
        models.Student.user_id == current_user.user_id
    ).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found.")

    # Fetch foundational grade history context entries
    transcript = crud.get_student_transcript(db, student_id=student.id)
    if not transcript:
        raise HTTPException(status_code=404, detail="No academic records found for your account.")

    # Calculate real-time cumulative GPA thresholds over verified entries
    visible_grades = [item['grade_value'] for item in transcript if item.get('grade_type') != 'Enrollment']
    calculated_gpa = round(sum(visible_grades) / len(visible_grades), 1) if visible_grades else 0.0

    full_name = f"{student.name} {student.surname}"
    response = generate_chatbot_response(
        user_message=user_message,
        transcript_data=transcript,
        student_name=full_name,
        current_gpa=calculated_gpa
    )

    return {
        "student_id": student.id,
        "message": user_message,
        "response": response
    }