from fastapi import HTTPException, status

def validate_grade_value(grade_value: float | None):
    """
    Validates that the provided grade entry falls strictly within the academic 
    score boundary limits of 0.0 and 100.0 inclusive.
    """
    if grade_value is None:
        return grade_value

    # Enforce standard academic grading constraints
    if grade_value < 0 or grade_value > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Validation Error: Grade value must be between 0 and 100 inclusive.",
        )
    return grade_value

def calculate_average(midterm: float, final: float, assignment: float = 0, quiz: float = 0):
    """
    Calculates the cumulative success grade using the standard institutional weights formula: 
    Midterm (30%), Final (50%), Assignment (10%), and Quiz (10%).
    """
    total = (midterm * 0.30) + (final * 0.50) + (assignment * 0.10) + (quiz * 0.10)
    return round(total, 2)

def check_absenteeism_limit(absenteeism_count: int, total_hours: int = 100):
    """
    Evaluates institutional attendance compliance criteria. 
    Returns True if the student's total absences exceed the allowed 30% limit.
    """
    limit = total_hours * 0.30
    if absenteeism_count > limit:
        return True 
    return False 

def verify_student_enrollment(enrolled_lessons: list, target_lesson_id: int):
    """
    Enforces systemic safety boundaries. 
    Guards against submitting evaluation scores for students not officially enrolled in a course.
    """
    if target_lesson_id not in enrolled_lessons:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access Denied: The student is not officially enrolled in this course context. Operation aborted."
        )
    return True

def check_duplicate_grade_entry(existing_grade_types: list, new_grade_type: str):
    """
    Enforces systemic idempotency guidelines. 
    Prevents assigning multiple redundant evaluation grades for the exact same assessment type category.
    """
    if new_grade_type in existing_grade_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Conflict Error: An evaluation score entry for type '{new_grade_type}' already exists for this student profile."
        )
    return True