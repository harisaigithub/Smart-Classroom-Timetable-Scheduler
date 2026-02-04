from django.db import models
from django.conf import settings

class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True) # e.g., CSE, MECH
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.code})"

from django.db import models

class Classroom(models.Model):
    ROOM_TYPES = [('classroom', 'Classroom'), ('lab', 'Laboratory')]
    
    name = models.CharField(max_length=50, unique=True)
    capacity = models.PositiveIntegerField()
    room_type = models.CharField(max_length=20, choices=ROOM_TYPES, default='classroom')
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    # Dynamic Utilization Calculation
    def get_weekly_utilization(self):
        """Calculates how many slots this specific room is occupied."""
        from timetable.models import TimetableEntry
        from scheduler.models import TimeSlot
        
        total_slots = TimeSlot.objects.filter(is_break=False).count()
        occupied_slots = TimetableEntry.objects.filter(classroom=self).count()
        
        if total_slots == 0: return 0
        return round((occupied_slots / total_slots) * 100)

class Semester(models.Model):
    number = models.PositiveSmallIntegerField() # 1 to 8
    academic_year = models.CharField(max_length=20) # e.g., 2025-2026

    def __str__(self):
        return f"Semester {self.number} ({self.academic_year})"

class Section(models.Model):
    name = models.CharField(max_length=10) # e.g., A, B, C
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='sections')
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    student_count = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.department.code} - Sem {self.semester.number} - Sec {self.name}"
    
class Subject(models.Model):
    SUBJECT_TYPES = [('theory', 'Theory'), ('lab', 'Laboratory')]
    
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    subject_type = models.CharField(max_length=10, choices=SUBJECT_TYPES, default='theory')
    
    # Requirement E: Credit & Class configuration
    credit_hours = models.PositiveIntegerField(default=3)
    classes_per_week = models.PositiveIntegerField(default=3)
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    

class Feedback(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    subject = models.CharField(max_length=150)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.subject} - {self.user.email}"