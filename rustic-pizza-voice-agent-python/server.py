from flask import Flask
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

from routes.call import call_bp
from routes.sms import sms_bp

app.register_blueprint(call_bp, url_prefix="/call")
app.register_blueprint(sms_bp, url_prefix="/sms")

@app.route("/")
def index():
    return "Rustic Pizza Voice Agent is running!"

if __name__ == "__main__":
    app.run(port=3000, debug=True)
