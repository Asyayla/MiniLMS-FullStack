import random
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app import models

db = SessionLocal()


def seed_data():
    print("Veri ekleme islemi baslatildi...")
    Base.metadata.create_all(bind=engine) #tablolari dbde fiziksel olustur.
    try:
        # 1. Test Ogretmeni ve Admin Kullanicisi Olustur
        test_teacher = models.User(username="hoca_ahmet", hashed_password="fake_password", role="teacher")
        db.add(test_teacher)
        db.commit()
        db.refresh(test_teacher)

        # 2. Test Dersi Olustur
        test_lesson = models.Lesson(name="Veri Yapilari", code="CENG201", teacher_id=test_teacher.id)
        db.add(test_lesson)
        db.commit()
        db.refresh(test_lesson)

        # 3. 1000 tane ogrenci ve bagli Kullanici olustur
        for i in range(1000):
            # Her ogrenci icin bir user kaydi sart
            new_user = models.User(username=f"user_{i}", hashed_password="pw", role="student")
            db.add(new_user)
            db.commit()
            db.refresh(new_user)

            new_student = models.Student(
                user_id=new_user.id,
                name=f"Ogrenci_Ad_{i}",
                surname=f"Soyad_{i}",
                email=f"ogrenci_{i}@iauegitim.com",
                student_number=f"202600{i}"
            )
            db.add(new_student)
            db.commit()
            db.refresh(new_student)

            # Her ogrenciye rastgele bir not ve devamsizlik ekle
            new_grade = models.Grade(
                student_id=new_student.id,
                lesson_id=test_lesson.id,
                grade_value=float(random.randint(0, 100)),
                grade_type="vize",
                absenteeism_count=random.randint(0, 15)
            )
            db.add(new_grade)

        db.commit()
        print("1000 kayit basariyla eklendi! Performans testi icin hazir.")

    except Exception as e:
        print(f"Hata olustu: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_data()