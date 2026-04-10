from app.database import SessionLocal
from app.models import User
import uuid

def seed():
    db = SessionLocal()
    existing = db.query(User).filter(User.email == "ianw@minddesign.co.za").first()
    if existing:
        print("User already exists")
        return
    
    user = User(
        id=str(uuid.uuid4()),
        name = "Ian",
        email = "ianw@minddesign.co.za",
        password_hash = "1234",
        role = "admin"
    )
    
    db.add(user)
    db.commit()
    db.close()
    print("User created")
    
if __name__ == "__main__":
    seed()
    