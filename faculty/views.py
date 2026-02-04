from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import datetime

# Model Imports
from .models import Faculty, FacultyAvailability
from accounts.models import User
from timetable.models import TimetableEntry
from scheduler.models import TimeSlot

class FacultyListView(LoginRequiredMixin, ListView):
    model = Faculty
    template_name = 'faculty/faculty_list.html'
    context_object_name = 'faculties'

class FacultyCreateView(LoginRequiredMixin, CreateView):
    model = Faculty
    fields = ['user', 'department', 'designation', 'employee_id', 'max_classes_per_day', 'max_classes_per_week']
    template_name = 'faculty/faculty_form.html'
    success_url = reverse_lazy('faculty_list')

@login_required
def faculty_dashboard(request):
    """Personalized dashboard for faculty members."""
    faculty_profile = Faculty.objects.filter(user=request.user).first()
    
    if not faculty_profile:
        # Redirect with a message instead of crashing
        messages.warning(request, "Faculty profile not found. Please contact Admin.")
        return render(request, 'faculty/faculty_dashboard.html', {'faculty': None})
    
    # 1. Fetch personal timetable entries
    my_classes = TimetableEntry.objects.filter(faculty=faculty_profile).select_related('subject', 'classroom', 'timeslot')
    
    # 2. Calculate Workload Stats
    limit = faculty_profile.max_classes_per_week or 20
    current_load = my_classes.count()
    workload_percent = round((current_load / limit) * 100) if limit > 0 else 0
    workload_offset = 502.4 - (502.4 * (min(workload_percent, 100) / 100))

    # 3. Organize "Today's Schedule"
    day_name = datetime.datetime.now().strftime('%A').lower()
    today_classes = my_classes.filter(day=day_name).order_by('timeslot__start_time')

    context = {
        'faculty': faculty_profile,
        'my_classes': my_classes,
        'today_classes': today_classes,
        'workload_percent': workload_percent,
        'workload_offset': workload_offset,
        'total_subjects': my_classes.values('subject').distinct().count(),
    }
    return render(request, 'faculty/faculty_dashboard.html', context)

@login_required
def availability_matrix(request):
    """Allows faculty to mark their 'Busy' periods for the scheduler."""
    faculty_profile = Faculty.objects.filter(user=request.user).first()
    
    if not faculty_profile:
        messages.error(request, "You must have an active Faculty profile to set availability.")
        return redirect('user_dashboard')

    days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']
    # Distinct periods for the row headers
    timeslots = TimeSlot.objects.values('start_time', 'end_time').distinct().order_by('start_time')

    if request.method == 'POST':
        # Clear existing unavailabilities to refresh
        FacultyAvailability.objects.filter(faculty=faculty_profile).delete()
        
        for day in days:
            for slot in timeslots:
                # Keys match the template: busy_monday_08:20
                key = f"busy_{day}_{slot['start_time'].strftime('%H:%M')}"
                if request.POST.get(key):
                    FacultyAvailability.objects.create(
                        faculty=faculty_profile,
                        day=day,
                        start_time=slot['start_time'],
                        is_available=False
                    )
        messages.success(request, "Your teaching preferences have been updated.")
        return redirect('user_dashboard')

    # Fetch current "Busy" list to pre-check checkboxes
    busy_slots = FacultyAvailability.objects.filter(faculty=faculty_profile).values_list('day', 'start_time')
    busy_list = [f"{b[0]}_{b[1].strftime('%H:%M')}" for b in busy_slots]

    return render(request, 'faculty/availability_matrix.html', {
        'days': days,
        'timeslots': timeslots,
        'busy_list': busy_list
    })