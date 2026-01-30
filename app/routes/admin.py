from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import Blog, Category, Tag, User,UserRole
from app.schemas import (
    BlogCreate, BlogUpdate, BlogResponse,
    CategoryCreate, CategoryUpdate, CategoryResponse,
    TagCreate, TagUpdate, TagResponse
)
from app.user_role import require_admin

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/dashboard")
def admin_dashboard(
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Admin dashboard with statistics (Admin only)"""
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    admin_count = db.query(User).filter(User.role == UserRole.ADMIN).count()
    user_count = db.query(User).filter(User.role == UserRole.USER).count()
    
    return {
        "message": f"Welcome Admin {admin_user.email}!",
        "statistics": {
            "total_users": total_users,
            "active_users": active_users,
            "inactive_users": total_users - active_users,
            "admin_count": admin_count,
            "user_count": user_count
        }
    }

@router.post("/categories", response_model=CategoryResponse)
def create_category(
    category: CategoryCreate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    existing = db.query(Category).filter(Category.name == category.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Category already exists")
    
    new_category = Category(name=category.name)
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return new_category

@router.get("/categories", response_model=List[CategoryResponse])
def get_categories(db: Session = Depends(get_db), admin_user: User = Depends(require_admin)):
    return db.query(Category).all()

@router.get("/categories/{category_id}", response_model=CategoryResponse)
def get_category(category_id: int, db: Session = Depends(get_db), admin_user: User = Depends(require_admin)):
    category = db.query(Category).get(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.put("/categories/{category_id}", response_model=CategoryResponse)
def update_category(category_id: int, category: CategoryUpdate, db: Session = Depends(get_db), admin_user: User = Depends(require_admin)):
    db_category = db.query(Category).get(category_id)
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    if category.name:
        db_category.name = category.name
    db.commit()
    db.refresh(db_category)
    return db_category

@router.delete("/categories/{category_id}")
def delete_category(category_id: int, db: Session = Depends(get_db), admin_user: User = Depends(require_admin)):
    db_category = db.query(Category).get(category_id)
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    db.delete(db_category)
    db.commit()
    return {"message": "Category deleted successfully"}




# Tag CRUD

@router.post("/tags", response_model=TagResponse)
def create_tag(tag: TagCreate, db: Session = Depends(get_db), admin_user: User = Depends(require_admin)):
    existing = db.query(Tag).filter(Tag.name == tag.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Tag already exists")
    new_tag = Tag(name=tag.name)
    db.add(new_tag)
    db.commit()
    db.refresh(new_tag)
    return new_tag

@router.get("/tags", response_model=List[TagResponse])
def get_tags(db: Session = Depends(get_db), admin_user: User = Depends(require_admin)):
    return db.query(Tag).all()

@router.get("/tags/{tag_id}", response_model=TagResponse)
def get_tag(tag_id: int, db: Session = Depends(get_db), admin_user: User = Depends(require_admin)):
    tag = db.query(Tag).get(tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    return tag

@router.put("/tags/{tag_id}", response_model=TagResponse)
def update_tag(tag_id: int, tag: TagUpdate, db: Session = Depends(get_db), admin_user: User = Depends(require_admin)):
    db_tag = db.query(Tag).get(tag_id)
    if not db_tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    if tag.name:
        db_tag.name = tag.name
    db.commit()
    db.refresh(db_tag)
    return db_tag

@router.delete("/tags/{tag_id}")
def delete_tag(tag_id: int, db: Session = Depends(get_db), admin_user: User = Depends(require_admin)):
    db_tag = db.query(Tag).get(tag_id)
    if not db_tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    db.delete(db_tag)
    db.commit()
    return {"message": "Tag deleted successfully"}



# Blog CRUD

@router.post("/blogs", response_model=BlogResponse)
def create_blog(blog: BlogCreate, db: Session = Depends(get_db), admin_user: User = Depends(require_admin))->BlogResponse:
    # Validate category
    category = db.query(Category).get(blog.category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Validate tags
    tags = db.query(Tag).filter(Tag.id.in_(blog.tag_ids)).all() if blog.tag_ids else []

    new_blog = Blog(
        title=blog.title,
        author=blog.author,
        category=category,
        tags=tags
    )
    db.add(new_blog)
    db.commit()

    db.refresh(new_blog)
    db.refresh(new_blog, attribute_names=["tags"])

    return new_blog


