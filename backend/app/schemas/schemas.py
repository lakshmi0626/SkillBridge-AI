from pydantic import BaseModel, EmailStr, Field, ConfigDict
class RegisterIn(BaseModel): name: str = Field(min_length=2, max_length=120); email: EmailStr; password: str = Field(min_length=8, max_length=72)
class LoginIn(BaseModel): email: EmailStr; password: str
class JobIn(BaseModel): title: str = Field(min_length=2, max_length=180); company: str | None = None; description: str = Field(min_length=30)
class UserOut(BaseModel): id: int; name: str; email: EmailStr; role: str; model_config = ConfigDict(from_attributes=True)
