from django.db import models

class TimeSlot(models.Model):
    # Requirement G: Defining the day structure
    DAYS_OF_WEEK = [
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
    ]

    day = models.CharField(max_length=10, choices=DAYS_OF_WEEK)
    start_time = models.TimeField()
    end_time = models.TimeField()
    
    # Requirement G: Identify breaks like lunch or short breaks
    is_break = models.BooleanField(default=False)
    break_name = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        ordering = ['start_time']
        unique_together = ('day', 'start_time', 'end_time')

    def __str__(self):
        return f"{self.get_day_display()}: {self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')}"

class ScheduleConfig(models.Model):
    # Global constraints for the engine (Requirement G)
    max_classes_per_day = models.PositiveIntegerField(default=7)
    working_days = models.PositiveIntegerField(default=5)
    academic_year = models.CharField(max_length=20)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Config {self.academic_year}"
    
class FixedSlot(models.Model):
    # Requirement G: Special slots that the generator cannot move
    subject = models.ForeignKey('core.Subject', on_delete=models.CASCADE)
    faculty = models.ForeignKey('faculty.Faculty', on_delete=models.CASCADE)
    classroom = models.ForeignKey('core.Classroom', on_delete=models.CASCADE)
    timeslot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE)
    section = models.ForeignKey('core.Section', on_delete=models.CASCADE)

    def __str__(self):
        return f"Fixed: {self.subject.code} at {self.timeslot}"

class ConstraintRule(models.Model):
    # Requirement G: Real-time validation warnings and enforcement
    RULE_TYPES = [
        ('faculty_clash', 'No Faculty Overlap'),
        ('room_clash', 'No Room Overlap'),
        ('capacity_check', 'Room Capacity vs Student Count'),
        ('lab_timing', 'Lab Timing Constraint'),
    ]
    
    rule_type = models.CharField(max_length=50, choices=RULE_TYPES)
    is_mandatory = models.BooleanField(default=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.get_rule_type_display()