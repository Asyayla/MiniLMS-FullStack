#disaridan gelen su ogrenciye su notu gir istegini alir
#logic.py daki kurallara sorar sorun yoksa crud.py uzerinden dbye kaydeder
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app import crud, schemas
from app.services import auth

#router tanimlama
router = APIRouter(
    prefix="/grades", #bu dosyadaki tum adresler /not ile baslar
    tags=["Grade Operations"], #swagger(dokumantasyon) sayfasinda bu baslikla gorunur
)

#1. not girisi yapma(POST /grades)
@router.post("/", response_model=schemas.GradeResponse)
def create_grade(
    grade: schemas.GradeCreate,
    db: Session = Depends(get_db),
    current_user: schemas.TokenData = Depends(auth.get_current_user)
):
    #yetki kontrolu
    if current_user.role not in ["teacher","admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission for this operation. Only teachers or administrators can submit grades.",
        )
    return crud.create_grade(db=db, grade_in=grade)

#2. Not guncelleme (PUT /grades/{id})
@router.put("/{id}", response_model=schemas.GradeResponse)
def update_grade(
    id: int,
    grade_update: schemas.GradeUpdate,
    db: Session = Depends(get_db),
    current_user: schemas.TokenData = Depends(auth.get_current_user)
):
    #yetki kontrolu
    if current_user.role not in ["teacher","admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission for this operation.",
        )

    #guncelleme islemi
    db_grade = crud.update_grade(db=db, grade_id=id, grade_update=grade_update)
    if not db_grade:
        raise HTTPException(status_code=404, detail="Grade not found.")

    return db_grade
