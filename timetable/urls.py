from django.urls import path
from . import views

urlpatterns = [
    # The 'name' here must match what is in your {% url '...' %} tags
    path('generate/', views.generate_timetable, name='generate_timetable'),
    path('view/', views.timetable_grid_view, name='timetable_view'),
    path('publish/', views.publish_timetable, name='publish_timetable'),
    path('export/pdf/<int:section_id>/', views.export_timetable_pdf, name='export_timetable_pdf'),
    path('public/', views.public_timetable_view, name='public_timetable'),
]