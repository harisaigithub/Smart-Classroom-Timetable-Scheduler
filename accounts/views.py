from django.contrib.auth import authenticate, login, logout, get_user_model
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db.models import Count
import random

# Model Imports
from .models import EmailOTP
from core.models import Department, Classroom, Section
from timetable.models import TimetableEntry
from faculty.models import Faculty
from scheduler.models import TimeSlot

User = get_user_model()

# --- Authentication Views ---

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('username')  # Frontend uses 'username' label
        password = request.POST.get('password')

        user = authenticate(request, email=email, password=password)

        if user:
            if not user.is_active:
                messages.error(request, 'Please verify your email first.')
                return render(request, 'accounts/login.html')

            login(request, user)
            user.login_count += 1
            user.save()
            
            if user.role == 'admin':
                return redirect('admin_dashboard')
            return redirect('user_dashboard')
        else:
            messages.error(request, 'Invalid email or password.')

    return render(request, 'accounts/login.html')

def signup_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role')

        if User.objects.filter(email=email).exists():
            messages.info(request, 'User already exists. Please login.')
            return redirect('login')

        user = User.objects.create_user(
            email=email,
            password=password,
            role=role,
            is_active=False
        )

        otp = str(random.randint(100000, 999999))
        EmailOTP.objects.update_or_create(user=user, defaults={'otp': otp})

        try:
            send_mail(
                'Verify your Smart Scheduler account',
                f'Your OTP verification code is: {otp}. It expires in 10 minutes.',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )
            request.session['verify_user'] = user.id
            return redirect('verify_otp')
        except Exception as e:
            messages.error(request, 'Error sending email. Please check SMTP settings.')
            return redirect('signup')

    return render(request, 'accounts/signup.html')

def verify_otp_view(request):
    user_id = request.session.get('verify_user')
    if not user_id:
        return redirect('signup')

    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        otp_obj = EmailOTP.objects.filter(user=user).first()

        if otp_obj and not otp_obj.is_expired() and entered_otp == otp_obj.otp:
            user.is_active = True
            user.is_verified = True
            user.save()
            otp_obj.delete()
            del request.session['verify_user']
            return render(request, 'accounts/verify_success.html')

        messages.error(request, 'Invalid or expired OTP.')

    return render(request, 'accounts/verify_otp.html')

def logout_view(request):
    logout(request)
    return redirect('login')

# --- Dashboard Views ---

@login_required
def admin_dashboard(request):
    if request.user.role != 'admin':
        return redirect('user_dashboard')

    # 1. Basic Counts
    total_depts = Department.objects.count()
    total_rooms = Classroom.objects.count()
    total_faculty = Faculty.objects.count()
    total_sections = Section.objects.count()

    # 2. Aggregating data for Charts (Classes per Department)
    dept_names = list(Department.objects.values_list('code', flat=True))
    dept_class_counts = []
    for dept_code in dept_names:
        count = TimetableEntry.objects.filter(subject__department__code=dept_code).count()
        dept_class_counts.append(count)

    # 3. Room Utilization Logic (For the Circular Ring)
    # total slots = (Active TimeSlots - Breaks) * (Available Classrooms)
    active_timeslots = TimeSlot.objects.filter(is_break=False).count()
    available_rooms = Classroom.objects.filter(is_available=True).count()
    
    total_possible_slots = active_timeslots * available_rooms
    actual_filled_slots = TimetableEntry.objects.count()
    
    utilization_rate = 0
    utilization_offset = 502.4  # Default: Full circle hidden (2 * PI * r=80)
    
    if total_possible_slots > 0:
        utilization_rate = round((actual_filled_slots / total_possible_slots) * 100)
        # Calculate SVG dash offset: 502.4 is 100%. 
        # We subtract the percentage portion to "show" the colored stroke.
        utilization_offset = 502.4 - (502.4 * (utilization_rate / 100))

    context = {
        'total_departments': total_depts,
        'total_rooms': total_rooms,
        'total_faculty': total_faculty,
        'total_sections': total_sections,
        'utilization_rate': utilization_rate,
        'utilization_offset': utilization_offset,
        'dept_names': dept_names,
        'dept_counts': dept_class_counts,
        'recent_activities': TimetableEntry.objects.order_by('-id')[:5],
        'recent_departments': Department.objects.all().order_by('-created_at')[:5],
    }
    return render(request, 'accounts/admin_dashboard.html', context)

@login_required
def user_dashboard(request):
    # Placeholder for faculty-specific view
    return render(request, 'accounts/user_dashboard.html')