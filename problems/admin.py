from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count
from .models import Problem, TestCase

class TestCaseInline(admin.TabularInline):
    model = TestCase
    extra = 1
    fields = ['is_sample', 'is_hidden', 'points', 'input_data', 'expected_output']

@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'problem_type', 'difficulty', 'is_active', 
        'success_rate', 'test_case_count', 'created_at', 'view_problem_link'
    ]
    list_filter = [
        'problem_type', 'difficulty', 'is_active', 'created_at', 'created_by'
    ]
    search_fields = ['title', 'description']
    readonly_fields = [
        'created_at', 'updated_at', 'total_attempts', 'successful_completions',
        'success_rate', 'view_problem_link', 'problem_summary'
    ]
    date_hierarchy = 'created_at'
    inlines = [TestCaseInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'problem_type', 'difficulty', 'is_active')
        }),
        ('Content Details', {
            'fields': ('input_format', 'output_format', 'constraints')
        }),
        ('Sample Data', {
            'fields': ('sample_input', 'sample_output'),
            'classes': ('collapse',)
        }),
        ('Files & Media', {
            'fields': ('image_file', 'pdf_file'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at')
        }),
        ('Statistics', {
            'fields': ('total_attempts', 'successful_completions', 'success_rate')
        }),
        ('Actions & Summary', {
            'fields': ('view_problem_link', 'problem_summary')
        }),
    )
    
    
    def success_rate(self, obj):
        if obj.total_attempts > 0:
            rate = (obj.successful_completions / obj.total_attempts) * 100
            color = 'green' if rate >= 50 else 'orange' if rate >= 25 else 'red'
            return format_html(
                '<span style="color: {};">{:.1f}%</span>',
                color, rate
            )
        return "0%"
    success_rate.short_description = "Success Rate"
    
    def test_case_count(self, obj):
        count = TestCase.objects.filter(problem=obj).count()
        return format_html('<span style="font-weight: bold;">{}</span>', count)
    test_case_count.short_description = "Test Cases"
    
    def view_problem_link(self, obj):
        if obj.pk:
            url = reverse('problems:detail', args=[obj.pk])
            return format_html('<a href="{}" target="_blank">View Problem</a>', url)
        return "N/A"
    view_problem_link.short_description = "View"
    
    def problem_summary(self, obj):
        if obj.pk:
            difficulty_color = {
                'easy': 'green',
                'medium': 'orange',
                'hard': 'red'
            }.get(obj.difficulty, 'gray')
            
            test_cases = TestCase.objects.filter(problem=obj)
            sample_count = test_cases.filter(is_sample=True).count()
            hidden_count = test_cases.filter(is_hidden=True).count()
            
            return format_html(
                '<div style="line-height: 1.4;">'
                '<span style="color: {};">● {}</span><br>'
                '<strong>Attempts:</strong> {} | <strong>Solved:</strong> {}<br>'
                '<strong>Test Cases:</strong> {} (Sample: {}, Hidden: {})<br>'
                '{}'
                '</div>',
                difficulty_color, obj.get_difficulty_display().upper(),
                obj.total_attempts, obj.successful_completions,
                test_cases.count(), sample_count, hidden_count,
                '<span style="color: red;">INACTIVE</span>' if not obj.is_active else ''
            )
        return "N/A"
    problem_summary.short_description = "Summary"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('created_by')
    
    actions = ['activate_problems', 'deactivate_problems', 'reset_statistics']
    
    def activate_problems(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} problems were activated.')
    activate_problems.short_description = "Activate selected problems"
    
    def deactivate_problems(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} problems were deactivated.')
    deactivate_problems.short_description = "Deactivate selected problems"
    
    def reset_statistics(self, request, queryset):
        updated = queryset.update(total_attempts=0, successful_completions=0)
        self.message_user(request, f'Statistics reset for {updated} problems.')
    reset_statistics.short_description = "Reset statistics for selected problems"

@admin.register(TestCase)
class TestCaseAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'problem_title', 'is_sample', 'is_hidden', 
        'points', 'input_preview', 'output_preview'
    ]
    list_filter = [
        'is_sample', 'is_hidden', 'problem__difficulty', 'problem__problem_type'
    ]
    search_fields = ['problem__title', 'input_data', 'expected_output']
    readonly_fields = ['input_preview', 'output_preview']
    
    fieldsets = (
        ('Test Case Information', {
            'fields': ('problem', 'is_sample', 'is_hidden', 'points')
        }),
        ('Test Data', {
            'fields': ('input_data', 'expected_output')
        }),
        ('Preview', {
            'fields': ('input_preview', 'output_preview'),
            'classes': ('collapse',)
        }),
    )
    
    def problem_title(self, obj):
        return obj.problem.title
    problem_title.short_description = "Problem"
    
    def input_preview(self, obj):
        preview = obj.input_data[:200] + "..." if len(obj.input_data) > 200 else obj.input_data
        return format_html('<pre style="white-space: pre-wrap;">{}</pre>', preview)
    input_preview.short_description = "Input Preview"
    
    def output_preview(self, obj):
        preview = obj.expected_output[:200] + "..." if len(obj.expected_output) > 200 else obj.expected_output
        return format_html('<pre style="white-space: pre-wrap;">{}</pre>', preview)
    output_preview.short_description = "Output Preview"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('problem')