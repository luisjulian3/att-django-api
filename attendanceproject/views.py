import datetime
from collections import Counter
from datetime import datetime as dt
from .models import RoleMaster
import jwt
import pytz
from django.contrib.auth.hashers import check_password
from django.http import JsonResponse
from django.utils import timezone
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from attendancesproject import settings
from .models import User, FaceImage, AttendanceLog
from .serializers import RegistrationSerializer, UserSerializer, UserSearchSerializer, AttendanceLogSerializer, \
    UserDashboardSerializer, UserDashboardAttendanceLogSerializer, UserUpdateSerializer
from .utils import detect_faces, recognize_face, check_location, get_datetime,calculate_working_hours, calculate_presence_status, get_attendance_status


class RegistrationView(APIView):
    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            response_data = {
                'message': 'Registration successful',
                'status': status.HTTP_200_OK
            }
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            error_message = "User with this nik already exists.".join(serializer.errors.get('non_field_errors', []))
            response_data = {
                'message': 'User with this nik already exists.',
                'status': status.HTTP_400_BAD_REQUEST
            }
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)


class UserUpdateView(APIView):
    def post(self, request):
        nik = request.query_params.get('nik')
        print(nik)
        try:
            user = User.objects.get(nik=nik)
        except User.DoesNotExist:
            return JsonResponse({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserUpdateSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=status.HTTP_200_OK)
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginTest(generics.CreateAPIView):
    def post(self, request):
        nik = request.data['nik']
        password = request.data['password']

        user = User.objects.filter(nik=nik).first()

        if user is None:
            response_data = {
                'message': 'User not found',
                'data': None,
                'status': status.HTTP_400_BAD_REQUEST,
                'token': None
            }
            return JsonResponse(response_data, status=status.HTTP_400_BAD_REQUEST)

        if not check_password(password, user.password):
            response_data = {
                'message': 'Password incorrect',
                'data': None,
                'status': status.HTTP_400_BAD_REQUEST,
                'token': None
            }
            return JsonResponse(response_data, status=status.HTTP_400_BAD_REQUEST)

        user_role = RoleMaster.objects.filter(role_id=user.role_id).first()

        if user_role is None:
            response_data = {
                'message': 'Role not found for the user',
                'data': None,
                'status': status.HTTP_400_BAD_REQUEST,
                'token': None
            }
            return JsonResponse(response_data, status=status.HTTP_400_BAD_REQUEST)

        current_time = timezone.now()

        indonesia_timezone = pytz.timezone('Asia/Jakarta')
        current_time = current_time.astimezone(indonesia_timezone)

        exp_timestamp = int((current_time + datetime.timedelta(hours=1)).timestamp())

        iat_timestamp = int(current_time.timestamp())

        payload = {
            'nik': user.nik,
            'exp': exp_timestamp,
            'iat': iat_timestamp,
            'full_name': user.full_name,
            'bind_status': user.bind,
            'attendance_employee_log_flag': user_role.attendance_employee_log,
            'register_employee_flag': user_role.register_employee,
            'settings_employee_flag': user_role.settings_employee,
        }

        token = jwt.encode(payload, 'secret', algorithm='HS256')

        response_data = {
            'message': 'Login Success',
            'data': payload,
            'status': status.HTTP_200_OK,
            'token': token
        }

        response = JsonResponse(response_data, status=status.HTTP_200_OK)
        response.set_cookie('token', token, httponly=True)
        response['Token'] = token

        return response


class HomePageData(APIView):
    def get(self, request):
        token = request.headers.get('Authorization', '').split(' ')[1]

        if not token:
            return Response({'message': 'Unauthenticated!'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
            nik = payload.get('nik')
            user = User.objects.filter(nik=nik).first()

            if not user:
                return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

            user_role = RoleMaster.objects.filter(role_id=user.role_id).first()

            if not user_role:
                return Response({'message': 'Role not found for the user'}, status=status.HTTP_404_NOT_FOUND)

            response_data = {
                'full_name': user.full_name,
                'bind_status': user.bind,
                'attendance_employee_log_flag': user_role.attendance_employee_log,
                'register_employee_flag': user_role.register_employee,
                'settings_employee_flag': user_role.settings_employee,
            }

            return Response({'data': response_data}, status=status.HTTP_200_OK)

        except jwt.ExpiredSignatureError:
            return Response({'message': 'Token has expired'}, status=status.HTTP_401_UNAUTHORIZED)

        except jwt.InvalidTokenError:
            return Response({'message': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)

        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserView(generics.CreateAPIView):
    serializer_class = UserSerializer

    def get(self, request):
        token = request.headers.get('Authorization', '').split(' ')[1]

        if not token:
            return JsonResponse({'Message': 'Unauthenticated!'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return JsonResponse({'Message': 'Unauthenticated!'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(nik=payload['nik']).first()
        serializer = UserSerializer(user)

        return JsonResponse(serializer.data)


class UserViewLog(APIView):
    serializer_class = UserSerializer

    def get(self, request):
        nik = request.query_params.get('nik')

        if not nik:
            return Response({'Message': 'Missing "nik" parameter'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(nik=nik).first()

        if not user:
            return Response({'Message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserSerializer(user)
        return Response(serializer.data)


class UserSearch(generics.ListAPIView):
    serializer_class = UserSearchSerializer

    def get_queryset(self):
        nik = self.request.query_params.get('nik', None)
        if nik and len(nik) >= 2:
            queryset = User.objects.filter(nik__icontains=nik)
            return queryset
        else:
            return User.objects.none()


class LogoutView(APIView):
    def post(self, request):
        response = Response()
        response.delete_cookie('jwt')
        response.data = {
            'message': 'Logout Success'
        }
        return JsonResponse.response


class DeleteAllDataView(generics.CreateAPIView):
    def delete(self, request):
        try:
            User.objects.all().delete()
            FaceImage.objects.all().delete()
            AttendanceLog.objects.all().delete()

            return Response({'message': 'All data deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TrainFace(generics.CreateAPIView):
    def post(self, request):
        image_file = request.FILES['image']
        nik = request.data['nik']
        image_data = image_file.read()

        try:
            message, status_code = detect_faces(image_data, settings.BASE_DIR, nik)
            return JsonResponse({'message': message, 'status': status_code}, status=status_code)

        except ValueError as ve:
            return JsonResponse({'message': str(ve), 'status': 400}, status=400)

        except Exception as e:
            return JsonResponse({'message': str(e), 'status': 500}, status=500)


GOOGLE_API_KEY = 'AIzaSyBDG4ESuCfHW8GjrYhnpu_X9LQF5YJfojU'


class RecognizeAttendanceIN(generics.CreateAPIView):
    def post(self, request):
        try:
            image_file = request.FILES['image']
            nik = request.data['nik']
            latitude = request.data.get('latitude')
            longitude = request.data.get('longitude')
            print(nik)

            current_datetime = get_datetime()

            attendance_date = current_datetime.date()
            today = attendance_date.today()

            existing_logs = AttendanceLog.objects.filter(nik=nik, attendance_date=today)

            if existing_logs.exists():
                return JsonResponse({'message': 'Attendance has already been logged for today'},
                                    status=status.HTTP_400_BAD_REQUEST)

            if latitude is None or longitude is None:
                return JsonResponse({'message': 'Latitude and longitude are required'},
                                    status=status.HTTP_400_BAD_REQUEST)

            office_name = check_location(latitude, longitude)

            if not office_name:
                return JsonResponse({'message': 'No office location found near the provided coordinates'},
                                    status=status.HTTP_400_BAD_REQUEST)

            message, status_code = recognize_face(image_file.read(), settings.BASE_DIR, nik)
            print('message', message)
            if status_code == 200:
                attendance_date = get_datetime()
                attendance_in_time = attendance_date.time()
                formatted_time = attendance_in_time.strftime('%H:%M:%S')

                attendance_status = get_attendance_status(formatted_time)
                print(attendance_status)
                print(attendance_in_time)

                attendance_log = AttendanceLog.objects.create(
                    nik=nik,
                    user_id=nik,
                    presence_status='AWT',
                    attendance_office=office_name,
                    attendance_in_status=attendance_status,
                    attendance_date=attendance_date,
                    attendance_in_time=formatted_time,
                    longitude_in=longitude,
                    latitude_in=latitude
                )

                attendance_log.save()

                return JsonResponse({
                    'message': 'Attendance In Success',
                    'status': status_code,
                    'presence_status': 'AWT',
                    'office_name': office_name
                }, status=status_code)
            else:
                return JsonResponse({'message': 'Face doesnt match', 'status:': status_code}, status=status_code)

        except ValueError as ve:
            return JsonResponse({'message': 'No faces detected in the provided image.', 'status': 404}, status=404)


class RecognizeAttendanceOUT(generics.CreateAPIView):
    def post(self, request):
        try:
            image_file = request.FILES['image']
            nik = request.data['nik']
            latitude = request.data.get('latitude')
            longitude = request.data.get('longitude')
            current_datetime = get_datetime()

            attendance_date = current_datetime.date()
            today = attendance_date.today()
            existing_logs = AttendanceLog.objects.filter(nik=nik, attendance_date=today)

            if not existing_logs.exists():
                return JsonResponse({'message': 'havent done any attendance yet today'},
                                    status=status.HTTP_404_NOT_FOUND)

            attendance_log = existing_logs.first()

            if attendance_log.attendance_out_time:
                return JsonResponse({'message': 'Attendance out already logged'},
                                    status=status.HTTP_400_BAD_REQUEST)

            if latitude is None or longitude is None:
                return JsonResponse({'message': 'Latitude and longitude are required'},
                                    status=status.HTTP_400_BAD_REQUEST)

            office_name = check_location(latitude, longitude)

            if not office_name:
                return JsonResponse({'message': 'No office location found near the provided coordinates'},
                                    status=status.HTTP_400_BAD_REQUEST)

            if office_name != attendance_log.attendance_office:
                return JsonResponse({'message': 'Office does not match the attendance log office'},
                                    status=status.HTTP_400_BAD_REQUEST)

            message, status_code = recognize_face(image_file.read(), settings.BASE_DIR, nik)

            if status_code == 200:
                attendance_date = get_datetime()
                attendance_in_time = attendance_date.time()
                formatted_time = attendance_in_time.strftime('%H:%M:%S')

                attendance_in_time_str = attendance_log.attendance_in_time.strftime('%H:%M:%S')
                working_hours = calculate_working_hours(attendance_in_time_str, formatted_time)

                presence_status = calculate_presence_status(working_hours)
                attendance_log.attendance_out = True
                attendance_log.attendance_out_time = formatted_time
                attendance_log.working_hours = working_hours
                attendance_log.latitude_out = latitude
                attendance_log.longitude_out = longitude
                attendance_log.presence_status = presence_status
                attendance_log.save()

                return JsonResponse({'message': 'Attendance Out Success', 'status:': status_code}, status=status_code)
            else:
                return JsonResponse({'message': message, 'status:': status_code}, status=status_code)

        except ValueError as ve:
            return JsonResponse({'message': 'No faces detected in the provided image.', 'status': 404}, status=404)

        except Exception as e:
            return JsonResponse({'message': 'An error occurred during image processing.', 'status': 500}, status=500)


class AttendanceLogList(generics.ListAPIView):
    serializer_class = AttendanceLogSerializer

    def get(self, request, *args, **kwargs):
        nik = request.query_params.get('nik', None)
        start_date = request.query_params.get('start_date', None)
        end_date = request.query_params.get('end_date', None)

        if nik is None:
            return JsonResponse({"data": []})

        queryset = AttendanceLog.objects.filter(nik=nik)

        if start_date and end_date:
            start_date = dt.strptime(start_date, "%Y-%m-%d").date()
            end_date = dt.strptime(end_date, "%Y-%m-%d").date()

            queryset = queryset.filter(attendance_date__range=(start_date, end_date))

        queryset = queryset.order_by('-attendance_date')

        serializer = self.serializer_class(queryset, many=True)

        presence_status_count = Counter(log['presence_status'] for log in serializer.data)

        data = {
            "data": serializer.data,
            "presence_status_count": dict(presence_status_count)
        }

        return JsonResponse(data, safe=False)


class DashboardView(APIView):
    def get(self, request):
        token = request.headers.get('Authorization', '').split(' ')[1]

        if not token:
            return Response({'Message': 'Unauthenticated!'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return Response({'Message': 'Unauthenticated!'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.get(nik=payload['nik'])

        attendance_logs = AttendanceLog.objects.filter(user=user).order_by('-attendance_date')[:3]

        user_serializer = UserDashboardSerializer(user)

        attendance_logs_serializer = UserDashboardAttendanceLogSerializer(attendance_logs, many=True)

        response_data = {
            'user': user_serializer.data,
            'attendance_logs': attendance_logs_serializer.data
        }
        print(response_data)

        return Response(response_data)
