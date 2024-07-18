from django.urls import path
from .views import *
urlpatterns = [
    path('teachers/', TeachersListView.as_view(), name='teachers_list'),
    path('teachers/add/', TeacherCreateView.as_view())

]
