from pydantic import BaseModel, EmailStr

class UserAuth(BaseModel):
    username: str
    password: str

class UserCreate(BaseModel):
    username: EmailStr
    password: str