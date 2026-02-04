from django.urls import path
from . import views

urlpatterns = [
    path('list/', views.FacultyListView.as_view(), name='faculty_list'),
    path('add/', views.FacultyCreateView.as_view(), name='faculty_add'),
    path('dashboard/', views.faculty_dashboard, name='user_dashboard'),
    path('availability/', views.availability_matrix, name='faculty_availability'), # ADD THIS LINE
]