from django.urls import path
from . import views

urlpatterns = [
    # Departments
    path('departments/', views.DepartmentListView.as_view(), name='department_list'),
    path('departments/add/', views.DepartmentCreateView.as_view(), name='department_add'),
    path('departments/edit/<int:pk>/', views.DepartmentUpdateView.as_view(), name='department_edit'),
    path('departments/delete/<int:pk>/', views.DepartmentDeleteView.as_view(), name='department_delete'),

    # Classrooms
    path('classrooms/', views.ClassroomListView.as_view(), name='classroom_list'),
    path('classrooms/add/', views.ClassroomCreateView.as_view(), name='classroom_add'),
    path('classrooms/edit/<int:pk>/', views.ClassroomUpdateView.as_view(), name='classroom_edit'),
    path('classrooms/delete/<int:pk>/', views.ClassroomDeleteView.as_view(), name='classroom_delete'),

    path('subjects/', views.SubjectListView.as_view(), name='subject_list'),
    path('subjects/add/', views.SubjectCreateView.as_view(), name='subject_add'),
    path('subjects/edit/<int:pk>/', views.SubjectUpdateView.as_view(), name='subject_edit'),
    path('subjects/delete/<int:pk>/', views.SubjectDeleteView.as_view(), name='subject_delete'),

    # Feedback URLs
    path('feedback/add/', views.FeedbackCreateView.as_view(), name='feedback_create'),
    path('feedback/manage/', views.AdminFeedbackListView.as_view(), name='admin_feedback_list'),
    path('feedback/resolve/<int:pk>/', views.resolve_feedback, name='resolve_feedback'),
]
