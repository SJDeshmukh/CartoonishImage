import random
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import cv2
import numpy as np
import base64
import os
import psycopg2

app = Flask(__name__)
CORS(app)  # Enable CORS
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # Limit file size to 10MB

# Database connection function
def get_db_connection():
    try:
        conn = psycopg2.connect(
            host='dpg-ctnuipdsvqrc73b4c260-a.frankfurt-postgres.render.com',
            database='cartoondatabase',
            user='cartoondatabase_user',
            password='VeniS20ArXFHvmN3L1xLCDL1yE8vn2E6'
        )
        return conn
    except psycopg2.Error as e:
        print(f"Database connection error: {e}")
        return None

# Cartoonize image and store in database
@app.route('/process', methods=['POST'])
def process_image():
    # Validate file upload
    if 'file' not in request.files or request.files['file'].filename == '':
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    user_name = request.form.get('user_name')
    user_email = request.form.get('user_email')

    # Validate user inputs
    if not user_name or not user_email:
        return jsonify({"error": "User name and email are required"}), 400

    # Save uploaded file temporarily
    filename = "uploaded_image.jpg"
    file.save(filename)

    # Read the image
    img = cv2.imread(filename)
    if img is None:
        os.remove(filename)
        return jsonify({"error": "Invalid image file"}), 400

    # Resize the image if it's too large
    max_width = 400
    height, width = img.shape[:2]
    if width > max_width:
        scaling_factor = max_width / width
        img = cv2.resize(img, (max_width, int(height * scaling_factor)))

    # Randomize cartoonization parameters
    total_color = random.randint(50, 70)
    sigma_value = random.randint(101, 200)

    # Functions for image processing
    def color_quantization(img, k):
        data = np.float32(img).reshape((-1, 3))
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.1)
        _, label, center = cv2.kmeans(data, k, None, criteria, 15, cv2.KMEANS_RANDOM_CENTERS)
        center = np.uint8(center)
        return center[label.flatten()].reshape(img.shape)

    def edge_mask(img, line_size, blur_value):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray_blur = cv2.medianBlur(gray, blur_value)
        return cv2.adaptiveThreshold(gray_blur, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, line_size, blur_value)

    # Apply cartoonization
    edges = edge_mask(img, line_size=9, blur_value=3)
    print("Got edges")
    print("Total color: ",total_color)
    # img = color_quantization(img, total_color)
    blurred = cv2.bilateralFilter(img, d=1, sigmaColor=sigma_value, sigmaSpace=sigma_value)
    print("Blurred")
    cartoon = cv2.bitwise_and(blurred, blurred, mask=edges)

    # Encode the cartoonized image in Base64
    _, buffer = cv2.imencode('.jpg', cartoon)
    img_base64 = base64.b64encode(buffer).decode('utf-8')

    # Clean up temporary file
    os.remove(filename)

    # Save data to database
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (name, email, image) VALUES (%s, %s, %s)', (user_name, user_email, img_base64))
        conn.commit()
        cursor.close()
        print("Commited and added successfully!")
    except Exception as e:
        conn.rollback()
        return jsonify({"error": f"Database error: {e}"}), 500
    finally:
        conn.close()

    return jsonify({'status': 'success', 'image': img_base64, 'message': 'Image processed successfully'})

# About page
@app.route('/about')
def about():
    return render_template('about.html')

# Contact page
@app.route('/contact')
def contact():
    return render_template('contact.html')

# Home page
@app.route('/')
def home():
    return render_template('cartoon_frontend.html')

if __name__ == '__main__':
    app.run(debug=True)
