import cv2
from PIL import Image
import numpy as np
import dlib
import os
import streamlit as st
import sqlite3
import time
import json
import pandas as pd
from datetime import datetime



# Set the page config
st.set_page_config(page_title="Time Tracker", page_icon=":alarm_clock:", layout="wide")

# Initialize session state for the timer and data storage
if 'timer_running' not in st.session_state:
    st.session_state.timer_running = False
    st.session_state.start_time = None
    st.session_state.data = []  # Initialize a list to store data entries
    st.session_state.attendance_input = ""  # Initialize attendance input
if 'student_present' not in st.session_state:
    st.session_state.student_present = False

# Connect to SQLite database
conn = sqlite3.connect('F:/MCA PROJECT/Final/Data/university.db')
cursor = conn.cursor()

# Define timer functions
def start_timer():
    st.session_state.timer_running = True
    st.session_state.start_time = time.time()
    st.session_state.start_time_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def stop_timer():
    try:
        st.session_state.timer_running = False
        elapsed_time = time.time() - st.session_state.start_time
        stop_time_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        student_id = st.session_state.selected_student
        attendance_id = f"STUD{datetime.now().strftime('%Y%m%d')}"
        routine_id = f"{st.session_state.selected_routine_id}{datetime.now().strftime('%Y%m%d')}"

        data_entry = {
            "StudentId": student_id,
            "ClassID": routine_id,
            "CourseID": st.session_state.selected_course_id,
            "Date": datetime.now().strftime('%Y-%m-%d'),
            "Out": stop_time_str,
            "SubjectTopic": st.session_state.attendance_input,
            "Room": st.session_state.selected_classroom,
            "Duration": round(elapsed_time, 2),
            "Attendance": "Present",
            "Logs": f"Started at: {st.session_state.start_time_str}, Stopped at: {stop_time_str}",
            "InTime": st.session_state.start_time_str
        }

        st.session_state.data.append(data_entry)
        st.session_state.attendance_input = ""  # Clear the input field
        save_to_database(data_entry)
    except Exception as e:
        st.error(f"Error stopping the timer: {e}")

