# from flask import Flask, render_template, url_for

# app = Flask(__name__)

# @app.route('/')
# def index():
#     # return "hello flask!"
#     return render_template("index.html")

# if __name__ == "__main__":
#     # Set to False later on.
#     app.run(debug=True)

from flask import Flask, render_template, request, jsonify, send_file, send_from_directory, session
import os
import subprocess

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

app.secret_key = "your_secret_key"  # Required for session usage

# # Dummy function for deep learning model
# def run_deep_learning_model(video_path):
#     return ["ABC123", "XYZ789", "LMN456", "UP113899"]

def run_deep_learning_model(video_path):
    # Path to the other environment's Python interpreter
    other_env_python = "./model-env/python"
    try:
        # Run Script 1
        subprocess.run(
            [other_env_python, "main.py", video_path],
            check=True,
        )
        # Run Script 2
        subprocess.run(
            [other_env_python, "add_missing_data.py", video_path],
            check=True,
        )
        # Run Script 3
        subprocess.run(
            [other_env_python, "visualize.py", video_path],
            check=True,
        )
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while running the scripts: {e}")
        return []

    # Return recognized plates (dummy example)
    return ["ABC123", "XYZ789", "LMN456", "UP113899"]


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file part"})
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"})
    if file:
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        file.save(file_path)
        return jsonify({"message": "File uploaded successfully", "file_path": f"/uploads/{file.filename}"})

@app.route("/uploads/<path:filename>")
def serve_uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

@app.route("/test", methods=["POST"])
def test_model():
    video_path = request.form.get("video_path")
    if not video_path or not os.path.exists(video_path[1:]):  # Remove leading slash from file path
        return jsonify({"error": "Invalid video path"})

    # Run the deep learning model on the uploaded video
    recognized_plates = run_deep_learning_model(video_path[1:])  # Use the proper video path

    # Save results dynamically (you can store them in session, global variable, or file)
    session["recognized_plates"] = recognized_plates  # Store plates in session for download
    return jsonify({"recognized_plates": recognized_plates})

@app.route("/download", methods=["GET"])
def download_results():
    result_file = os.path.join(UPLOAD_FOLDER, "recognized_plates.txt")

    # Retrieve the recognized plates from session or a persistent store
    recognized_plates = session.get("recognized_plates", [])
    if not recognized_plates:
        return jsonify({"error": "No recognized plates available for download"}), 400

    # Write recognized plates to a file
    with open(result_file, "w") as f:
        f.write("\n".join(recognized_plates))
    
    # Send the file for download
    return send_file(result_file, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)

