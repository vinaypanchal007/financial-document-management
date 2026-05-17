from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user_model import User
from app.auth.rbac import role_required
from app.schemas.user_schema import RoleCreate, AssignRole


router = APIRouter(
    tags=["Roles & Permissions"]
)

VALID_ROLES = ["admin", "analyst", "auditor", "client"]

ROLE_PERMISSIONS = {
    "admin": [
        "manage_users",
        "assign_roles",
        "upload_documents",
        "delete_documents",
        "semantic_search",
        "system_control",
        "review_documents",
        "edit_documents"
    ],
    "analyst": [
        "upload_documents",
        "edit_documents",
        "semantic_search"
    ],
    "auditor": [
        "review_documents",
        "analyze_reports",
        "access_audit_info"
    ],
    "client": [
        "view_documents",
        "search_financial_reports"
    ]
}


@router.post("/roles/create")
def create_role(
    role: RoleCreate,
    current_user: User = Depends(role_required(["admin"]))
):

    if role.role_name not in VALID_ROLES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid role. Valid roles are: {VALID_ROLES}"
        )

    return {
        "message": f"Role '{role.role_name}' is available in the system",
        "role_name": role.role_name,
        "description": role.description,
        "permissions": ROLE_PERMISSIONS.get(role.role_name, [])
    }


@router.post("/users/assign-role")
def assign_role(
    data: AssignRole,
    db: Session = Depends(get_db),
    current_user: User = Depends(role_required(["admin"]))
):

    if data.role not in VALID_ROLES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid role. Valid roles are: {VALID_ROLES}"
        )

    user = db.query(User).filter(User.id == data.user_id).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    old_role = user.role
    user.role = data.role
    db.commit()
    db.refresh(user)

    return {
        "message": f"Role updated successfully",
        "user_id": user.id,
        "username": user.username,
        "old_role": old_role,
        "new_role": user.role
    }


@router.get("/users/{user_id}/roles")
def get_user_roles(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(role_required(["admin"]))
):

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return {
        "user_id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role
    }


@router.get("/users/{user_id}/permissions")
def get_user_permissions(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(role_required(["admin"]))
):

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    permissions = ROLE_PERMISSIONS.get(user.role, [])

    return {
        "user_id": user.id,
        "username": user.username,
        "role": user.role,
        "permissions": permissions
    }