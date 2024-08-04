from flask import render_template, request, redirect, url_for
from app import app
from app.ocr import extract_timestamps
from app.trimming import trim_and_save_clips
import os

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_video():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    if file:
        filename = file.filename
        file_path = os.path.join('uploads', filename)
        file.save(file_path)

        # Define the OCR region (adjust as needed)
        ocr_region = (100, 50, 200, 50)
        clip_timestamps, _ = extract_timestamps(file_path, ocr_region)
        trim_and_save_clips(file_path, clip_timestamps)

        return redirect(url_for('index'))

    return redirect(url_for('index'))
