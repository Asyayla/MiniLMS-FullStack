from pydantic import BaseModel, Field, EmailStr  
from typing import Optional, List


class UserCreate(BaseModel):
    """
    Schema for processing initial user registration payloads.
    """
    username: str
    password: str
    role: str  


class UserResponse(BaseModel):
    """
    Schema for returning sanitized user account profiles.
    """
    id: int
    username: str
    role: str

    class Config:
        from_attributes = True


class Token(BaseModel):
    """
    Schema representing a successful authentication token response package.
    """
    access_token: str
    token_type: str
    user_id: int
    role: str
    username: str


class TokenData(BaseModel):
    """
    Internal container schema for carrying unpacked security claims from decrypted JWT payloads.
    """
    user_id: Optional[int] = None
    username: Optional[str] = None
    role: Optional[str] = None


class StudentCreate(BaseModel): 
    """
    Base validation schema for capturing new student operational profile inputs.
    """
    name: str
    surname: str
    email: EmailStr
    student_number: str 
    user_id: int 


class StudentResponse(StudentCreate): 
    """
    Data transmission schema for returning student records.
    Inherits structural attributes from StudentCreate and appends the database ID key.
    """
    id: int  

    class Config: 
        from_attributes = True  # Enables seamless parsing from SQLAlchemy ORM entities


class LessonCreate(BaseModel):
    """
    Validation schema for establishing new institutional course listings.
    """
    name: str
    code: str
    teacher_id: int


class LessonResponse(LessonCreate):
    """
    Data transmission schema for returning populated lesson data representations.
    """
    id: int

    class Config:
        from_attributes = True


class GradeCreate(BaseModel):
    """
    Validation schema enforcing input boundary safety metrics over grade submissions.
    """
    student_id: int
    lesson_id: int
    grade_value: float = Field(ge=0, le=100, description="Grade entry must fall within the range of 0.0 to 100.0 inclusive.") 
    grade_type: str  # Evaluation category archetypes: "Midterm", "Final", "Quiz", "Homework", etc.
    absenteeism_count: int = Field(ge=0, description="Absenteeism metrics count must be a non-negative integer value.")


class GradeUpdate(BaseModel):
    """
    Validation schema handling partial updates over evaluation items safely.
    """
    grade_value: Optional[float] = Field(ge=0, le=100, description="Grade entry must fall within the range of 0.0 to 100.0 inclusive.")
    absenteeism_count: Optional[int] = Field(ge=0, description="Absenteeism metrics count must be a non-negative integer value.")


class GradeResponse(BaseModel):
    """
    Data transmission schema for downstream evaluation grade record reads.
    """
    id: int
    student_id: int
    lesson_id: int
    grade_value: float
    grade_type: str
    absenteeism_count: int

    class Config:
        from_attributes = True


class TranscriptEntry(BaseModel):
    """
    Data transfer sub-schema mapping single course records for transcript compiling actions.
    """
    lesson_name: str
    grade: float
    status: str   # Evaluation binary mappings outcomes: "Passed" or "Failed"


class StudentTranscript(BaseModel):
    """
    Aggregated document presentation schema structuring complete student academic transcripts records listings.
    """
    student_name: str
    student_number: str
    grades: List[TranscriptEntry]


class ChangePassword(BaseModel):
    """
    Security validation schema for executing password rotation request operations.
    """
    current_password: str
    new_password: str