from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, UserRole
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
