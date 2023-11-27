from django.contrib import admin
from django.urls import path
from attendanceproject.views import RegistrationView, LoginTest, LogoutView, UserView, DeleteAllDataView, Loc, TrainFace, RecognizeFace

urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', RegistrationView.as_view(), name='register'),
    path('logintest/', LoginTest.as_view(), name='logintest'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('userview/', UserView.as_view(), name='userview'),
    path('delete-all-data/', DeleteAllDataView.as_view(), name='delete-all-data'),
    path('loc/', Loc.as_view(), name='loc'),
    path('trainface/', TrainFace.as_view(), name='trainface'),
    path('recogface/', RecognizeFace.as_view(), name='trainface'),

]
