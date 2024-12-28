import random
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS  # Import CORS
import cv2
import numpy as np
import base64
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024
@app.route('/process', methods=['POST'])
def process_image():
    print("Got Request")
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    filename = "uploaded_image.jpg"
    file.save(filename)

    # Process the image
    img = cv2.imread(filename)
    if img is None:
        return jsonify({"error": "Invalid image file"}), 400
    max_width = 300
    height, width = img.shape[:2]
    if width > max_width:
        scaling_factor = max_width / width
        new_size = (max_width, int(height * scaling_factor))
        img = cv2.resize(img, new_size, interpolation=cv2.INTER_AREA)
        print(f"Image resized to {new_size}")
    # Randomize `total_color`, `sigmaColor`, and `sigmaSpace`
    total_color = random.randint(25, 50)  # Randomize between 25 and 70
    sigma_value = random.randint(101, 200)  # Randomize between 100 and 200
    print(f"Using total_color: {total_color}, sigma_value: {sigma_value}")

    kernel = np.ones((5, 5), np.uint8)

    def color_quantization(img, k):
        # Transform the image
        data = np.float32(img).reshape((-1, 3))

        # Determine criteria
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.1)

        # Implementing K-Means
        ret, label, center = cv2.kmeans(data, k, None, criteria, 5, cv2.KMEANS_RANDOM_CENTERS)
        center = np.uint8(center)
        result = center[label.flatten()]
        result = result.reshape(img.shape)
        return result

    def edge_mask(img, line_size, blur_value):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray_blur = cv2.medianBlur(gray, blur_value)
        edges = cv2.adaptiveThreshold(gray_blur, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, line_size, blur_value)
        return edges

    line_size = 3
    blur_value = 3

    # Convert the image to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    print("Reached Gray")
    # Apply adaptive thresholding to convert the image to binary
    gray = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 9)

    edges = edge_mask(img, line_size, blur_value)
    img = color_quantization(img, total_color)
    blurred = cv2.bilateralFilter(img, d=1, sigmaColor=sigma_value, sigmaSpace=sigma_value)
    print("Blurred")
    cartoon = cv2.bitwise_and(blurred, blurred, mask=edges)

    color = cv2.bilateralFilter(img, 10, sigma_value, sigma_value)

    cartoon = cv2.bitwise_and(color, color, mask=gray)
    print("Cartoonized")

    # Convert the cartoonized image to base64
    _, buffer = cv2.imencode('.jpg', cartoon)
    img_base64 = base64.b64encode(buffer).decode('utf-8')

    # Clean up the temporary uploaded image
    os.remove(filename)

    print("Cartoonized image processed and base64 encoded.")
    
    # Return the base64-encoded image as JSON response
    return jsonify({'image': img_base64})

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/')
def home():
    return render_template('cartoon_frontend.html')
      

if __name__ == '__main__':
    app.run(debug=True)
