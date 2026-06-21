from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app import crud, schemas
from app.services import auth


router = APIRouter(
    prefix="/grades", 
    tags=["Grade Operations"], 
)

@router.post("/", response_model=schemas.GradeResponse)
def create_grade(
    grade: schemas.GradeCreate,
    db: Session = Depends(get_db),
    current_user: schemas.TokenData = Depends(auth.get_current_user)
):
    """
    Submits a new grade evaluation record for a student.
    Strictly restricted to users with 'teacher' or 'admin' roles.
    """
    # Role-based access control checking
    if current_user.role not in ["teacher", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission for this operation. Only teachers or administrators can submit grades.",
        )
        
    return crud.create_grade(db=db, grade_in=grade)


@router.put("/{id}", response_model=schemas.GradeResponse)
def update_grade(
    id: int,
    grade_update: schemas.GradeUpdate,
    db: Session = Depends(get_db),
    current_user: schemas.TokenData = Depends(auth.get_current_user)
):
    """
    Updates an existing grade or absenteeism entry by its unique identifier.
    Strictly restricted to users with 'teacher' or 'admin' roles.
    """
    # Role-based access control checking
    if current_user.role not in ["teacher", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission for this operation.",
        )

    # Execute the update operation within the database session context
    db_grade = crud.update_grade(db=db, grade_id=id, grade_update=grade_update)
    if not db_grade:
        raise HTTPException(status_code=404, detail="Grade not found.")

    return db_grade