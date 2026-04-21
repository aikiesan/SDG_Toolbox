from flask_mail import Message
from app import mail
from flask import current_app, render_template
from threading import Thread

def send_async_email(app, msg):
    with app.app_context():
        try:
            mail.send(msg)
        except Exception as e:
            app.logger.error(f"Failed to send email: {str(e)}")
            # Don't raise - email failure shouldn't block the app

def send_email(subject, recipients, html_body, text_body=None):
    msg = Message(subject, recipients=recipients)
    msg.body = text_body or html_body
    msg.html = html_body
    
    # Send email asynchronously
    Thread(target=send_async_email, args=(current_app._get_current_object(), msg)).start()

def send_confirmation_email(user):
    token = user.generate_confirmation_token()
    confirm_url = url_for('auth.confirm_email', token=token, _external=True)
    html = render_template('auth/email/confirm_email.html', confirm_url=confirm_url, user=user)
    text = render_template('auth/email/confirm_email.txt', confirm_url=confirm_url, user=user)
    
    subject = "Please confirm your email"
    send_email(subject, [user.email], html, text)

def send_password_reset_email(user):
    token = user.generate_reset_token()
    reset_url = url_for('auth.reset_password', token=token, _external=True)
    html = render_template('auth/email/reset_password.html', reset_url=reset_url, user=user)
    text = render_template('auth/email/reset_password.txt', reset_url=reset_url, user=user)
    
    subject = "Password Reset Request"
    send_email(subject, [user.email], html, text)