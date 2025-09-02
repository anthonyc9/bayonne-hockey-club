from app import db, create_app
from app.models import PreApprovedEmails

app = create_app()

def seed_emails():
    with app.app_context():
        emails = ["anthonycortese9@gmail.com", "testuser@example.com"]
        for email in emails:
            if not PreApprovedEmails.query.filter_by(email=email).first():
                db.session.add(PreApprovedEmails(email=email))
        db.session.commit()
        print("Pre-approved emails seeded!")

if __name__ == "__main__":
    seed_emails()