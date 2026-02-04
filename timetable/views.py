from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.db import transaction

# Model Imports
from core.models import Section, Subject, Classroom
from scheduler.models import TimeSlot
from faculty.models import Faculty
from notifications.models import Notification
from .models import TimetableEntry

# PDF Generation
from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet


# ----------------------------------------------------------
# GENERATE TIMETABLE
# ----------------------------------------------------------

@login_required
def generate_timetable(request):
    if request.user.role != 'admin':
        return redirect('user_dashboard')

    if request.method == 'POST':
        with transaction.atomic():

            TimetableEntry.objects.all().delete()

            sections = Section.objects.all()
            classrooms = list(Classroom.objects.filter(is_available=True))
            faculty_members = list(Faculty.objects.all())

            days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']

            for section in sections:

                subjects = list(
                    Subject.objects.filter(
                        semester=section.semester,
                        department=section.department
                    )
                )

                # Track subject weekly usage
                subject_usage = {s.id: 0 for s in subjects}

                for day in days:

                    previous_subject = None

                    slots = TimeSlot.objects.filter(
                        day=day,
                        is_break=False
                    ).order_by('start_time')

                    for slot in slots:

                        assigned = False

                        # Try subjects in rotation
                        for subject in subjects:

                            # Avoid consecutive same subject
                            if previous_subject == subject.id:
                                continue

                            # Respect weekly count but allow reuse if necessary
                            if subject_usage[subject.id] >= subject.classes_per_week:
                                continue

                            # Room allocation
                            room = None
                            for r in classrooms:
                                if subject.code.endswith("L"):
                                    if "Lab" not in r.name:
                                        continue
                                if r.capacity >= section.student_count:
                                    if not TimetableEntry.objects.filter(
                                        classroom=r,
                                        day=day,
                                        timeslot=slot
                                    ).exists():
                                        room = r
                                        break

                            if not room:
                                continue

                            # Faculty allocation
                            faculty_member = None
                            for f in faculty_members:
                                if f.department != subject.department:
                                    continue
                                if not TimetableEntry.objects.filter(
                                    faculty=f,
                                    day=day,
                                    timeslot=slot
                                ).exists():
                                    faculty_member = f
                                    break

                            if not faculty_member:
                                continue

                            # Create entry
                            TimetableEntry.objects.create(
                                subject=subject,
                                section=section,
                                classroom=room,
                                faculty=faculty_member,
                                timeslot=slot,
                                day=day
                            )

                            subject_usage[subject.id] += 1
                            previous_subject = subject.id
                            assigned = True
                            break

                        # If no subject fits (all exhausted), rotate again ignoring weekly limit
                        if not assigned:
                            for subject in subjects:

                                if previous_subject == subject.id:
                                    continue

                                room = classrooms[0]
                                faculty_member = faculty_members[0]

                                TimetableEntry.objects.create(
                                    subject=subject,
                                    section=section,
                                    classroom=room,
                                    faculty=faculty_member,
                                    timeslot=slot,
                                    day=day
                                )

                                previous_subject = subject.id
                                assigned = True
                                break

            # FINAL VALIDATION
            total_required_slots = TimeSlot.objects.filter(is_break=False).count() * sections.count()
            total_created = TimetableEntry.objects.count()

            if total_created >= total_required_slots:
                messages.success(request, "Complete Full-Week Timetable Generated Successfully.")
            else:
                messages.warning(request, "Timetable generated but some slots could not be filled.")

        return redirect('timetable_view')

    return render(request, 'timetable/generate_confirm.html')

# ----------------------------------------------------------
# GRID VIEW
# ----------------------------------------------------------

@login_required
def timetable_grid_view(request):

    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']

    # Unique rows based ONLY on start_time
    unique_timeslots = (
        TimeSlot.objects
        .order_by('start_time')
        .values('start_time', 'end_time', 'is_break', 'break_name')
        .distinct()
    )

    section_id = request.GET.get('section')

    if section_id:
        entries = TimetableEntry.objects.filter(section_id=section_id)
    else:
        entries = TimetableEntry.objects.all()

    grid = {day: {} for day in days}

    for entry in entries:
        key = entry.timeslot.start_time.strftime('%H:%M')
        grid[entry.day][key] = entry

    return render(request, 'timetable/timetable_view.html', {
        'days': days,
        'timeslots': unique_timeslots,
        'grid': grid,
        'sections': Section.objects.all(),
        'selected_section': section_id
    })


# ----------------------------------------------------------
# EXPORT PDF
# ----------------------------------------------------------

def export_timetable_pdf(request, section_id):

    section = get_object_or_404(Section, id=section_id)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Timetable_{section.name}.pdf"'

    doc = SimpleDocTemplate(response, pagesize=landscape(A4))
    elements = []
    styles = getSampleStyleSheet()

    elements.append(
        Paragraph(
            f"Official Timetable - Section {section.name} ({section.department.code})",
            styles['Title']
        )
    )

    data = [['Time', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']]

    times = (
        TimeSlot.objects
        .order_by('start_time')
        .values('start_time', 'end_time', 'is_break', 'break_name')
        .distinct()
    )

    for t in times:

        time_str = t['start_time'].strftime('%H:%M')
        row = [time_str]

        for d in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']:

            if t['is_break']:
                row.append(t['break_name'] or "BREAK")
            else:
                entry = TimetableEntry.objects.filter(
                    section=section,
                    day=d,
                    timeslot__start_time=t['start_time']
                ).first()

                if entry:
                    row.append(f"{entry.subject.code}\n{entry.classroom.name}")
                else:
                    row.append("-")

        data.append(row)

    table = Table(data, hAlign='CENTER')
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E3A8A')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTSIZE', (0, 0), (-1, -1), 7),
    ]))

    elements.append(table)
    doc.build(elements)

    return response


# ----------------------------------------------------------
# PUBLISH TIMETABLE
# ----------------------------------------------------------

@login_required
def publish_timetable(request):

    if request.method == 'POST':

        entries = TimetableEntry.objects.all()

        faculty_users = (
            Faculty.objects
            .filter(timetableentry__in=entries)
            .values_list('user', flat=True)
            .distinct()
        )

        for user_id in faculty_users:
            Notification.objects.create(
                user_id=user_id,
                title="Timetable Published",
                message="The final academic schedule is now live."
            )

        messages.success(request, "Timetable published successfully.")

    return redirect('timetable_view')


def public_timetable_view(request):
    """A public, read-only view of the schedule for students/guests."""
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    unique_timeslots = TimeSlot.objects.values('start_time', 'end_time', 'is_break', 'break_name').distinct().order_by('start_time')
    
    section_id = request.GET.get('section')
    sections = Section.objects.all()
    
    grid = {day: {} for day in days}
    if section_id:
        entries_qs = TimetableEntry.objects.filter(section_id=section_id)
        for entry in entries_qs:
            time_key = entry.timeslot.start_time.strftime('%H:%M')
            grid[entry.day][time_key] = entry

    return render(request, 'timetable/public_view.html', {
        'days': days,
        'timeslots': unique_timeslots,
        'grid': grid,
        'sections': sections,
        'selected_section': section_id
    })