#JWT authentication icin gerekli
#dis kapi, internete acik kisim
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.services import auth #guvenlik dosyasi
from app.services.auth import hash_password

router = APIRouter(
    prefix="/auth",
    tags=["Entry Operations"],
)

@router.post("/login", response_model=schemas.Token)
def login_for_access_token(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends() #kullanici adi ve sifreyi otomatik alir
):
    #1. kullaniciyi dbde ara
    user = db.query(models.User).filter(models.User.username == form_data.username).first()

    #2. sifre dogrulamasi ve hata kontrolu
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Kullanici adi veya sifre hatali.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    #3. her sey dogruysa kullaniciya ozel rol bilgisini de iceren JWT(bilet) olustur
    access_token = auth.create_access_token(
        data={"sub": user.username, "role": user.role}
    )

    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    #business logic: kullanici zaten var mi?
    existing_user = db.query(models.User).filter(models.User.username == user.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu kullanici adi zaten sistemde kayitli!",
        )

    #1. sifreyi hashle ve yeni kullaniciyi kaydet
    # hashlemek(bir veriyi sabit uzunlukta ve geri dondurulemez degere donustur)
    hashed_pwd = hash_password(user.password)

    #2. user objesi olustur
    new_user = models.User(
        username=user.username,
        hashed_password=hashed_pwd,
        role=user.role
    )

    #3. dbye kaydet
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user