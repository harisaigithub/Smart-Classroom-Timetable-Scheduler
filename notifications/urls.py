from django.urls import path
from . import views

urlpatterns = [
    path('all/', views.notification_list, name='notification_list'),
]