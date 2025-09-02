from flask import url_for, render_template_string
from flask_mail import Message
from app import mail
import threading


def send_async_email(app, msg):
    """Send email asynchronously."""
    with app.app_context():
        try:
            mail.send(msg)
        except Exception as e:
            print(f"Failed to send email: {str(e)}")


def send_email(subject, sender, recipients, text_body, html_body):
    """Send email with both text and HTML body."""
    from flask import current_app
    
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    
    # Send email asynchronously
    thread = threading.Thread(
        target=send_async_email, 
        args=(current_app._get_current_object(), msg)
    )
    thread.start()


def send_password_reset_email(user, token):
    """Send password reset email to user."""
    from flask import current_app
    
    reset_url = url_for('main.reset_password', token=token, _external=True)
    
    subject = "Password Reset Request - Bayonne Hockey Club"
    
    # Text version
    text_body = f"""
Hi {user.username},

You have requested a password reset for your Bayonne Hockey Club account.

Click the following link to reset your password:
{reset_url}

This link will expire in 1 hour.

If you did not request this password reset, please ignore this email.

Best regards,
Bayonne Hockey Club
"""

    # HTML version
    html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Password Reset Request</title>
    <style>
        body {{ 
            font-family: Arial, sans-serif; 
            line-height: 1.6; 
            max-width: 600px; 
            margin: 0 auto; 
            padding: 20px;
        }}
        .header {{ 
            text-align: center; 
            background-color: #b01e43; 
            color: white; 
            padding: 20px; 
            border-radius: 5px;
        }}
        .content {{ 
            padding: 20px; 
            background-color: #f9f9f9; 
            border-radius: 5px; 
            margin: 20px 0;
        }}
        .button {{ 
            display: inline-block; 
            background-color: #b01e43; 
            color: white; 
            padding: 12px 24px; 
            text-decoration: none; 
            border-radius: 5px; 
            margin: 20px 0;
        }}
        .footer {{ 
            text-align: center; 
            color: #666; 
            font-size: 0.9em; 
            margin-top: 20px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Password Reset Request</h1>
    </div>
    
    <div class="content">
        <p>Hi <strong>{user.username}</strong>,</p>
        
        <p>You have requested a password reset for your Bayonne Hockey Club account.</p>
        
        <p>Click the button below to reset your password:</p>
        
        <p style="text-align: center;">
            <a href="{reset_url}" class="button">Reset Your Password</a>
        </p>
        
        <p><strong>This link will expire in 1 hour.</strong></p>
        
        <p>If you did not request this password reset, please ignore this email.</p>
    </div>
    
    <div class="footer">
        <p>Best regards,<br>Bayonne Hockey Club</p>
    </div>
</body>
</html>
"""

    try:
        send_email(
            subject=subject,
            sender=current_app.config['MAIL_DEFAULT_SENDER'],
            recipients=[user.email],
            text_body=text_body,
            html_body=html_body
        )
        return True
    except Exception as e:
        print(f"Error sending password reset email: {str(e)}")
        return False
