"""
Creates the first admin, or makes an existing account an admin:  python -m scripts.create_admin
The password is typed privately, so it never appears in a command history or a file.
"""
from getpass import getpass

from sqlalchemy import select

from app.core.database import SessionLocal
from app.core.security import hash_password, password_problem
from app.models import User


def main() -> None:
    email = input("Admin email: ").strip().lower()
    with SessionLocal() as db:
        user = db.scalar(select(User).where(User.email == email))
        if user:
            user.role = "admin"
        else:
            password = getpass("Password (it won't show while you type): ")
            problem = password_problem(password, email)
            if problem:
                raise SystemExit(problem)
            if password != getpass("Type it again: "):
                raise SystemExit("The passwords didn't match.")
            db.add(User(email=email, password_hash=hash_password(password), role="admin"))
        db.commit()
    print(f"{email} is now an admin.")


if __name__ == "__main__":
    main()
