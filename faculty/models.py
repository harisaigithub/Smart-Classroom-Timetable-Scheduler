from django.db import models
from django.conf import settings
from core.models import Department

class Faculty(models.Model):
    # Linking to the Custom User model from the accounts app
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        limit_choices_to={'role': 'faculty'}
    )
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='faculty_members')
    designation = models.CharField(max_length=100)
    employee_id = models.CharField(max_length=20, unique=True)
    
    # Workload Constraints (from your requirements)
    max_classes_per_day = models.PositiveIntegerField(default=4)
    max_classes_per_week = models.PositiveIntegerField(default=20)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.department.code}"

    class Meta:
        verbose_name_plural = "Faculty Members"

class FacultyAvailability(models.Model):
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name='availabilities')
    day = models.CharField(max_length=10, choices=[
        ('monday', 'Monday'), ('tuesday', 'Tuesday'), ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'), ('friday', 'Friday'), ('saturday', 'Saturday')
    ])
    # Store the start time to identify which period the professor is busy
    start_time = models.TimeField()
    is_available = models.BooleanField(default=False) # True = Can teach, False = Busy

    class Meta:
        unique_together = ('faculty', 'day', 'start_time')