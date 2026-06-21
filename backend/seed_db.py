import random
from app.database import SessionLocal, engine, Base
from app import models

db = SessionLocal()


def seed_data():
    print("✨ Enterprise MiniLMS Data Seeding Pipeline Initiated...")
    # Synchronize and ensure all physical database structures exist in SQL Server
    Base.metadata.create_all(bind=engine)
    
    try:
        # 1) Validate existence of primary Teacher identity
        teacher_user = db.query(models.User).filter(models.User.username == "kagan").first()
        if not teacher_user:
            raise ValueError("Core identity 'kagan' (Teacher) not found. Please execute user registration first.")

        # 2) Validate existence of primary Student identity
        eda_user = db.query(models.User).filter(models.User.username == "eda").first()
        if not eda_user:
            raise ValueError("Core identity 'eda' (Student) not found. Please execute user registration first.")

        # 3) Orchestrate and provision structured courses for the faculty member
        lesson_specs = [
            {"name": "Database Systems", "code": "CENG330"},
            {"name": "Web Development", "code": "CENG350"},
            {"name": "Artificial Intelligence Basics", "code": "CENG470"},
        ]

        lessons = []
        for spec in lesson_specs:
            lesson = (
                db.query(models.Lesson)
                .filter(models.Lesson.code == spec["code"])
                .first()
            )
            if not lesson:
                lesson = models.Lesson(
                    name=spec["name"],
                    code=spec["code"],
                    teacher_id=teacher_user.id,
                )
                db.add(lesson)
                db.commit()
                db.refresh(lesson)
            lessons.append(lesson)

        # 4) Resolve target authentication ledgers for 'eda' and batch accounts user_0 through user_10
        target_usernames = ["eda"] + [f"user_{i}" for i in range(11)]
        target_users = db.query(models.User).filter(models.User.username.in_(target_usernames)).all()

        students_to_enroll = []
        missing_students = []
        
        for user in target_users:
            student = db.query(models.Student).filter(models.Student.user_id == user.id).first()
            if student:
                students_to_enroll.append(student)
            else:
                missing_students.append(user.username)

        # 5) Populate polymorphic grade matrices and distribute absenteeism telemetry
        total_inserted = 0
        total_updated = 0
        grade_types = ["Midterm", "Final"]

        for student in students_to_enroll:
            for lesson in lessons:
                # Generate realistic grade data distributions to properly feed cognitive AI analytical modules
                random_grade = round(random.uniform(35.0, 98.5), 1)
                
                # Enforce diverse absenteeism metrics to intentionally trigger at-risk thresholds for the AI Study Guide testing matrix
                random_absenteeism = random.choice([1, 2, 3, 4, 8, 12]) if student.user.username != "eda" else 2
                random_grade_type = random.choice(grade_types)

                existing_grade = (
                    db.query(models.Grade)
                    .filter(models.Grade.student_id == student.id, models.Grade.lesson_id == lesson.id)
                    .first()
                )

                if existing_grade:
                    existing_grade.grade_value = random_grade
                    existing_grade.absenteeism_count = random_absenteeism
                    existing_grade.grade_type = random_grade_type
                    total_updated += 1
                else:
                    new_grade = models.Grade(
                        student_id=student.id,
                        lesson_id=lesson.id,
                        grade_value=random_grade,
                        grade_type=random_grade_type,
                        absenteeism_count=random_absenteeism,
                    )
                    db.add(new_grade)
                    total_inserted += 1

        db.commit()

        print("✓ Database seeding pipeline completed successfully.")
        print(f"✓ Active Faculty Instructor: {teacher_user.username} (id={teacher_user.id})")
        print(f"✓ Active Academic Curriculum: {[lesson.code for lesson in lessons]}")
        print(f"✓ Total Enrolled Student Profiles Processed: {len(students_to_enroll)}")
        print(f"✓ Ledger Records State -> Inserted: {total_inserted}, Updated: {total_updated}")
        
        if missing_students:
            print(f"⚠️ Warning: User entries resolved without corresponding Student records: {missing_students}")

    except Exception as e:
        print(f"⚠️ Execution failed. Rolling back database transaction state. Error: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_data()