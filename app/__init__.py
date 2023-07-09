from flask import Flask

# Create the Flask application instance
app = Flask(__name__)

# Import the routes
from app import routes
