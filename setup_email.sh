#!/bin/bash

echo "Setting up email configuration for Bayonne Hockey Club Portal"
echo "============================================================="
echo

# Prompt for email configuration
echo "Please enter your email configuration:"
echo

read -p "Enter your Gmail address: " email_username
read -s -p "Enter your Gmail App Password: " email_password
echo
echo

# Create .env file
cat > .env << EOF
# Email Configuration for Bayonne Hockey Club
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=$email_username
MAIL_PASSWORD=$email_password
MAIL_DEFAULT_SENDER=noreply@bayonnehockeyclub.com
EOF

echo "✅ .env file created successfully!"
echo
echo "Now you can start your app with:"
echo "source .venv/bin/activate && python run.py"
echo
echo "The app will automatically load the email settings from the .env file."
