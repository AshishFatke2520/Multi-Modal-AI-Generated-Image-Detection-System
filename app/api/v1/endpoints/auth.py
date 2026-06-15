from datetime import timedelta
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from app.core.database import db
from app.core.security import get_password_hash, verify_password, create_access_token
from app.schemas.user import UserCreate, UserResponse, Token
from app.core.config import settings

router = APIRouter()

@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate):
    # Check if user exists
    existing_user = await db.db.users.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash password and create user
    hashed_pass = get_password_hash(user.password)
    user_dict = {
        "email": user.email,
        "hashed_password": hashed_pass
    }
    
    new_user = await db.db.users.insert_one(user_dict)
    
    return UserResponse(
        id=str(new_user.inserted_id), 
        email=user.email
    )

@router.post("/login", response_model=Token)
async def login(form_data: UserCreate): # Using UserCreate for JSON body, standard is OAuth2PasswordRequestForm
    # We allow JSON body login
    email = form_data.email
    password = form_data.password
    
    user = await db.db.users.find_one({"email": email})
    if not user or not verify_password(password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["email"]}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}