def save_to_database(data_entry):
    try:
        cursor.execute("""
            INSERT INTO StudentAttendance (ClassID, CourseID, StudentId, Date, Out, SubjectTopic, Room, Duration, Attendance, Logs, InTime) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data_entry["ClassID"], data_entry["CourseID"], data_entry["StudentId"], data_entry["Date"],
            data_entry["Out"], data_entry["SubjectTopic"], data_entry["Room"], data_entry["Duration"],
            data_entry["Attendance"], data_entry["Logs"], data_entry["InTime"]
        ))
        conn.commit()
    except Exception as e:
        st.error(f"Error saving to database: {e}")

def get_student_routine(student_id):
    try:
        query = """
            SELECT Routine.StartTime, Routine.EndTime, Routine.Subject, Routine.Classroom, Routine.TeacherName
            FROM Routine
            JOIN Courses ON Routine.CourseID = Courses.CourseID
            JOIN Students ON Courses.CourseID = Students.CourseId
            WHERE Students.StudentID = ? AND Routine.DayOfWeek = ?
        """
        day_of_week = datetime.now().strftime('%A')
        cursor.execute(query, (student_id, day_of_week))
        return cursor.fetchall()
    except Exception as e:
        st.error(f"Error fetching student routine: {e}")
        return []

def get_students():
    try:
        cursor.execute("SELECT StudentID, FirstName, LastName FROM Students")
        return cursor.fetchall()
    except Exception as e:
        st.error(f"Error fetching students: {e}")
        return []

def get_today_data(student_id):
    try:
        today_date = datetime.now().strftime('%Y-%m-%d')
        cursor.execute("SELECT * FROM StudentAttendance WHERE StudentId = ? AND Date = ?", (student_id, today_date))
        return cursor.fetchall()
    except Exception as e:
        st.error(f"Error fetching today's data: {e}")
        return []

# Load class state
def load_state():
    try:
        with open('F:/MCA PROJECT/Final/Data/class_state.json', 'r') as f:
            state = json.load(f)
            st.session_state.class_started = state['class_started']
            st.session_state.timer_start = state['timer_start']
    except FileNotFoundError:
        st.session_state.class_started = False
        st.session_state.timer_start = 0

def mark_present():
    st.session_state.student_present = not st.session_state.student_present

def capture_image():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        st.error("Error: Could not open webcam.")
        return None

    ret, frame = cap.read()
    if not ret:
        st.error("Error: Could not read frame.")
        return None

    cap.release()
    return frame

load_state()

students = get_students()

# Select Student
student_ids = [student[0] for student in students]
student_names = [f"{student[1]} {student[2]}" for student in students]

# Set default student
default_student_id = "STU961527236"
if default_student_id in student_ids:
    default_index = student_ids.index(default_student_id)
else:
    default_index = 0

selected_student_index = st.selectbox("Selected Student", range(len(student_ids)), index=default_index, format_func=lambda x: student_names[x])
st.session_state.selected_student = student_ids[selected_student_index]


# Initialize session state for the timer and data storage
if 'timer_running' not in st.session_state:
    st.session_state.timer_running = False
    st.session_state.start_time = None
    st.session_state.data = []  # Initialize a list to store data entries
    st.session_state.attendance_input = ""  # Initialize attendance input

# Define timer functions
def start_timer():
    st.session_state.timer_running = True
    st.session_state.start_time = time.time()
    st.session_state.start_time_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def stop_timer():
    st.session_state.timer_running = False
    elapsed_time = time.time() - st.session_state.start_time
    stop_time_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    st.session_state.data.append({
        "What do you learn?": st.session_state.attendance_input,
        "Start time": st.session_state.start_time_str,
        "Stop time": stop_time_str,
        "Duration( in seconds)": round(elapsed_time, 2)
    })
    st.session_state.attendance_input = ""  # Clear the input field
    save_to_excel(st.session_state.data)

def save_to_excel(data):
    df = pd.DataFrame(data)
    df.to_excel("attendance_data.xlsx", index=False)

# Load pre-trained face detection and face recognition models
detector = dlib.get_frontal_face_detector()
sp = dlib.shape_predictor("F:/MCA PROJECT/Final/Data/shape_predictor_68_face_landmarks.dat")
facerec = dlib.face_recognition_model_v1("F:/MCA PROJECT/Final/Data/dlib_face_recognition_resnet_model_v1.dat")

# Function to load and prepare face data from a directory
def load_face_data(directory):
    known_face_encodings = []
    known_face_names = []
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
    return known_face_encodings, known_face_names

# Load saved faces from directory
saved_faces_directory = 'F:/MCA PROJECT/Final/Data/SavedFaces'
known_face_encodings, known_face_names = load_face_data(saved_faces_directory)

# Initialize webcam
cap = cv2.VideoCapture(0)

# Time tracker section
st.write("### Time Tracker")
left, right = st.columns([3, 1])
with left:
    with st.form(key='attendance_form'):
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            st.session_state.attendance_input = st.text_input("What did you learn?", "")
        with col2:
            add_button = st.form_submit_button(label=':heavy_plus_sign: Add')
        with col3:
            snap_button = st.form_submit_button(label=':camera: Snap')

if 'captured_image' not in st.session_state:
    st.session_state.captured_image = None

if snap_button:
    st.session_state.captured_image = capture_image()
    if st.session_state.captured_image is not None:
        image_pil = Image.fromarray(cv2.cvtColor(st.session_state.captured_image, cv2.COLOR_BGR2RGB))
        st.image(image_pil, caption='Captured Image')
        
        # Face recognition
        img_rgb = cv2.cvtColor(st.session_state.captured_image, cv2.COLOR_BGR2RGB)
        dets = detector(img_rgb, 1)
        if len(dets) == 0:
            st.error("No face detected. Please try again.")
        else:
            for k, d in enumerate(dets):
                shape = sp(img_rgb, d)
                face_descriptor = facerec.compute_face_descriptor(img_rgb, shape)
                face_encoding = np.array(face_descriptor)

                distances = np.linalg.norm(known_face_encodings - face_encoding, axis=1)
                min_distance = np.min(distances)
                if min_distance < 0.6:  # You can adjust the threshold as needed
                    matched_idx = np.argmin(distances)
                    matched_name = known_face_names[matched_idx]
                    st.success(f"Face recognized: {matched_name}")
                    st.session_state.student_present = True
                    st.session_state.timer_running = True  # Enable timer if face recognized
                    start_timer()
                else:
                    st.error("Face not recognized. Please try again.")
                    st.session_state.student_present = False
                    st.session_state.timer_running = False

with right:
    if st.session_state.timer_running:
        stop_button = st.button("Stop")
        if stop_button:
            stop_timer()
    else:
        start_button = st.button("Start")
        if start_button:
            if not st.session_state.student_present:
                st.warning("Please take a snapshot to start the timer.")
            else:
                start_timer()

# Display the attendance log
st.write("### Attendance Log")
df = pd.DataFrame(st.session_state.data)
st.table(df)

# Display today's routine
st.write("### Today's Routine")
routine = get_student_routine(st.session_state.selected_student)
routine_df = pd.DataFrame(routine, columns=["StartTime", "EndTime", "Subject", "Classroom", "TeacherName"])
st.table(routine_df)

# Clean up and release webcam
cap.release()
cv2.destroyAllWindows()
conn.close()
