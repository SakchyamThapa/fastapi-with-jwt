from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, UserRole,Blog, Category, Tag
from app.schemas import (
    UserResponse,
    UserUpdate,
    UserUpdateAdmin,
    MessageResponse,
    BlogCreate, BlogResponse
)
from app.user_role import hash_password, get_current_user, require_admin

router = APIRouter(prefix="/users", tags=["Users Blogs"])




@router.get("/me", response_model=UserResponse)
def get_my_profile(current_user: User = Depends(get_current_user)):
    """Get current user's profile"""
    return current_user


@router.put("/me", response_model=UserResponse)
def update_my_profile(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user's profile (cannot change role)"""
    # Check if new email is already taken
    if user_data.email and user_data.email != current_user.email:
        if db.query(User).filter(User.email == user_data.email).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        current_user.email = user_data.email
    
    if user_data.full_name is not None:
        current_user.full_name = user_data.full_name
    
    if user_data.password:
        current_user.hashed_password = hash_password(user_data.password)
    
    # Users cannot change their own is_active status or role
    
    db.commit()
    db.refresh(current_user)
    return current_user


# ==================== ADMIN ROUTES ====================

@router.get("/", response_model=List[UserResponse])
def list_all_users(
    skip: int = 0,
    limit: int = 100,
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """List all users (Admin only)"""
    users = db.query(User).offset(skip).limit(limit).all()
    return users


@router.get("/{user_id}", response_model=UserResponse)
def get_user_by_id(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific user by ID (User can only see their own, Admin can see all)"""
    # Regular users can only see their own profile
    if current_user.role != UserRole.ADMIN and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this user"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.put("/{user_id}", response_model=UserResponse)
def update_user_admin(
    user_id: int,
    user_data: UserUpdateAdmin,
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Update any user (Admin only)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if new email is already taken
    if user_data.email and user_data.email != user.email:
        if db.query(User).filter(User.email == user_data.email).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        user.email = user_data.email
    
    if user_data.full_name is not None:
        user.full_name = user_data.full_name
    
    if user_data.password:
        user.hashed_password = hash_password(user_data.password)
    
    if user_data.is_active is not None:
        user.is_active = user_data.is_active
    
    if user_data.role is not None:
        user.role = user_data.role
    
    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}", response_model=MessageResponse)
def delete_user(
    user_id: int,
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Soft delete a user - sets is_active to False (Admin only)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Prevent admin from deleting themselves
    if user.id == admin_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    # Soft delete - set is_active to False
    user.is_active = False
    db.commit()
    return {"message": f"User {user.email} has been deactivated"}



# List all blogs

@router.get("/blogs", response_model=List[BlogResponse])
def list_blogs(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """List all blogs with category and tags"""
    return db.query(Blog).all()

# Get single blog by ID

@router.get("/blogs/{blog_id}", response_model=BlogResponse)
def get_blog(blog_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    blog = db.query(Blog).get(blog_id)
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")
    return blog


# Create blog (existing category + tags only)

@router.post("/blogs", response_model=BlogResponse)
def create_blog(
    blog: BlogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # 🔐 only authenticated users
):

    category = db.query(Category).get(blog.category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")


    tags = []
    if blog.tag_ids:
        tags = db.query(Tag).filter(Tag.id.in_(blog.tag_ids)).all()
        # Ensure all requested tags exist
        if len(tags) != len(blog.tag_ids):
            raise HTTPException(status_code=400, detail="One or more tags not found")

   
    new_blog = Blog(
        title=blog.title,
        author=current_user.full_name or current_user.email,
        category=category
    )
    
    new_blog.tags = tags

  
    db.add(new_blog)
    db.commit()
    db.refresh(new_blog)

    return new_blog
