from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import LearningSession

@admin.register(LearningSession)
class LearningSessionAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'user', 'problem', 'status', 'accuracy', 
        'progress', 'started_at', 'completed_at', 'view_session_link'
    ]
    list_filter = [
        'status', 'started_at', 'completed_at', 
        'problem__difficulty', 'problem__problem_type'
    ]
    search_fields = ['user__username', 'problem__title', 'id']
    readonly_fields = [
        'started_at', 'completed_at', 'accuracy', 
        'progress', 'view_session_link', 'session_summary'
    ]
    date_hierarchy = 'started_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'problem', 'status')
        }),
        ('MCQ Information', {
            'fields': ('mcq_set', 'current_mcq_index', 'total_mcqs')
        }),
        ('Progress & Performance', {
            'fields': ('correct_answers', 'accuracy', 'progress')
        }),
        ('Timestamps', {
            'fields': ('started_at', 'completed_at')
        }),
        ('Actions & Summary', {
            'fields': ('view_session_link', 'session_summary')
        }),
    )
    
    def accuracy(self, obj):
        if obj.total_mcqs > 0:
            accuracy = (obj.correct_answers / obj.total_mcqs) * 100
            color = 'green' if accuracy >= 80 else 'orange' if accuracy >= 60 else 'red'
            return format_html(
                '<span style="color: {};">{:.1f}%</span>',
                color, accuracy
            )
        return "0%"
    accuracy.short_description = "Accuracy"
    
    def progress(self, obj):
        if obj.total_mcqs > 0:
            progress = (obj.current_mcq_index / obj.total_mcqs) * 100
            return format_html('{:.1f}%', progress)
        return "0%"
    progress.short_description = "Progress"
    
    def view_session_link(self, obj):
        if obj.pk:
            if obj.status == 'completed':
                url = reverse('learning_sessions:session_results', args=[obj.pk])
                return format_html('<a href="{}" target="_blank">View Results</a>', url)
            else:
                url = reverse('learning_sessions:session_detail', args=[obj.pk])
                return format_html('<a href="{}" target="_blank">View Session</a>', url)
        return "N/A"
    view_session_link.short_description = "View"
    
    def session_summary(self, obj):
        if obj.pk:
            status_color = {
                'started': 'blue',
                'mcq_generation': 'orange',
                'mcq_ready': 'green',
                'in_progress': 'purple',
                'completed': 'green',
                'failed': 'red'
            }.get(obj.status, 'gray')
            
            return format_html(
                '<div>'
                '<span style="color: {};">Status: {}</span><br>'
                'Questions: {}/{}<br>'
                'Correct: {}<br>'
                '</div>',
                status_color, obj.get_status_display(),
                obj.current_mcq_index, obj.total_mcqs,
                obj.correct_answers
            )
        return "N/A"
    session_summary.short_description = "Summary"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'problem', 'mcq_set')