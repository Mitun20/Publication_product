

def send_whatsapp_message(to, message):
    from twilio.rest import Client
    from editorial_manager.settings import local
    import traceback

    client = Client(local.TWILIO_ACCOUNT_SID, local.TWILIO_AUTH_TOKEN)
    try:
        msg = client.messages.create(
            from_=local.TWILIO_WHATSAPP_NUMBER,
            body=message,
            to=f'whatsapp:{to}'
        )
        print(f"Message sent with SID: {msg.sid}")
        return msg.sid
    except Exception as e:
        print("Error sending WhatsApp message:")
        traceback.print_exc()
        return None

# views.py

from django.http import JsonResponse


def send_message_view(request):
    to = '917395829944'  
    message = 'Hello from Django via WhatsApp!'
    sid = send_whatsapp_message(to, message)
    return JsonResponse({'sid': sid})
