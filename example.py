from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

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
    # Start our TwiML response
    resp = MessagingResponse()

    # Add a message
    resp.message("The Robots are coming! Head for the hills!")

    return str(resp)

# @app.route("/sms-monkey", methods=['GET', 'POST'])
# def hello_world():
#     return "Hello, ERM's Phone!"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
