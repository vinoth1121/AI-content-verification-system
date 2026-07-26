"""Seed the backend DB with a demo admin user + sample scans for the dashboard."""
import os
import sys
from pathlib import Path

# Ensure env vars override the sandbox defaults
os.environ["DATABASE_URL"] = "sqlite:///./acvs.db"
os.environ.setdefault("JWT_SECRET", "dev-secret-must-be-at-least-32-characters-long-1234567890")
os.environ.setdefault("CORS_ORIGINS", '["http://localhost:3000"]')

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
sys.path.insert(0, str(ROOT / "ai-engine"))

from app.db.session import SessionLocal, init_db  # noqa: E402
from app.core.security import hash_password  # noqa: E402
from app.models.user import User, UserRole  # noqa: E402
from app.models.scan import Scan, ScanModality, ScanStatus  # noqa: E402
from app.services.scan_service import run_text_scan  # noqa: E402

from datetime import datetime, timedelta, timezone


def main() -> None:
    init_db()
    db = SessionLocal()

    # Create admin user
    admin_email = "admin@acvs.io"
    if not db.query(User).filter_by(email=admin_email).first():
        admin = User(
            email=admin_email,
            full_name="System Administrator",
            hashed_password=hash_password("Admin123!Admin"),
            role=UserRole.admin,
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        print(f"Admin user created: {admin_email} / Admin123!Admin")
    else:
        admin = db.query(User).filter_by(email=admin_email).first()
        print("Admin user already exists")

    # Create regular user
    user_email = "user@acvs.io"
    if not db.query(User).filter_by(email=user_email).first():
        regular = User(
            email=user_email,
            full_name="Demo User",
            hashed_password=hash_password("User123!User"),
            role=UserRole.user,
        )
        db.add(regular)
        db.commit()
        db.refresh(regular)
        print(f"Demo user created: {user_email} / User123!User")

    # Generate sample scans for the admin user
    sample_texts = [
        "The quick brown fox jumps over the lazy dog. The dog barked once, then went back to sleep.",
        "It is important to note that this system represents a comprehensive approach to addressing the multifaceted challenges inherent in modern content verification.",
        "I went to the store yesterday. They were out of milk. Got eggs instead.",
        "Furthermore, it should be noted that the implementation of said framework necessitates a thorough understanding of the underlying methodologies.",
        "Breaking news! You won't believe what doctors are calling the secret trick that changed everything!",
    ]

    existing = db.query(Scan).filter_by(user_id=admin.id).count()
    if existing == 0:
        print("Generating sample scans...")
        for text in sample_texts:
            scan = run_text_scan(db, admin.id, text)
            print(f"  Scan #{scan.id}: label={scan.label} conf={scan.confidence:.2f}")
    else:
        print(f"Admin already has {existing} scans")

    db.close()
    print("Seed complete.")


if __name__ == "__main__":
    main()
