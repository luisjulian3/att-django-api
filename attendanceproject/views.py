import datetime
import os

import cv2
import jwt
import numpy as np
import requests
import yaml
from django.contrib.auth.hashers import check_password
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseServerError, JsonResponse
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from attendancesproject import settings
from .models import User, FaceImage, AttendanceLog
from .serializers import RegistrationSerializer, UserSerializer
from .utils import format_datetime, calculate_distance, detect_faces, train_lbph_on_detected_faces, save_detected_faces


class RegistrationView(generics.CreateAPIView):
    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            response_data = {
                'message': 'Login Succes',
                'data': serializer.data,
                'status': status.HTTP_200_OK
            }
            return Response(response_data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginTest(generics.CreateAPIView):
    def post(self, request):
        nik = request.data['nik']
        password = request.data['password']

        print(password)

        user = User.objects.filter(nik=nik).first()

        if user is None:
            return Response({'User no Found'}, status=status.HTTP_400_BAD_REQUEST)

        if not check_password(password, user.password):
            return Response({'password fail'}, status=status.HTTP_400_BAD_REQUEST)

        payload = {
            'nik': user.nik,
            'exp': format_datetime(datetime.datetime.now() + datetime.timedelta(minutes=60)),
            'iat': format_datetime(datetime.datetime.now())
        }

        token = jwt.encode(payload, 'secret', algorithm='HS256')

        jwt_data = Response()

        jwt_data.set_cookie(key='jwt', value=token, httponly=True)
        jwt_data = {
            'jwt': token
        }

        response_data = {
            'message': 'Login Succes',
            'data': payload,
            'status': status.HTTP_200_OK
        }

        return Response(response_data)


class UserView(generics.CreateAPIView):
    serializer_class = UserSerializer

    def get(self, request):
        token = request.COOKIES.get('jwt')

        if not token:
            return Response({'Unauthenticated!'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return Response({'Unauthenticated!'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(nik=payload['nik']).first()
        serializer = UserSerializer(user)

        return Response(serializer.data)


class LogoutView(APIView):
    def post(self, request):
        response = Response()
        response.delete_cookie('jwt')
        response.data = {
            'message': 'Logout Success'
        }
        return response


class DeleteAllDataView(generics.CreateAPIView):
    def delete(self, request):
        try:
            # Delete all instances of YourModel
            User.objects.all().delete()
            FaceImage.objects.all().delete()
            AttendanceLog.objects.all().delete()

            return Response({'message': 'All data deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


GOOGLE_API_KEY = 'AIzaSyBDG4ESuCfHW8GjrYhnpu_X9LQF5YJfojU'


class Loc(generics.CreateAPIView):
    def get(self, request):
        latitude = request.data.get('latitude')
        longitude = request.data.get('longitude')
        declared_latitude = -6.245019817727446
        declared_longitude = 106.64977656394416

        url = f'https://maps.googleapis.com/maps/api/geocode/json?latlng={latitude},{longitude}&key={GOOGLE_API_KEY}'
        response = requests.get(url)

        if latitude is None or longitude is None:
            return Response({'message': 'Latitude and longitude are required'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the provided latitude and longitude are within 5km of the declared area
        distance = calculate_distance(declared_latitude, declared_longitude, float(latitude), float(longitude))

        if distance <= 5:  # Within 5km radius
            return Response({'message': 'Within 5km radius'}, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'Outside 5km radius'}, status=status.HTTP_200_OK)


class TrainFace(generics.CreateAPIView):
    def post(self, request):
        image_file = request.FILES['image']
        nik = request.data['nik']

        # Read the uploaded image
        image_data = image_file.read()
        try:
            # Call the detect_faces function
            faces, gray = detect_faces(image_data, settings.BASE_DIR)
            save_detected_faces(settings.BASE_DIR, nik, faces, gray)
            train_lbph_on_detected_faces(settings.BASE_DIR)
            return HttpResponse('Image processed successfully!')
        except ValueError as e:
            return HttpResponseBadRequest(str(e))
        except Exception as e:
            return HttpResponseServerError('An error occurred during image processing.')


class RecognizeFace(generics.CreateAPIView):
    def post(self, request):
        nik = request.data['nik']

        # Read the uploaded image
        image_file = request.FILES['image']
        image_data = image_file.read()

        try:
            # Convert the image to grayscale
            img = cv2.imdecode(np.fromstring(image_data, np.uint8), cv2.IMREAD_COLOR)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # Load the LBPH recognizer
            recognizer = cv2.face.LBPHFaceRecognizer_create()
            recognizer.read(os.path.join(settings.BASE_DIR, 'lbph_model.yml'))


            # Perform face recognition
            label, confidence = recognizer.predict(gray)

            return JsonResponse({'recognized_face': {'label': label, 'confidence': confidence}})
        except ValueError as e:
            return HttpResponseBadRequest(str(e))
        except Exception as e:
            print(f'Error: {e}')
            return HttpResponseServerError('Terjadi kesalahan selama proses pengenalan wajah.')
