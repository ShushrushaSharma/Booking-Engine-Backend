from django.core.mail import send_mail
import random 
from django.conf import settings
from .models import UserRegistration, Contact

def send_otp_via_email(email):
    subject = 'Your account verfication email'
    otp = random.randint(1000,9999)
    message = f'Your otp is {otp}'
    email_from = settings.EMAIL_HOST_USER
    send_mail(subject,message,email_from,[email])
    user_obj = UserRegistration.objects.get(email=email)
    user_obj.otp = otp
    user_obj.save()


def send_query_reply(email, reply):
    subject = 'Your Queries reply email'
    message = reply
    email_from = settings.EMAIL_HOST_USER

    try:
        send_mail(subject, message, email_from, [email])
        contact_email = Contact.objects.get(email=email)
        contact_email.reply = reply
        contact_email.save()
        return True, "Reply sent successfully."
    except Exception as e:
        return False, f"Error sending reply: {str(e)}"


def send_password_reset_email(email, link):
    subject = "Reset Password Link"
    message = "Please click on this link to reset the password: " + link
    email_from = settings.EMAIL_HOST_USER
    send_mail(subject,message,email_from,[email])

