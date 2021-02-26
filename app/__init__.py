from flask import Flask
from flask_cors import CORS

# Place where app is defined
app = Flask(__name__)

# JWT Secret Key
app.config["SECRET_KEY"] = "hTOiVN7OD5eSTR28h9Mm7SJRRhJ6sa3i"

# Token Valid in Minutes
app.config["TOKEN_VALID_FOR"] = "60"

# CORS POLICY
cors = CORS(app)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
app.config["CORS_HEADERS"] = "Content-Type"

from app import requestMethods