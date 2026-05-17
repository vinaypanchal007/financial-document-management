from fastapi import APIRouter, Depends

from app.models.user_model import User

from app.auth.rbac import role_required


router = APIRouter(
    tags=["Dashboards"]
)

@router.get("/admin/dashboard")
def admin_dashboard(
    current_user: User = Depends(
        role_required(["admin"])
    )
):
    return {
        "message": f"Welcome Admin {current_user.username}",
        "role": current_user.role,
        "access_level": "Full Access",
        "permissions": [
            "Manage Users",
            "Assign Roles",
            "Upload Documents",
            "Delete Documents",
            "Semantic Search",
            "System Control"
        ]
    }

@router.get("/client/dashboard")
def client_dashboard(
    current_user: User = Depends(
        role_required(["client"])
    )
):
    return {
        "message": f"Welcome Client {current_user.username}",
        "role": current_user.role,
        "access_level": "Limited Access",
        "permissions": [
            "View Company Documents",
            "Search Financial Reports"
        ]
    }

@router.get("/analyst/dashboard")
def analyst_dashboard(
    current_user: User = Depends(
        role_required(["admin", "analyst"])
    )
):
    return {
        "message": f"Welcome Financial Analyst {current_user.username}",
        "role": current_user.role,
        "access_level": "Document Management Access",
        "permissions": [
            "Upload Documents",
            "Edit Financial Documents",
            "Perform Semantic Search"
        ]
    }

@router.get("/auditor/dashboard")
def auditor_dashboard(
    current_user: User = Depends(
        role_required(["auditor"])
    )
):
    return {
        "message": f"Welcome Auditor {current_user.username}",
        "role": current_user.role,
        "access_level": "Review Access",
        "permissions": [
            "Review Financial Documents",
            "Analyze Reports",
            "Access Audit Information"
        ]
    }