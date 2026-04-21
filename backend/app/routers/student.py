#logic: is kurallari, projenin beyni.
#bu beyni dis dunyaya baglayan da main ve routers.
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import crud, schemas, database
from typing import List

router = APIRouter(
    prefix="/students",
    tags=["Student Operations"],
)

#db baglantisini her istekte acip kapatan yardimci fonksiyon
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

#1. yeni ogrenci olusturma(POST /ogrenci)
@router.post("/", response_model=schemas.StudentResponse)
def create_student(student: schemas.StudentCreate, db: Session = Depends(get_db)):
    return crud.create_student(db=db, student=student)

#2. id ile ogrenci getirme(GET /student{id})
@router.get("/{id}", response_model=schemas.StudentResponse)
def read_student(id: int, db: Session = Depends(get_db)): #dependency injection
    db_student = crud.get_student(db, student_id=id)
    if db_student is None:
        raise HTTPException(status_code=404, detail="Ogrenci bulunamadi")
    return db_student

#3. Get Student Transaction (GET /student/{id}/transcript)
@router.get("/{id}/transcript")
def read_student_transcript(id: int, db: Session = Depends(get_db)):
    #bu fonksiyon ogrencinin notlarini cekip %30 devamsizlik kurallarina gore gecti/kaldi hesaplar.
    transcript = crud.get_student_transcript(db, student_id=id)
    if not transcript:
        raise HTTPException(status_code=404, detail="Transcript veya not bulunamadi")
    return transcript


