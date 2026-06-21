from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    """
    Represents the fundamental authentication and identity layer.
    Governs JWT-based authentication and handles strict role-based access control (RBAC).
    """
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(150), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False)  # Systems access tiers: "admin", "teacher", "student"


class Student(Base):
    """
    Represents the operational student registry profile directory.
    Maintains structural relational foreign key mappings back to the identity domain.
    """
    __tablename__ = 'students'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)  # Enforces a strict one-to-one identity bond
    name = Column(String(100))
    surname = Column(String(100))
    email = Column(String(150), unique=True, index=True)
    student_number = Column(String(50), unique=True, index=True)

    # Establish relational bidirectional connection mapping to evaluation grade schemas
    grades = relationship("Grade", back_populates="student")


class Lesson(Base):
    """
    Represents academic course definitions within the learning ecosystem.
    Binds courses directly to an instructor tracking profile context.
    """
    __tablename__ = 'lessons'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    code = Column(String(50), unique=True, index=True, nullable=False) 
    teacher_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Establish relational bidirectional connection mapping to evaluation grade schemas
    grades = relationship("Grade", back_populates="lesson")


class Grade(Base):
    """
    The intermediate transactional model acting as a multi-tier link.
    Tracks structural student evaluation parameters alongside course absenteeism metrics.
    """
    __tablename__ = 'grades'
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey('students.id'))
    lesson_id = Column(Integer, ForeignKey('lessons.id'))
    grade_value = Column(Float)
    grade_type = Column(String(50))  # Evaluation archetypes: "Midterm", "Final", "Quiz", "Homework", "Enrollment"
    absenteeism_count = Column(Integer, default=0) 

    # Operational mapping relationships back-populates configurations
    student = relationship("Student", back_populates="grades")
    lesson = relationship("Lesson", back_populates="grades")