from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, SessionLocal, Base
from app.models import User, UserRole
from app.config import settings
from app.user_role import hash_password
from app.routes import auth, users, admin


# Create tables
Base.metadata.create_all(bind=engine)

# Create default admin user if not exists
db = SessionLocal()
try:
    existing_admin = db.query(User).filter(User.email == settings.ADMIN_EMAIL).first()
    if not existing_admin:
        admin_user = User(
            email=settings.ADMIN_EMAIL,
            hashed_password=hash_password(settings.ADMIN_PASSWORD),
            full_name="System Administrator",
            role="admin",
            is_active=True
        )
        db.add(admin_user)
        db.commit()
        print(f"Admin user created: {settings.ADMIN_EMAIL}")
    else:
        print(f"Admin user already exists: {settings.ADMIN_EMAIL}")
finally:
    db.close()


app = FastAPI(
    title="My FastAPI Application"
)


# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(admin.router)


@app.get("/", tags=["Root"])
def root():
    return {"status": "API is running",}


