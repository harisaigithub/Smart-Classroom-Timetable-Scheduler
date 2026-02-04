from django.db import models

class TimetableEntry(models.Model):
    # Requirement H: Core data for the grid view
    day = models.CharField(max_length=10)
    timeslot = models.ForeignKey('scheduler.TimeSlot', on_delete=models.CASCADE)
    subject = models.ForeignKey('core.Subject', on_delete=models.CASCADE)
    classroom = models.ForeignKey('core.Classroom', on_delete=models.CASCADE)
    section = models.ForeignKey('core.Section', on_delete=models.CASCADE)
    faculty = models.ForeignKey('faculty.Faculty', on_delete=models.SET_NULL, null=True)
    is_fixed = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Timetable Entries"

    def __str__(self):
        return f"{self.day} - {self.subject.code} for {self.section.name}"