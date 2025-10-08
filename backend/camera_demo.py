

import cv2
import time
from agent_utils import analyze_image_for_stress, get_stress_category, analyze_emotion_sync
import io
import numpy as np
from PIL import Image


def check_face_in_frame(frame):
    """Use OpenCV to detect if there's a face in the frame."""
    try:
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        return len(faces) > 0, len(faces)
    except Exception as e:
        return False, 0

def get_emotion_preview(emotion_data):
    """Generate a text-based preview of detected emotions."""
    if not emotion_data or emotion_data.get('emotion') == 'neutral':
        return "No emotion detected"

    emotion = emotion_data.get('emotion', 'unknown')
    confidence = emotion_data.get('confidence', 0.0)

    if confidence > 0.7:
        return f"Strong {emotion} ({confidence:.2f})"
    elif confidence > 0.5:
        return f"Moderate {emotion} ({confidence:.2f})"
    else:
        return f"Weak {emotion} ({confidence:.2f})"

def demo_camera_live_detection(headless=True, duration_seconds=30):
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Error: Cannot open camera")
        return

    print("👤 Starting live face detection: Hume AI analyzes your facial stress & emotions")
    print("💡 Keep your face clearly visible in front of the camera!")

    start_time = time.time()
    frame_count = 0

    while time.time() - start_time < duration_seconds:
        frame_count += 1
        ret, frame = cap.read()
        if not ret:
            print("❌ Failed to read frame from camera")
            break

        has_face, num_faces = check_face_in_frame(frame)
        face_status = f"✅ {num_faces} face(s) detected" if has_face else "❌ No faces detected"

        print(f"\n📸 Frame {frame_count} | Image: {frame.shape[1]}x{frame.shape[0]} | {face_status}")

        if not has_face:
            print(f"🔍 Skip: No face visible - position yourself in front of camera")
            time.sleep(1.5)
            continue

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        pil_img = Image.fromarray(frame_rgb)
        img_data = io.BytesIO()
        pil_img.save(img_data, format='JPEG', quality=95)
        img_bytes = img_data.getvalue()
        img_size_kb = len(img_bytes) / 1024

        print(f"📊 Processing | JPEG: {img_size_kb:.1f} KB")

        emotion_data = analyze_emotion_sync(img_bytes)
        emotion_preview = get_emotion_preview(emotion_data)

        stress_percentage = analyze_image_for_stress(img_bytes)
        stress_category = get_stress_category(stress_percentage)

        print(f"🎭 Result | {emotion_preview} | Stress: {stress_percentage:.1f}% | Category: {stress_category}")
        print(f"─".rjust(70, "─"))

        time.sleep(2.0)

        if frame_count >= 5:
            print("\n⚠️ Completion: 5 face detections processed")
            break

    cap.release()
    print("\n🎉 Analysis complete!")
    print(f"📊 Processed {frame_count} frames with face detections")
    print("💡 Tip: Stay in camera view for continuous emotion analysis!")


if __name__ == "__main__":
    demo_camera_live_detection(headless=True, duration_seconds=20)
