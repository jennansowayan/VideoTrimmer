from flask import render_template, request, redirect, url_for, send_from_directory, flash
from app import app
from app.ocr import extract_timestamps
from app.trimming import trim_and_save_clips
import os

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_video():
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
