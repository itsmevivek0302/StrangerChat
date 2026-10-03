from database import Base, engine, SessionLocal
from models import User
from auth import hash_password

Base.metadata.create_all(bind=engine)
demo = [
    ("alice", "alice@example.com", "Alice here 👋"),
    ("bob", "bob@example.com", "Coffee, coding and conversations."),
    ("charlie", "charlie@example.com", "Always happy to meet new people."),
]

with SessionLocal.begin() as db:
    for username, email, bio in demo:
        existing_user = db.query(User).filter(
            (User.email == email) | (User.username == username)
        ).first()
        if not existing_user:
            db.add(
                User(
                    username=username,
                    email=email,
                    password_hash=hash_password("password123"),
                    bio=bio,
                )
            )

print("Demo users created. Password: password123")
