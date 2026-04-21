#schemas.py: APIye disaridan gelecek veya APIdan gidecek verilerin tip kontrolu(Pydantic)
from pydantic import BaseModel, Field, EmailStr  #field: check kismi gibi
from typing import Optional, List

#kullanici ve auth semalari

class UserCreate(BaseModel):
    username: str
    password: str
    role: str  #admin, teacher, student

class UserResponse(BaseModel):
    id: int
    username: str
    role: str

    class Config:
        from_attributes = True

#kullanicinin giris yaparken gonderecegi bilgiler
class Token(BaseModel):
    access_token: str
    token_type: str

#token icinden cikacak veriler
class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None

#ogrenci semalari

#Ogrenci olustururken bekledigimiz veriler
class StudentCreate(BaseModel): #basemodel: bu sinif bir pydantic modeldir, icindekileri kontrol et diyor
    name: str
    surname: str
    email: EmailStr
    student_number: str #fastapi de tip belirleme kullaniyoruz
    user_id: int #her ogrenci bir user ile bagli olmali

#API den ogrenci bilgisi donerken kullanilacak model
class StudentResponse(StudentCreate): #inheritance(kalitim): parantez icinde baska sinif
    id: int  #ogrenciyi ekrandan geri okurken(GET) studentcreatee ek olarak db nin verdigi id yi istersin
#studentresponse icine tekrar isim soyisim yazmamak icin. studentcreati al üstüne id ekle
    class Config: #nested(ic ice) sinif, verinin nasil davranacagini soyler
        from_attributes = True #SQLAlchemy modelleriyle calismasi icin

#ders semalari
class LessonCreate(BaseModel):
    name: str
    code: str
    teacher_id: int


class LessonResponse(LessonCreate):
    id: int

    class Config:
        from_attributes = True

#not semalari

#Not girisi icin model(is kurallarini burada uyguluyoruz)
class GradeCreate(BaseModel):
    student_id: int
    lesson_id: int
    grade_value: float = Field(ge=0, le=100, description="Not degeri 0-100 arasinda olmalidir.") #not 0-100 arasi olmali
    grade_type: str #odev mi quiz mi?
    absenteeism_count: int = Field(ge=0, description="Devamsizlik sayisi 0 veya daha yuksek olmalidir.")

class GradeUpdate(BaseModel):
    grade_value: Optional[float] = Field(ge=0, le=100, description="Not degeri 0-100 arasinda olmalidir.")
    absenteeism_count: Optional[int] = Field(ge=0, description="Devamsizlik sayisi 0 veya daha yuksek olmalidir.")

#notun geri donus modeli(Response)
class GradeResponse(BaseModel):
    id: int
    student_id: int
    lesson_id: int
    grade_value: float
    grade_type: str
    absenteeism_count: int

    class Config:
        from_attributes = True

#transkript ve rapor semasi

#transkript icin model
class TranscriptEntry(BaseModel):
    lesson_name: str
    grade: float
    status: str   #gecti veya kaldi

class StudentTranscript(BaseModel):
    student_name: str
    student_number: str
    grades: List[TranscriptEntry]




