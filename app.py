from flask import Flask, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from twilio.twiml.messaging_response import MessagingResponse
from monkeybot import ConversationManager

app = Flask(__name__)
cm = ConversationManager()

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    # storage_uri="memory://",
)

@app.route("/sms-monkey", methods=['GET', 'POST'])
@limiter.limit("20/minute", override_defaults=True)
def sms_reply():
    """Respond to incoming calls with a simple text message."""
    user_input = request.values.get('Body', None)
    trimmed_ai_response = cm.complete_chat(user_input)
    # print(body)
    # Start our TwiML response
    resp = MessagingResponse()

    # Add a message
    resp.message(trimmed_ai_response)

    return str(resp)

# @app.route("/sms-monkey", methods=['GET', 'POST'])
# def hello_world():
#     return "Hello, ERM's Phone!"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
