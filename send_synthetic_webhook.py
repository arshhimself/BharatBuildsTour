import hmac
import hashlib
import requests
import json
import time

SECRET = "6f77d52bdd504d4d6f1d582781b3e512" # from tfvars, app secret
URL = "https://stockaware.vaaani.co.in/webhook/whatsapp"
NUMBER_B_ID = "1353344187842745" # Biz phone number ID

def send_message(text):
    payload = {
        "object": "whatsapp_business_account",
        "entry": [{
            "id": "1122334455",
            "changes": [{
                "value": {
                    "messaging_product": "whatsapp",
                    "metadata": {
                        "display_phone_number": "911234567890",
                        "phone_number_id": NUMBER_B_ID
                    },
                    "contacts": [{"profile": {"name": "Test User"}, "wa_id": "919999999999"}],
                    "messages": [{
                        "from": "919999999999",
                        "id": f"wamid.{int(time.time())}",
                        "timestamp": str(int(time.time())),
                        "text": {"body": text},
                        "type": "text"
                    }]
                },
                "field": "messages"
            }]
        }]
    }
    
    body = json.dumps(payload).encode('utf-8')
    signature = "sha256=" + hmac.new(SECRET.encode('utf-8'), body, hashlib.sha256).hexdigest()
    
    headers = {
        "Content-Type": "application/json",
        "X-Hub-Signature-256": signature
    }
    
    response = requests.post(URL, headers=headers, data=body)
    print(f"Sent: '{text}', Response Status: {response.status_code}")
    print(response.text)

print("Sending Hello Bhai...")
send_message("Hello Bhai")

time.sleep(2)

print("\nSending Products dikhao...")
send_message("Products dikhao")

