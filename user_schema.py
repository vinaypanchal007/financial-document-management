from pydantic import BaseModel, EmailStr


class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class RoleCreate(BaseModel):
    role_name: str
    description: str = ""


class AssignRole(BaseModel):
    user_id: int
    role: str