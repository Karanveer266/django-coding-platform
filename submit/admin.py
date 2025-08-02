from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count, Avg
from .models import Submission, TestCaseResult

@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'user', 'problem', 'language', 'status', 
        'score', 'execution_time', 'submitted_at', 'view_details_link'
    ]
    list_filter = [
        'status', 'language', 'submitted_at', 
        'problem__difficulty', 'problem__problem_type'
    ]
    search_fields = ['user__username', 'problem__title', 'id']
    readonly_fields = [
        'submitted_at', 'max_execution_time', 'score', 
        'view_details_link', 'test_results_summary'
    ]
    date_hierarchy = 'submitted_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'problem', 'language', 'status')
        }),
        ('Code & Input', {
            'fields': ('code', 'input_data'),
            'classes': ('collapse',)
        }),
        ('Results', {
            'fields': (
                'total_test_cases', 'passed_test_cases', 'score',
                'max_execution_time', 'max_memory_used'
            )
        }),
        ('Output & Errors', {
            'fields': ('output_data', 'error_data'),
            'classes': ('collapse',)
        }),
        ('Details', {
            'fields': ('submitted_at', 'view_details_link', 'test_results_summary')
        }),
    )
    
    def view_details_link(self, obj):
        if obj.pk:
            url = reverse('submit:submission_detail', args=[obj.pk])
            return format_html('<a href="{}" target="_blank">View Details</a>', url)
        return "N/A"
    view_details_link.short_description = "Details"
    
    def test_results_summary(self, obj):
        if obj.pk:
            results = TestCaseResult.objects.filter(submission=obj)
            total = results.count()
            if total == 0:
                return "No test results"
            
            passed = results.filter(status='ACCEPTED').count()
            failed = total - passed
            
            return format_html(
                '<span style="color: green;">✓ {}</span> | '
                '<span style="color: red;">✗ {}</span>',
                passed, failed
            )
        return "N/A"
    test_results_summary.short_description = "Test Results"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'problem')

@admin.register(TestCaseResult)
class TestCaseResultAdmin(admin.ModelAdmin):
    list_display = [
        'submission_id', 'test_case', 'status', 
        'execution_time', 'memory_used', 'submission_user'
    ]
    list_filter = ['status', 'test_case__is_sample', 'test_case__is_hidden']
    search_fields = [
        'submission__id', 'submission__user__username', 
        'test_case__problem__title'
    ]
    readonly_fields = ['submission_user', 'test_case_details']
    
    def submission_user(self, obj):
        return obj.submission.user.username
    submission_user.short_description = "User"
    
    def test_case_details(self, obj):
        if obj.test_case:
            return format_html(
                'Sample: {} | Hidden: {} | Points: {}',
                "✓" if obj.test_case.is_sample else "✗",
                "✓" if obj.test_case.is_hidden else "✗",
                obj.test_case.points
            )
        return "N/A"
    test_case_details.short_description = "Test Case Info"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'submission__user', 'test_case__problem'
        )