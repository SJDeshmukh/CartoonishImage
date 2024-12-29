from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import base64
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Model for storing images
class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    processed_image = db.Column(db.LargeBinary, nullable=False)  # Store processed image
    user_name = db.Column(db.String(100), nullable=False)  # Store user name
    user_email = db.Column(db.String(100), nullable=True)  # Store user email (optional)

db.create_all()
