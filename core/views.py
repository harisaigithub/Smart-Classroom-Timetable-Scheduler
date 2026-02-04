from django.shortcuts import render, redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from .models import Department, Classroom, Subject, Feedback
from django.shortcuts import get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from .models import Feedback

# --- Department Views ---
class DepartmentListView(LoginRequiredMixin, ListView):
    model = Department
    template_name = 'core/department_list.html'
    context_object_name = 'departments'

class DepartmentCreateView(LoginRequiredMixin, CreateView):
    model = Department
    fields = ['name', 'code']
    template_name = 'core/department_form.html'
    success_url = reverse_lazy('department_list')

class DepartmentUpdateView(LoginRequiredMixin, UpdateView):
    model = Department
    fields = ['name', 'code']
    template_name = 'core/department_form.html'
    success_url = reverse_lazy('department_list')

class DepartmentDeleteView(LoginRequiredMixin, DeleteView):
    model = Department
    template_name = 'core/department_confirm_delete.html'
    success_url = reverse_lazy('department_list')

# --- Classroom Views ---
class ClassroomListView(LoginRequiredMixin, ListView):
    model = Classroom
    template_name = 'core/classroom_list.html'
    context_object_name = 'classrooms'

class ClassroomCreateView(LoginRequiredMixin, CreateView):
    model = Classroom
    fields = ['name', 'capacity', 'room_type', 'is_available']
    template_name = 'core/classroom_form.html'
    success_url = reverse_lazy('classroom_list')

class ClassroomUpdateView(LoginRequiredMixin, UpdateView):
    model = Classroom
    fields = ['name', 'capacity', 'room_type', 'is_available']
    template_name = 'core/classroom_form.html'
    success_url = reverse_lazy('classroom_list')

class ClassroomDeleteView(LoginRequiredMixin, DeleteView):
    model = Classroom
    template_name = 'core/classroom_confirm_delete.html'
    success_url = reverse_lazy('classroom_list')

# --- Subject Views ---
class SubjectListView(LoginRequiredMixin, ListView):
    model = Subject
    template_name = 'core/subject_list.html'
    context_object_name = 'subjects'

class SubjectCreateView(LoginRequiredMixin, CreateView):
    model = Subject
    fields = ['name', 'code', 'department', 'semester', 'subject_type', 'credit_hours', 'classes_per_week']
    template_name = 'core/subject_form.html'
    success_url = reverse_lazy('subject_list')

# Recommended: Add SubjectUpdateView here if you want to edit subjects later

# --- Feedback Views ---
class FeedbackCreateView(LoginRequiredMixin, CreateView):
    model = Feedback
    fields = ['subject', 'message']
    template_name = 'feedback/feedback_form.html'
    success_url = reverse_lazy('user_dashboard')

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, "Your feedback has been submitted successfully.")
        return super().form_valid(form)

class AdminFeedbackListView(LoginRequiredMixin, ListView):
    model = Feedback
    template_name = 'feedback/admin_feedback_list.html'
    context_object_name = 'feedbacks'
    
    def get_queryset(self):
        # Latest feedback appears first
        return Feedback.objects.all().order_by('-created_at')
    
@staff_member_required
def resolve_feedback(request, pk):
    feedback = get_object_or_404(Feedback, pk=pk)
    feedback.status = 'resolved'
    feedback.save()
    messages.success(request, f"Feedback from {feedback.user.email} marked as resolved.")
    return redirect('admin_feedback_list')

class SubjectUpdateView(LoginRequiredMixin, UpdateView):
    model = Subject
    fields = ['name', 'code', 'department', 'semester', 'subject_type', 'credit_hours', 'classes_per_week']
    template_name = 'core/subject_form.html'
    success_url = reverse_lazy('subject_list')

class SubjectDeleteView(LoginRequiredMixin, DeleteView):
    model = Subject
    template_name = 'core/subject_confirm_delete.html'
    success_url = reverse_lazy('subject_list')