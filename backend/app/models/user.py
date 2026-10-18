from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from sqlalchemy.orm import relationship
from app.core.database import Base


class User(Base):
    """
    User entity representing system actors (USER, ANALYST, ADMIN).
    Enforces secure credential management, role-based authorization, and activity auditing.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    name = Column(String(100), nullable=True)  # Backward-compatible alias for existing code
    role = Column(String(20), default="USER", nullable=False)  # 'USER', 'ANALYST', 'ADMIN'
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    # Relationships
    documents = relationship(
        "Document",
        back_populates="user",
        cascade="all, delete-orphan",
        foreign_keys="Document.user_id"
    )
    audit_logs = relationship(
        "AuditLog",
        back_populates="user",
        cascade="all, delete-orphan",
        foreign_keys="AuditLog.user_id"
    )

    def __init__(self, **kwargs):
        # Support name and full_name interchangeably
        if "full_name" in kwargs and "name" not in kwargs:
            kwargs["name"] = kwargs["full_name"]
        elif "name" in kwargs and "full_name" not in kwargs:
            kwargs["full_name"] = kwargs["name"]
        
        # If username not provided, derive from email or name
        if "username" not in kwargs:
            if "email" in kwargs and kwargs["email"]:
                kwargs["username"] = kwargs["email"].split("@")[0]
            elif "full_name" in kwargs and kwargs["full_name"]:
                kwargs["username"] = kwargs["full_name"].lower().replace(" ", "_")
        
        # Normalize role to uppercase
        if "role" in kwargs and kwargs["role"]:
            kwargs["role"] = kwargs["role"].upper()

        super().__init__(**kwargs)

    def __repr__(self) -> str:
        return f"<User id={self.id} username='{self.username}' email='{self.email}' role='{self.role}'>"
