#ic oda, internete kapali kisim
#token uretme araci
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from app import schemas

SECRET_KEY = "staj_projesi_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

#swagger uideki authorize butonunun login endpointini bulabilmesi icin prefixle uyumlu olmali.
oauth2_schema = OAuth2PasswordBearer(tokenUrl="/auth/login")
#API in tokenlari hangi adresten okuyacagini soyluyoruz

def get_current_user(token: str = Depends(oauth2_schema)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Gecersiz veya suresi dolmus token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")  #rol bilgisini payloaddan aliyoruz
        user_id: int = payload.get("user_id")  #kullanici ID'sini payloaddan aliyoruz
        
        if username is None or role is None or user_id is None:  #erisim engelleniyor
            raise credentials_exception

        return schemas.TokenData(username=username, role=role, user_id=user_id)
    except JWTError:  #sadece token ile ilgili hatalari yakaladik diger olusabilen hatalarin token hatasi sayilmasi engellendi.
        raise credentials_exception

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()

    now = datetime.now(timezone.utc) #python 3.12+ standartlarina uygun utc zaman damgasi
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
