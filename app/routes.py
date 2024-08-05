from flask import render_template, request, redirect, url_for, send_from_directory, flash
from app import app
from app.ocr import extract_timestamps
from app.trimming import trim_and_save_clips
import os
import cv2
import uuid

# Path to the first_frame directory
FIRST_FRAME_DIR = os.path.abspath('uploads/first_frames')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

@app.route('/internal_error')
def internal_error():
    return render_template('error.html', message="An internal error occurred. Please try again later.")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/first_frame/<filename>')
def serve_first_frame(filename):
    return send_from_directory(FIRST_FRAME_DIR, filename)

def save_first_frame(video_file):
    unique_id = str(uuid.uuid4())
    filename = f'{unique_id}_first_frame.jpg'
    file_path = os.path.join(FIRST_FRAME_DIR, filename)
    
    cap = cv2.VideoCapture(video_file)
    ret, frame = cap.read()
    if ret:
        cv2.imwrite(file_path, frame)
    cap.release()
    
    return filename

@app.route('/upload', methods=['POST'])
def upload_video():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    
    if file:
        filename = file.filename
        file_path = os.path.join('uploads', filename)
        file.save(file_path)

        # Save the first frame and get the unique filename
        first_frame_filename = save_first_frame(file_path)

        return render_template('index.html', first_frame=True, video_uploaded=True, first_frame_path=url_for('serve_first_frame', filename=first_frame_filename))

    return redirect(url_for('index'))

@app.route('/process_video', methods=['POST'])
def process_video():
    try:
        x = int(request.form['x'])
        y = int(request.form['y'])
        w = int(request.form['w'])
        h = int(request.form['h'])
        video_path = request.form['video_path']

        ocr_region = (x, y, w, h)
        clip_timestamps, clip_durations = extract_timestamps(video_path, ocr_region)
        clip_paths = trim_and_save_clips(video_path, clip_timestamps)

        clips = [
            {"name": os.path.basename(path), "duration": duration}
            for path, duration in zip(clip_paths, clip_durations)
        ]

        return render_template('index.html', clips=clips)

    except Exception as e:
        app.logger.error(f'Error processing video: {e}')
        return redirect(url_for('internal_error'))

    return redirect(url_for('index'))

    try:
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file:
            filename = file.filename
            file_path = os.path.join('uploads', filename)
            file.save(file_path)

            # Get OCR region values from the form
            try:
                x = int(request.form['x'])
                y = int(request.form['y'])
                w = int(request.form['w'])
                h = int(request.form['h'])
                ocr_region = (x, y, w, h)
            except ValueError:
                flash('Invalid OCR region values')
                return redirect(url_for('index'))

            clip_timestamps, clip_durations = extract_timestamps(file_path, ocr_region)
            clip_paths = trim_and_save_clips(file_path, clip_timestamps)

            clips = [
                {"name": os.path.basename(path), "duration": duration}
                for path, duration in zip(clip_paths, clip_durations)
            ]

            return render_template('index.html', clips=clips)

    except Exception as e:
        app.logger.error(f'Error processing video: {e}')
        return redirect(url_for('internal_error'))

    return redirect(url_for('index'))

@app.route('/download/<filename>')
def download_file(filename):
    try:
        return send_from_directory('clips', filename, as_attachment=True)
    except Exception as e:
        app.logger.error(f'Error downloading file: {e}')
        return redirect(url_for('internal_error'))

@app.route('/download_all')
def download_all():
    try:
        import zipfile
        import io

        memory_file = io.BytesIO()
        with zipfile.ZipFile(memory_file, 'w') as zf:
            for filename in os.listdir('clips'):
                zf.write(os.path.join('clips', filename), filename)
        memory_file.seek(0)
        return send_file(memory_file, attachment_filename='all_clips.zip', as_attachment=True)
    except Exception as e:
        app.logger.error(f'Error downloading all files: {e}')
        return redirect(url_for('internal_error'))
