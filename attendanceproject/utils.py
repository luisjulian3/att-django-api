import datetime
import os
import xml
from math import radians, sin, cos, sqrt, atan2

import cv2
import numpy as np
import yaml

from attendanceproject.models import FaceImage
from attendancesproject.settings import BASE_DIR


def format_datetime(dt):
    return dt.strftime("%Y-%m-%d %H:%M:%S")


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


def train_lbph_model():
    faces = FaceImage.objects.all()
    labels = []
    images = []

    xml_path = '/xml'
    file_name = 'haarcascade_frontalface_default.xml'
    face_cascade = cv2.CascadeClassifier(xml_path + file_name)

    for face in faces:
        image = cv2.imread(face.image.path)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        if len(faces) == 1:
            (x, y, w, h) = faces[0]

            face_region = gray[y:y + h, x:x + w]

            lbp = cv2.face.LBPHFaceRecognizer_create()
            labels.append(face.id)
            images.append(face_region)

    lbph_model = cv2.face.LBPHFaceRecognizer_create()
    lbph_model.train(images, np.array(labels))
    print(lbph_model)
    print(lbph_model.train(images, np.array(labels)))
    lbph_model.save('lbph_model.yml')


def detect_faces(image_data, base_dir):
    print('a')
    nparr = np.fromstring(image_data, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    # Loading the face detection classifier
    xml_path = os.path.join(base_dir, 'xml', 'haarcascade_frontalface_default.xml')
    face_cascade = cv2.CascadeClassifier(xml_path)

    # Convert the image to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Detect faces in the image
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    # Create a directory for each user if it doesn't exist
    return faces, gray


def save_detected_faces(base_dir, nik, faces, gray):
    # Create a directory for each user if it doesn't exist
    user_faces_dir = os.path.join(base_dir, 'detected_faces')
    os.makedirs(user_faces_dir, exist_ok=True)

    # Save the detected faces with unique filenames
    for idx, (x, y, w, h) in enumerate(faces):
        # Crop the detected face region
        cropped_face = gray[y:y + h, x:x + w]

        # Define a unique filename based on nik and index
        save_path = os.path.join(user_faces_dir, f'face_{nik}_{idx}.jpg')

        # Save the cropped face
        cv2.imwrite(save_path, cropped_face)


def train_lbph_on_detected_faces(base_dir):
    print('1')
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    print('2')

    faces = []
    labels = []

    detected_faces_path = os.path.join(base_dir, 'detected_faces')
    for filename in os.listdir(detected_faces_path):
        print(filename)
        if filename.endswith('.jpg'):
            face_path = os.path.join(detected_faces_path, filename)
            label = int(filename.split('_')[1].split('.')[0])
            face_image = cv2.imread(face_path, cv2.IMREAD_GRAYSCALE)

            faces.append(face_image)
            labels.append(label)
    print('3')
    recognizer.train(faces, np.array(labels))
    recognizer.save(os.path.join(base_dir, 'lbph_model.yml'))
    print('4')

