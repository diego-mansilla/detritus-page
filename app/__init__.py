from flask import Flask

# Create the Flask application instance
app = Flask(__name__)

# Import the routes
from app import routes
app.secret_key = '62e5ff4d8597c01399609372aabf8e42'