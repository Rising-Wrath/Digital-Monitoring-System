import streamlit as st
import cv2
import numpy as np
import os
import dlib
from PIL import Image

# Set the page config
st.set_page_config(page_title="Face Recognition", page_icon="😀", layout="wide")

# Load pre-trained face detection and face recognition models
detector = dlib.get_frontal_face_detector()
sp = dlib.shape_predictor("F:/MCA PROJECT/Final/Data/shape_predictor_68_face_landmarks.dat")
facerec = dlib.face_recognition_model_v1("F:/MCA PROJECT/Final/Data/dlib_face_recognition_resnet_model_v1.dat")

def get_lbp_histogram(image):
    def calculate_lbp(img, x, y):
        center = img[x, y]
        code = 0
        for i in range(8):
            xi = x + int(np.cos(2 * np.pi * i / 8))
            yi = y + int(np.sin(2 * np.pi * i / 8))
            if xi >= 0 and xi < img.shape[0] and yi >= 0 and yi < img.shape[1]:
                if img[xi, yi] >= center:
                    code |= 1 << i
        return code

    height, width = image.shape
    lbp_image = np.zeros((height, width), dtype=np.uint8)
    for i in range(1, height - 1):
        for j in range(1, width - 1):
            lbp_image[i, j] = calculate_lbp(image, i, j)

    hist, _ = np.histogram(lbp_image.ravel(), bins=256, range=(0, 256))
    return hist

def analyze_texture(face_region):
    gray_face = cv2.cvtColor(face_region, cv2.COLOR_RGB2GRAY)
    lbp_hist = get_lbp_histogram(gray_face)
    
    # You might need to adjust these thresholds based on experimentation
    variance = np.var(lbp_hist)
    entropy = -np.sum(lbp_hist * np.log2(lbp_hist + 1e-7))
    
    # Higher variance and entropy typically indicate a real face
    return variance > 1000 and entropy > 5

# Function to load and prepare face data from a directory
def load_face_data(directory):
    known_face_encodings = []
    known_face_names = []
    try:
        for filename in os.listdir(directory):
            if filename.endswith(".jpg") or filename.endswith(".png"):
                img_path = os.path.join(directory, filename)
                img = dlib.load_rgb_image(img_path)
                dets = detector(img, 1)
                for k, d in enumerate(dets):
                    shape = sp(img, d)
                    face_descriptor = facerec.compute_face_descriptor(img, shape)
                    known_face_encodings.append(np.array(face_descriptor))
                    known_face_names.append(filename.split('.')[0])
    except Exception as e:
        st.error(f"Error loading face data: {e}")
    return known_face_encodings, known_face_names

def detect_blinks(shape):
    # Extract the left and right eye coordinates
    left_eye = np.array([(shape.part(n).x, shape.part(n).y) for n in range(42, 48)])
    right_eye = np.array([(shape.part(n).x, shape.part(n).y) for n in range(36, 42)])
    
    # Calculate the eye aspect ratios
    left_ear = eye_aspect_ratio(left_eye)
    right_ear = eye_aspect_ratio(right_eye)
    
    # Average the eye aspect ratio together for both eyes
    ear = (left_ear + right_ear) / 2.0
    
    # Check if the eye aspect ratio is below the blink threshold
    return ear < 0.3  # You may need to adjust this threshold

def eye_aspect_ratio(eye):
    # Compute the euclidean distances between the two sets of
    # vertical eye landmarks (x, y)-coordinates
    A = np.linalg.norm(eye[1] - eye[5])
    B = np.linalg.norm(eye[2] - eye[4])

    # Compute the euclidean distance between the horizontal
    # eye landmark (x, y)-coordinates
    C = np.linalg.norm(eye[0] - eye[3])

    # Compute the eye aspect ratio
    ear = (A + B) / (2.0 * C)

    return ear

def detect_motion(frame, prev_frame):
    diff = cv2.absdiff(frame, prev_frame)
    gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)
    dilated = cv2.dilate(thresh, None, iterations=3)
    contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    for contour in contours:
        if cv2.contourArea(contour) > 1000:
            return True
    return False

# Load saved faces from directory
saved_faces_directory = 'F:/MCA PROJECT/Final/Data/SavedFaces'
known_face_encodings, known_face_names = load_face_data(saved_faces_directory)

# Initialize webcam
cap = cv2.VideoCapture(0)

st.title("Face Recognition")

# Initialize session state for buttons
if 'start' not in st.session_state:
    st.session_state['start'] = False
if 'snap' not in st.session_state:
    st.session_state['snap'] = False

col1, col2, col3 = st.columns(3)
with col1:
    start_button = st.button("Start")
with col2: 
    snap_button = st.button("Snap")
with col3:
    stop_button = st.button("Stop")

if start_button:
    st.session_state['start'] = True
if stop_button:
    st.session_state['start'] = False

if st.session_state['start']:
    stframe = st.empty()
    auth_message = st.empty()
    liveness_message = st.empty()

    # Modify your main loop
    prev_frame = None
    blink_counter = 0
    motion_counter = 0
    
    while st.session_state['start']:
        try:
            ret, frame = cap.read()
            if not ret:
                st.error("Failed to capture image")
                break
            
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            dets = detector(rgb_frame, 1)
            
            is_live = False
            texture_real = False
            recognized_names = []
            
            for k, d in enumerate(dets):
                shape = sp(rgb_frame, d)
                face_descriptor = facerec.compute_face_descriptor(rgb_frame, shape)
                face_encoding = np.array(face_descriptor)
                
                # Extract face region for texture analysis
                face_region = rgb_frame[d.top():d.bottom(), d.left():d.right()]
                
                # Liveness detection
                if detect_blinks(shape):
                    blink_counter += 1
                
                if prev_frame is not None and detect_motion(frame, prev_frame):
                    motion_counter += 1
                
                # Texture analysis
                texture_real = analyze_texture(face_region)
                
                # Face recognition
                matches = []
                for known_face_encoding in known_face_encodings:
                    matches.append(np.linalg.norm(known_face_encoding - face_encoding))
                
                min_distance = min(matches)
                if min_distance < 1:
                    name = known_face_names[matches.index(min_distance)]
                else:
                    name = "Unknown"
                
                recognized_names.append(name)

                # Draw a box around the face
                left, top, right, bottom = d.left(), d.top(), d.right(), d.bottom()
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                
                # Draw a label with a name below the face
                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(frame, name, (left + 6, bottom - 6), font, 0.5, (255, 255, 255), 1)
            
            if blink_counter > 1 and motion_counter > 2 and texture_real:
                is_live = True
                
            prev_frame = frame.copy()
            
            stframe.image(frame, channels="BGR")
            
            if is_live:
                liveness_message.success("Live person detected")
            else:
                liveness_message.warning("Liveness not confirmed")
            
            if snap_button:
                st.session_state['snap'] = True
            
            if st.session_state['snap']:
                if not is_live:
                    auth_message.error("Authentication unsuccessful: Not a live person")
                elif not texture_real:
                    auth_message.error("Authentication unsuccessful: Texture analysis failed")
                elif "Unknown" in recognized_names:
                    auth_message.error("Authentication unsuccessful: Unknown person")
                else:
                    auth_message.success(f"Authentication successful: {', '.join(recognized_names)}")
                st.session_state['snap'] = False

            # Reset counters for next frame
            blink_counter = 0
            motion_counter = 0

        except Exception as e:
            st.error(f"Error processing frame: {e}")
else:
    st.write("Click the 'Start' button to begin face recognition.")

# Release the webcam
cap.release()
