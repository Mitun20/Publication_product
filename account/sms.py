from twilio.rest import Client
from editorial_manager.settings import local
from django.template.loader import render_to_string
from django.utils.html import strip_tags

def send_sms_message(to, message):
    client = Client(local.TWILIO_ACCOUNT_SID, local.TWILIO_AUTH_TOKEN)
    try:
        msg = client.messages.create(
            from_=local.TWILIO_SMS_NUMBER,  # Regular Twilio phone number here
            body=message,
            to=to  # recipient's full phone number, e.g. '+919876543210'
        )
        print(f"SMS sent with SID: {msg.sid}")
        return msg.sid
    except Exception as e:
        print(f"Error sending SMS message: {e}")
        return None

from django.http import JsonResponse

def send_sms(user, template_name, context):
    html_content = render_to_string(template_name, context)
    message = strip_tags(html_content)
    # to = user.phone_number
    to = '+917395829944'
    return send_sms_message(to, message)

def send_sms_view(request):
    to = '+917395829944'  # recipient phone number with plus and country code
    message = 'Hello from Django via SMS!'
    sid = send_sms_message(to, message)
    return JsonResponse({'sid': sid})
