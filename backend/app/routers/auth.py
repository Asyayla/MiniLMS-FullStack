from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.services import auth 
from app.services.auth import hash_password

router = APIRouter(
    prefix="/auth",
    tags=["Entry Operations"],
)

@router.post("/login", response_model=schemas.Token)
def login_for_access_token(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends() 
):
    """
    Authenticates a user based on username and password, 
    then returns a signed JWT access token.
    """
    # Look up the user entity by username in the database
    user = db.query(models.User).filter(models.User.username == form_data.username).first()

    # Validate user existence and verify the hashed password
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username or password is incorrect.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Generate a signed JWT containing security claims: username, role, and user ID
    access_token = auth.create_access_token(
        data={
            "sub": user.username,
            "role": user.role,
            "user_id": user.id
            }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "role": user.role,
        "username": user.username
    }


@router.post("/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Registers a new unique user into the database after hashing their password.
    """
    # Prevent duplicate usernames within the system
    existing_user = db.query(models.User).filter(models.User.username == user.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This username is already registered in the system!",
        )

    # Secure the plain text password using cryptographic hashing
    hashed_pwd = hash_password(user.password)

    # Instantiate the new user model object
    new_user = models.User(
        username=user.username,
        hashed_password=hashed_pwd,
        role=user.role
    )

    # Persist the new user record into the database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

@router.put("/change-password")
def change_password(
    password_data: schemas.ChangePassword,
    db: Session = Depends(get_db),
    current_user: schemas.TokenData = Depends(auth.get_current_user)
):
    """
    Securely updates the password of an already authenticated current user.
    """
    # Fetch the logged-in user from the database context
    user = db.query(models.User).filter(models.User.id == current_user.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
        
    # Verify the old password before allowing changes
    if not auth.verify_password(password_data.current_password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Current password is incorrect.")
        
    # Hash the new password and commit changes to database state
    user.hashed_password = auth.hash_password(password_data.new_password)
    db.commit()
    return {"message": "Password changed successfully."}