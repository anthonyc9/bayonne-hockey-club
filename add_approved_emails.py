#!/usr/bin/env python3
"""
Script to add pre-approved email addresses to the production database.
Run this on Heroku to populate the PreApprovedEmails table.
"""

from app import create_app
from app.models import PreApprovedEmails, db

def add_approved_emails():
    app = create_app()
    
    with app.app_context():
        # Check if emails already exist
        existing_emails = [email.email for email in PreApprovedEmails.query.all()]
        
        # Emails to add
        emails_to_add = [
            "anthonycortese9@gmail.com",
            "bayonnehockeyclub@gmail.com"
        ]
        
        print("Current pre-approved emails:")
        for email in existing_emails:
            print(f"- {email}")
        
        print(f"\nAdding {len(emails_to_add)} new emails...")
        
        # Add new emails
        for email_address in emails_to_add:
            if email_address not in existing_emails:
                new_email = PreApprovedEmails(email=email_address)
                db.session.add(new_email)
                print(f"Added: {email_address}")
            else:
                print(f"Already exists: {email_address}")
        
        # Commit changes
        db.session.commit()
        
        print("\nFinal list of pre-approved emails:")
        final_emails = PreApprovedEmails.query.all()
        for email in final_emails:
            print(f"- {email.email}")
        
        print(f"\nTotal: {len(final_emails)} pre-approved emails")

if __name__ == "__main__":
    add_approved_emails()
