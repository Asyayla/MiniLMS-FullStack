# projedeki is kurallari burada denetlenir.
# APIdan gelen verilerin mantikli olup olmadigini kontrol eder.
from fastapi import HTTPException, status

#pydantic(schemas) 0-100 kontrolunu yapiyor ama backend seviyesinde kontrol etmeliyiz
def validate_grade_value(grade_value: float | None):
    """Notun 0 ile 100 arasinda olup olmadigini kontrol eder."""
    if grade_value is None:
        return grade_value

    if grade_value < 0 or grade_value > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Hata: Not degeri 0 ile 100 arasinda olmalidir!",
        )
    return grade_value

def calculate_average(midterm: float, final: float, assignment: float = 0, quiz:float = 0):
    """Vize %30, Final %50, Odev %10, Quiz %10 etkili olacak sekilde toplam basari notunu hesaplar"""
    total = (midterm * 0.30) + (final * 0.50) + (assignment * 0.10) + (quiz * 0.10)
    return round(total, 2)

def check_absenteeism_limit(absenteeism_count: int, total_hours: int = 100):
    """Devamsizlik %30dan fazlaysa otomatik kalir kuralini denetler."""
    limit = total_hours * 0.30
    if absenteeism_count > limit:
        return True #limit asildi, kaldi
    return False #limit dahilinde

def verify_student_enrollment(enrolled_lessons: list, target_lesson_id: int):
    """Ogrenci derse kayitli degilse not girilemez kuralini denetler."""
    if target_lesson_id not in enrolled_lessons:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hata: Ogrenci bu derse kayitli degil, not girisi yapilamaz!"
        )
    return True

def check_duplicate_grade_entry(existing_grade_types: list, new_grade_type: str):
    """Aynı sinav tipi(midterm/final) icin ikinci not girilemez kuralini denetler"""
    if new_grade_type in existing_grade_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Hata: Bu ogrenci icin zaten bir '{new_grade_type}' notu sisteme girilmis!"
        )
    return True
