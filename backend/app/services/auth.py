from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from app import schemas

# Core JWT cryptographic configuration constants
SECRET_KEY = "staj_projesi_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Initialize passlib context with bcrypt hashing algorithm for secure storage
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Extract the Bearer token directly from the Authorization header gateway mapping
oauth2_schema = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(token: str = Depends(oauth2_schema)):
    """
    Decodes, validates, and unpacks security claims from the incoming bearer JWT.
    Injects a structured TokenData instance into protected route handlers.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials. Token is invalid or expired.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Decode the signed token structure securely using the symmetric system key
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")  
        user_id: int = payload.get("user_id")  
        
        # Enforce validation constraint guards over critical identity attributes
        if username is None or role is None or user_id is None:  
            raise credentials_exception

        return schemas.TokenData(username=username, role=role, user_id=user_id)
    except JWTError:  
        raise credentials_exception

def hash_password(password: str):
    """
    Generates a secure cryptographic salted hash from a plain text string.
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    """
    Verifies a plain text candidate password against an existing cryptographic database hash.
    """
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    """
    Encodes data dictionary payloads into a signed JWT string with explicit expiration boundaries.
    """
    to_encode = data.copy()

    # Enforce timezone-aware expiration delta stamps using absolute UTC tracking configurations
    now = datetime.now(timezone.utc) 
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    # Inject the token expiration timestamp property field claim structure
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt