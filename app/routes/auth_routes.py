from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user_model import User
from app.schemas.user_schema import UserRegister

from app.auth.auth_handler import (
    hash_password,
    verify_password
)

from app.auth.jwt_handler import create_access_token

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post("/register")
def register(
    user: UserRegister,
    db: Session = Depends(get_db)
):

    existing_user = db.query(User).filter(
        (User.email == user.email) |
        (User.username == user.username)
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email or Username already registered"
        )

    hashed_password = hash_password(user.password)

    new_user = User(
        username=user.username,
        email=user.email,
        password=hashed_password,
        role="client"
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "User registered successfully"
    }


@router.post("/login")
def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):

    existing_user = db.query(User).filter(
        (User.email == form_data.username) |
        (User.username == form_data.username)
    ).first()

    if not existing_user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    valid_password = verify_password(
        form_data.password,
        existing_user.password
    )

    if not valid_password:
        raise HTTPException(
            status_code=401,
            detail="Invalid password"
        )

    token = create_access_token(
        data={
            "user_id": existing_user.id,
            "role": existing_user.role
        }
    )

    dashboard = ""

    if existing_user.role == "admin":
        dashboard = "/admin/dashboard"

    elif existing_user.role == "client":
        dashboard = "/client/dashboard"

    elif existing_user.role == "analyst":
        dashboard = "/analyst/dashboard"

    elif existing_user.role == "auditor":
        dashboard = "/auditor/dashboard"

    return {
        "access_token": token,
        "token_type": "bearer",
        "role": existing_user.role,
        "redirect_url": dashboard
    }
