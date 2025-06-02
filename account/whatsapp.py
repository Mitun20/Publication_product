
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from twilio.rest import Client
from editorial_manager.settings import local
import traceback


def send_whatsapp_message(to, message):
    client = Client(local.TWILIO_ACCOUNT_SID, local.TWILIO_AUTH_TOKEN)
    from_number = local.TWILIO_WHATSAPP_NUMBER
    try:
        msg = client.messages.create(
            from_='whatsapp:+14155238886',
            body=message,
            to=f'whatsapp:{to}'  # ✅ Already correct
        )
        print(f"Message sent with SID: {msg.sid}")
        return msg.sid
    except Exception as e:
        print("Error sending WhatsApp message:")
        traceback.print_exc()
        return None

def send_whatsapp(user, template_name, context):

    html_content = render_to_string(template_name, context)
    message = strip_tags(html_content)
    print(f"Sending WhatsApp message to with content: {message}")
    # to = user.phone_number
    to ='+917395829944' 
    
    return send_whatsapp_message(to, message)

# views.py

from django.http import JsonResponse


def send_message_view(request):
    to ='+917395829944'  
    message = 'Hello from Django via WhatsApp!'
    sid = send_whatsapp_message(to, message)
    return JsonResponse({'sid': sid})
