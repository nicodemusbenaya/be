from pydantic import BaseModel, EmailStr, Field

class RegisterRequest(BaseModel):
    username: str 
    email: EmailStr
    password: str 
    confirm_password: str 

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    username: str

    class Config:
        orm_mode = True
