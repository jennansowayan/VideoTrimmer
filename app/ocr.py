import cv2
import pytesseract

# Configure Tesseract executable path (update this if Tesseract is not in your PATH)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Change this path

def extract_timestamps(video_path, ocr_region, ocr_config='--psm 6'):
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = frame_count / fps

    timestamps = []
    frame_number = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame_number += 1
        if frame_number % fps != 0:  # Check every second (or adjust as needed)
            continue

        x, y, w, h = ocr_region
        cropped_frame = frame[y:y+h, x:x+w]
        text = pytesseract.image_to_string(cropped_frame, config=ocr_config).strip()

        if text and is_valid_timestamp(text):
            timestamp = frame_number / fps
            timestamps.append(timestamp)

    cap.release()
    return timestamps, duration

def is_valid_timestamp(text):
    import re
    pattern = re.compile(r'^\d{2}:\d{2}:\d{2}$')
    return pattern.match(text) is not None
