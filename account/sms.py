from twilio.rest import Client
from editorial_manager.settings import local

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

def send_sms_view(request):
    to = '+917395829944'  # recipient phone number with plus and country code
    message = 'Hello from Django via SMS!'
    sid = send_sms_message(to, message)
    return JsonResponse({'sid': sid})
