#models.py: db tablolarinin pythondaki karsiligi(SQLAlchemy(ORM))
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

#kullanici ve rol yonetimi
#JWT tabanli authentication ve rol bazli erisim icin
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(150), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False) # "admin", "teacher", "student"

#ogrenci tablosu
class Student(Base):
    __tablename__ = 'students' #sql: create table students
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False) #her ogrenci bir kullanicidir
    name = Column(String(100))
    surname = Column(String(100))
    email = Column(String(150), unique=True, index=True)
    student_number = Column(String(50), unique=True, index=True)

    grades = relationship("Grade", back_populates="student")

#ders tablosu
class Lesson(Base):
    __tablename__ = 'lessons'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    code = Column(String(50), unique=True, index=True, nullable=False) #ornek: MAT101
    teacher_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    grades = relationship("Grade", back_populates="lesson") #grade sinifindaki lesson ile konusabilmesi icin

#not tablosu
class Grade(Base):
    __tablename__ = 'grades'
    id = Column(Integer, primary_key=True, index=True)
    #foreign key: hangi ogrenci ve hangi ders?
    student_id = Column(Integer, ForeignKey('students.id'))
    lesson_id = Column(Integer, ForeignKey('lessons.id'))
    grade_value = Column(Float)
    grade_type = Column(String(50)) #SQL: type VARCHAR  (vize, final ,odev, quiz)
    absenteeism_count = Column(Integer, default=0) #devamsizlik takibi

    student = relationship("Student", back_populates="grades")
    lesson = relationship("Lesson", back_populates="grades")

