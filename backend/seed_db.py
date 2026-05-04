import random
from app.database import SessionLocal, engine, Base
from app import models

db = SessionLocal()


def seed_data():
    print("Veri ekleme islemi baslatildi...")
    Base.metadata.create_all(bind=engine)  # tablolari dbde fiziksel olustur.
    try:
        
        teacher_user = db.query(models.User).filter(models.User.username == "kagan").first()
        if not teacher_user:
            raise ValueError("'kagan' kullanicisi bulunamadi. Lutfen once bu kullaniciyi olusturun.")

        
        eda_user = db.query(models.User).filter(models.User.username == "eda").first()
        if not eda_user:
            raise ValueError("'eda' kullanicisi bulunamadi. Lutfen once bu kullaniciyi olusturun.")

        eda_student = db.query(models.Student).filter(models.Student.user_id == eda_user.id).first()
        if not eda_student:
            raise ValueError("'eda' kullanicisi icin Student kaydi bulunamadi.")

        # 3) 'kagan' kullanicisina 2 yeni ders ata (varsa tekrar olusturma)
        lesson_specs = [
            {"name": "Database Systems", "code": "CENG330"},
            {"name": "Web Dev", "code": "CENG350"},
        ]

        lessons = []
        for spec in lesson_specs:
            lesson = (
                db.query(models.Lesson)
                .filter(models.Lesson.code == spec["code"], models.Lesson.teacher_id == teacher_user.id)
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

        # 4) 'eda' + user_0...user_10 ogrencilerini bul
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

        # 5) Her hedef ogrenciyi bu iki derse kaydet + random grade/devamsizlik ata
        total_inserted = 0
        total_updated = 0
        grade_types = ["Midterm", "Final"]

        for student in students_to_enroll:
            for lesson in lessons:
                existing_grade = (
                    db.query(models.Grade)
                    .filter(models.Grade.student_id == student.id, models.Grade.lesson_id == lesson.id)
                    .first()
                )

                random_grade = float(random.randint(0, 100))
                random_absenteeism = random.randint(0, 15)
                random_grade_type = random.choice(grade_types)

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

        print("Seed islemi tamamlandi.")
        print(f"Ogretmen: {teacher_user.username} (id={teacher_user.id})")
        print(f"Dersler: {[lesson.name for lesson in lessons]}")
        print(f"Kayitlanan ogrenci sayisi: {len(students_to_enroll)}")
        print(f"Yeni grade kaydi: {total_inserted}, guncellenen grade kaydi: {total_updated}")
        if missing_students:
            print(f"Student kaydi bulunamayan kullanicilar: {missing_students}")

    except Exception as e:
        print(f"Hata olustu: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_data()