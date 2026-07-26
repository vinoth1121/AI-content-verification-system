"""Admin router: platform-wide analytics & user management (admin-only)."""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.deps import AdminUser, DbSession
from app.models.scan import Scan, ScanModality, ScanStatus
from app.models.user import User, UserRole

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/stats")
def stats(db: DbSession, _: AdminUser):
    """Platform-wide KPIs for the admin dashboard."""
    total_users = db.scalar(select(func.count(User.id))) or 0
    total_scans = db.scalar(select(func.count(Scan.id))) or 0
    completed = db.scalar(select(func.count(Scan.id)).where(Scan.status == ScanStatus.completed)) or 0
    failed = db.scalar(select(func.count(Scan.id)).where(Scan.status == ScanStatus.failed)) or 0

    by_modality = {}
    for m in ScanModality:
        by_modality[m.value] = db.scalar(select(func.count(Scan.id)).where(Scan.modality == m)) or 0

    # Confidence averages per modality
    avg_conf = {}
    for m in ScanModality:
        avg = db.scalar(select(func.avg(Scan.confidence)).where(Scan.modality == m, Scan.confidence.isnot(None)))
        avg_conf[m.value] = round(float(avg), 4) if avg else 0.0

    # Label distribution
    label_rows = db.execute(
        select(Scan.label, func.count(Scan.id)).where(Scan.label.isnot(None)).group_by(Scan.label)
    ).all()
    by_label = {row[0]: row[1] for row in label_rows}

    return {
        "users": {"total": total_users},
        "scans": {
            "total": total_scans,
            "completed": completed,
            "failed": failed,
            "by_modality": by_modality,
            "by_label": by_label,
            "avg_confidence": avg_conf,
        },
    }


@router.get("/users")
def list_users(db: DbSession, _: AdminUser, page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100)):
    total = db.scalar(select(func.count(User.id))) or 0
    rows = db.scalars(select(User).order_by(User.id.desc()).offset((page - 1) * page_size).limit(page_size)).all()
    return {
        "items": [
            {
                "id": u.id,
                "email": u.email,
                "full_name": u.full_name,
                "role": u.role.value,
                "is_active": u.is_active,
                "created_at": u.created_at.isoformat() if u.created_at else None,
                "last_login_at": u.last_login_at.isoformat() if u.last_login_at else None,
            }
            for u in rows
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.post("/users/{user_id}/toggle-active")
def toggle_user_active(user_id: int, db: DbSession, admin: AdminUser):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.id == admin.id:
        raise HTTPException(status_code=400, detail="Cannot disable your own account")
    user.is_active = not user.is_active
    db.commit()
    return {"id": user.id, "is_active": user.is_active}


@router.post("/users/{user_id}/promote")
def promote_user(user_id: int, db: DbSession, admin: AdminUser):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.role = UserRole.admin if user.role == UserRole.user else UserRole.user
    db.commit()
    return {"id": user.id, "role": user.role.value}
