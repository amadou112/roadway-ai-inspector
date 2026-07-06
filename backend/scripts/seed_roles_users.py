"""Creates one demo user per role for instant recruiter/demo login.
Safe to re-run: skips users that already exist.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.enums import RoleEnum
from app.models.user import User

DEMO_PASSWORD = "RoadwayDemo!2026"

DEMO_USERS = [
    ("pm@demo.gov", "Alicia Torres", RoleEnum.program_manager),
    ("projectmanager@demo.gov", "Marcus Webb", RoleEnum.project_manager),
    ("resident-engineer@demo.gov", "Priya Nair", RoleEnum.resident_engineer),
    ("inspector@demo.gov", "Daniel Ruiz", RoleEnum.inspector),
    ("designer@demo.gov", "Grace Lin", RoleEnum.designer),
    ("contractor@demo.gov", "Tom Bradley", RoleEnum.contractor),
    ("executive@demo.gov", "Denise Carter", RoleEnum.dot_executive),
]


def run() -> None:
    db = SessionLocal()
    try:
        for email, full_name, role in DEMO_USERS:
            existing = db.query(User).filter(User.email == email).first()
            if existing:
                continue
            user = User(
                email=email,
                full_name=full_name,
                role=role,
                hashed_password=hash_password(DEMO_PASSWORD),
            )
            db.add(user)
            print(f"created {role.value}: {email}")
        db.commit()
        print(f"\nDemo password for all seeded users: {DEMO_PASSWORD}")
    finally:
        db.close()


if __name__ == "__main__":
    run()
