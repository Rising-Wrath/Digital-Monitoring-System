import streamlit as st
import sqlite3
import pandas as pd
import base64

st.set_page_config(page_title="Notifications ", layout="wide")


# Initialize connection to SQLite database
conn = sqlite3.connect("F:/MCA PROJECT/Final/Data/university.db")
c = conn.cursor()

# Function to fetch students
def fetch_students():
    c.execute('SELECT StudentID, FirstName, MiddleName, LastName, DepartmentID, CourseID FROM Students')
    return c.fetchall()

# Function to fetch department name by ID
def fetch_department_name(department_id):
    c.execute('SELECT Name FROM Departments WHERE DepartmentID = ?', (department_id,))
    result = c.fetchone()
    return result[0] if result else None

# Function to fetch student details by ID
def fetch_student_details(student_id):
    c.execute('SELECT * FROM Students WHERE StudentID = ?', (student_id,))
    return c.fetchone()

# Function to fetch notifications
def fetch_notifications():
    c.execute('SELECT NotificationID, Date, Description, Type, DepartmentName, Attachments FROM Notifications')
    return c.fetchall()

# Function to generate download link for attachments
def get_download_link(file_data, filename):
    b64 = base64.b64encode(file_data).decode()
    href = f'<a href="data:file/;base64,{b64}" download="{filename}">{filename}</a>'
    return href

students = fetch_students()
notifications = fetch_notifications()

# Create a dictionary and options list for the selectbox
student_dict = {f"{id_} - {first_name} {middle_name} {last_name}": id_ for id_, first_name, middle_name, last_name, _, _ in students}
student_options = [f"{id_} - {first_name} {middle_name} {last_name}" for id_, first_name, middle_name, last_name, _, _ in students]

# Find the display value corresponding to the default student ID
default_student_id = 'STU961527236'
default_display_value = next((key for key, value in student_dict.items() if value == default_student_id), None)

# Determine the index of the default value in the options list
default_index = student_options.index(default_display_value) if default_display_value else 0

# Select student ID with the default value set
selected_student = st.selectbox("Select Student", student_options, index=default_index)
selected_student_id = student_dict.get(selected_student)
# Fetch selected student details
if selected_student_id:
    student_details = fetch_student_details(selected_student_id)
    if student_details:
        selected_student_department_id = fetch_department_name(student_details[4])
        selected_student_course_id = student_details[5]

        # Fetch department name for selected student
        selected_student_department_name = fetch_department_name(selected_student_department_id)

        # Display filtered notifications
        st.write("## Relevant Notifications")
        notifications_list = []
        for notification in notifications:
            notification_id, date, description, type_, department_name, attachments = notification
            if (department_name == "All Departments" or department_name == selected_student_department_name) or (selected_student_course_id == "ALL" or selected_student_course_id == selected_student_course_id):
                if attachments:
                    filename = f"attachment_{notification_id}"
                    download_link = get_download_link(attachments, filename)
                else:
                    download_link = "No attachment"
                notifications_list.append([notification_id, date, description, type_, department_name, download_link])

        notifications_df = pd.DataFrame(notifications_list, columns=["NotificationID", "Date", "Description", "Type", "DepartmentName", "Attachments"])
        st.markdown(notifications_df.to_html(escape=False, index=False), unsafe_allow_html=True)
