from pydantic import BaseModel, EmailStr, Field
from typing import Optional,List
from datetime import datetime
from app.models import UserRole


# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None
    role: Optional[str] = None


# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)


class UserCreateAdmin(UserCreate):
    role: UserRole = UserRole.USER


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = Field(None, min_length=6)
    is_active: Optional[bool] = None


class UserUpdateAdmin(UserUpdate):
    role: Optional[UserRole] = None


class UserResponse(UserBase):
    id: int
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str


# Message Response
class MessageResponse(BaseModel):
    message: str


#category Schemas

class CategoryBase(BaseModel):
    name: str = Field(..., max_length=100)


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)


class CategoryResponse(CategoryBase):
    id: int

    class Config:
        from_attributes = True

class TagBase(BaseModel):
    name: str = Field(..., max_length=100)


class TagCreate(TagBase):
    pass


class TagUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)


class TagResponse(TagBase):
    id: int

    class Config:
        from_attributes = True



#Blog Schemas
class BlogBase(BaseModel):
    title: str = Field(..., max_length=255)
    author: str = Field(..., max_length=255)
    category_id: int
    tag_ids: List[int] = []

class BlogCreate(BlogBase):
    pass


class BlogUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    author: Optional[str] = Field(None, max_length=255)
    category_id: Optional[int] = None
    tag_ids: Optional[List[int]] = None


class BlogResponse(BaseModel):
    id: int
    title: str
    author: str
    category: CategoryResponse
    tags: List[TagResponse]
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
