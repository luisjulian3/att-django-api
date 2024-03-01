from django.contrib import admin
from django.urls import path
from attendanceproject.views import RegistrationView, LoginTest, LogoutView, UserView, DeleteAllDataView, \
    TrainFace, RecognizeAttendanceIN, RecognizeAttendanceOUT, UserSearch, UserViewLog, AttendanceLogList, \
    DashboardView, HomePageData, UserUpdateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', RegistrationView.as_view(), name='register'),
    path('logintest/', LoginTest.as_view(), name='logintest'),
    path('update', UserUpdateView.as_view(), name='user-update'),
    path('home/', HomePageData.as_view(), name='logintest'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('userview/', UserView.as_view(), name='userview'),
    path('delete-all-data/', DeleteAllDataView.as_view(), name='delete-all-data'),
    path('trainface/', TrainFace.as_view(), name='trainface'),
    path('attendancein/', RecognizeAttendanceIN.as_view(), name='recogface'),
    path('attendanceout/', RecognizeAttendanceOUT.as_view(), name='recogface'),
    path('search', UserSearch.as_view(), name='usersearchadmin'),
    path('userviewlog/',UserViewLog.as_view(), name='userviewlog'),
    path('attendance-logs/', AttendanceLogList.as_view(), name='attendance-log-list'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
]
