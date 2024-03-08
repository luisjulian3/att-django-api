from datetime import datetime, time, timedelta
from math import radians, sin, cos, sqrt, atan2, inf
import pytz
import cv2
import numpy as np
import os

from attendanceproject.models import FaceImage, User, OfficeMaster
from attendancesproject import settings
from attendancesproject.settings import BASE_DIR


def get_datetime(timezone_name='Asia/Jakarta'):
    timezone_obj = pytz.timezone(timezone_name)
    current_datetime = datetime.now(timezone_obj)
    return current_datetime


def format_time(time_obj):
    return time_obj.strftime('%H:%M:%S')


def calculate_distance(lat1, lon1, lat2, lon2):
    # Radius of the Earth in km
    R = 6371.0

    # Convert latitude and longitude from degrees to radians
    lat1_rad = radians(lat1)
    lon1_rad = radians(lon1)
    lat2_rad = radians(lat2)
    lon2_rad = radians(lon2)

    # Calculate differences between latitudes and longitudes
    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad

    # Calculate distance using Haversine formula
    a = sin(dlat / 2) ** 2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c

    return distance


def calculate_working_hours(attendance_in_time_str, attendance_out_time_str):
    # Parse attendance_in_time and attendance_out_time strings into datetime objects
    attendance_in_datetime = datetime.strptime(attendance_in_time_str, '%H:%M:%S')
    attendance_out_datetime = datetime.strptime(attendance_out_time_str, '%H:%M:%S')

    # Calculate the difference between attendance_out_time and attendance_in_time
    working_hours_timedelta = attendance_out_datetime - attendance_in_datetime

    # Calculate hours, minutes, and seconds from the timedelta
    total_seconds = working_hours_timedelta.total_seconds()
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    seconds = int(total_seconds % 60)

    # Convert the total seconds to a time object
    working_hours_time = time(hours, minutes, seconds)

    return working_hours_time


def check_location(latitude, longitude):
    # Fetch all office locations from the database
    offices = OfficeMaster.objects.all()

    # Initialize variables to keep track of the nearest office
    nearest_office_name = None
    nearest_distance = inf

    # Iterate through each office and check the distance
    for office in offices:
        distance = calculate_distance(float(latitude), float(longitude), float(office.office_lat),
                                      float(office.office_long))
        if distance < 1 and distance < nearest_distance:
            nearest_distance = distance
            nearest_office_name = office.office_name

    # Return the nearest office name if found within 1 km, otherwise return None
    return nearest_office_name


def calculate_presence_status(working_hours):
    # Define the threshold for a full working day (8 hours)
    full_day_threshold = time(hour=8)

    # Compare working_hours with the threshold and determine presence status
    if working_hours >= full_day_threshold:
        return 'PRS'  # Present
    else:
        return 'LE'  # Late


def get_attendance_status(attendance_time):
    # Define the time ranges
    late_start_time = time(7, 15, 0)
    late_end_time = time(23, 59, 59)
    late_end_time_next_day = time(4, 0, 0)
    in_time_start_time = time(6, 0, 0)
    in_time_end_time = time(7, 15, 0)
    early_start_time = time(4, 0, 0)
    early_end_time = time(6, 0, 0)

    # Convert the string attendance time to a datetime object
    attendance_datetime = datetime.strptime(attendance_time, '%H:%M:%S').time()

    # Check the attendance status based on the time ranges
    if late_start_time <= attendance_datetime <= late_end_time or attendance_datetime <= late_end_time_next_day:
        return 'Late'
    elif early_start_time <= attendance_datetime <= early_end_time:
        return 'Early'
    elif in_time_start_time <= attendance_datetime <= in_time_end_time:
        return 'In Time'
    else:
        return 'Absent'


def process_image(image_data, base_dir):
    nparr = np.fromstring(image_data, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # Loading the face detection classifier
    xml_path = os.path.join(base_dir, 'xml', 'haarcascade_frontalface_default.xml')
    face_cascade = cv2.CascadeClassifier(xml_path)

    # Convert the image to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Detect faces in the image
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=4, minSize=(20, 20))

    return img, gray, faces


def detect_faces(image_data, base_dir, nik):
    try:
        existing_face = FaceImage.objects.filter(nik=nik).exists()
        if existing_face:
            raise ValueError("Face already registered for the provided NIK")

        img, gray, faces = process_image(image_data, base_dir)

        if len(faces) == 0:
            raise ValueError("No faces detected in the provided image")
        img, gray, faces = process_image(image_data, base_dir)

        save_detected_faces(gray, faces, base_dir, nik)
        print('asdasd')
        train_lbph_model(nik)
        print('1231231')

        # Set the 'bind' field of the user to True
        user = User.objects.get(nik=nik)
        user.bind = True
        user.save()

        return 'Image processed successfully!', 200
    except User.DoesNotExist:
        return 'User with provided NIK does not exist', 404

    except ValueError as ve:
        return str(ve), 400

    except Exception as e:
        return f'An error occurred: {str(e)}', 500


def save_detected_faces(gray, faces, base_dir, nik):
    try:
        user = User.objects.get(nik=nik)
    except User.DoesNotExist:
        return None

    face_images = []
    for i, (x, y, w, h) in enumerate(faces):
        face_region = gray[y:y + h, x:x + w]

        filename = f'face_{nik}.jpg'
        save_path = os.path.join(base_dir, 'detected_faces', filename)

        cv2.imwrite(save_path, face_region)

        face_image = FaceImage.objects.create(
            nik=nik,
            image_id=filename,
            image=save_path,
            image_path=save_path
        )
        face_images.append(face_image)

    return face_images


def train_lbph_model(nik):
    faces = FaceImage.objects.filter(nik=nik)
    labels = []
    images = []

    for face in faces:
        image = cv2.imread(face.image.path)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        images.append(gray)
        labels.append(face.nik)

    # Convert labels to numpy array
    labels = np.array(labels)

    lbph_model = cv2.face.LBPHFaceRecognizer_create()
    lbph_model.train(images, labels)

    # Save the LBPH model
    lbph_model_path = os.path.join(settings.BASE_DIR, 'trained_models', f'lbph_model_{nik}.yml')
    lbph_model.save(lbph_model_path)


def recognize_face(image_data, base_dir, nik):
    try:
        img, gray, faces = process_image(image_data, base_dir)

        recognized_results = []
        # Check if faces are detected
        if len(faces) == 0:
            raise ValueError("No faces detected in the provided image")

        # Load the LBPH recognizer
        recognizer = cv2.face.LBPHFaceRecognizer_create()

        # Load the trained model based on the provided nik
        model_path = os.path.join(base_dir, 'trained_models', f'lbph_model_{nik}.yml')
        recognizer.read(model_path)

        # Process each detected face
        for idx, (x, y, w, h) in enumerate(faces):
            face_region = gray[y:y + h, x:x + w]

            # Perform face recognition using the loaded model
            label, confidence = recognizer.predict(face_region)
        print(confidence)
        if confidence <= 55:
            return confidence, 200
        else:
            return confidence, 400  # 200 is the HTTP status code for success

    except ValueError as ve:
        # Custom error message for "No faces detected" case
        return str(ve), 404  # 404 is the HTTP status code for not found

    except Exception as e:
        # Generic error message for other exceptions
        return f'An error occurred: {str(e)}', 500
