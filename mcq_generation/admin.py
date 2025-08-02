from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count, Avg
from .models import MCQSet, MCQ, MCQResponse

class MCQInline(admin.TabularInline):
    model = MCQ
    extra = 0
    fields = ['sequence_order', 'question_text', 'correct_answer', 'difficulty_level']
    readonly_fields = ['sequence_order']

@admin.register(MCQSet)
class MCQSetAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'problem', 'total_questions', 'is_active', 
        'generated_at', 'usage_count', 'view_problem_link'
    ]
    list_filter = [
        'is_active', 'generated_at', 'problem__difficulty', 
        'problem__problem_type'
    ]
    search_fields = ['problem__title', 'id']
    readonly_fields = ['generated_at', 'usage_count', 'view_problem_link']
    inlines = [MCQInline]
    date_hierarchy = 'generated_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('problem', 'total_questions', 'is_active')
        }),
        ('Details', {
            'fields': ('generated_at', 'usage_count', 'view_problem_link')
        }),
    )
    
    def usage_count(self, obj):
        from learning_sessions.models import LearningSession
        count = LearningSession.objects.filter(mcq_set=obj).count()
        return format_html('<span style="font-weight: bold;">{}</span>', count)
    usage_count.short_description = "Sessions"
    
    def view_problem_link(self, obj):
        if obj.problem:
            url = reverse('problems:detail', args=[obj.problem.id])
            return format_html('<a href="{}" target="_blank">View Problem</a>', url)
        return "N/A"
    view_problem_link.short_description = "Problem"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('problem')

@admin.register(MCQ)
class MCQAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'mcq_set_problem', 'sequence_order', 'question_preview', 
        'correct_answer', 'difficulty_level', 'response_count'
    ]
    list_filter = [
        'difficulty_level', 'correct_answer', 'mcq_set__problem__difficulty'
    ]
    search_fields = [
        'question_text', 'mcq_set__problem__title', 'explanation'
    ]
    readonly_fields = ['response_count', 'accuracy_rate']
    
    fieldsets = (
        ('Question Information', {
            'fields': ('mcq_set', 'sequence_order', 'difficulty_level')
        }),
        ('Question Content', {
            'fields': ('question_text', 'hint_text')
        }),
        ('Answer Options', {
            'fields': ('option_a', 'option_b', 'option_c', 'option_d', 'correct_answer')
        }),
        ('Explanation', {
            'fields': ('explanation',)
        }),
        ('Statistics', {
            'fields': ('response_count', 'accuracy_rate')
        }),
    )
    
    def mcq_set_problem(self, obj):
        return f"{obj.mcq_set.problem.title}"
    mcq_set_problem.short_description = "Problem"
    
    def question_preview(self, obj):
        return obj.question_text[:50] + "..." if len(obj.question_text) > 50 else obj.question_text
    question_preview.short_description = "Question"
    
    def response_count(self, obj):
        count = MCQResponse.objects.filter(mcq=obj).count()
        return format_html('<span style="font-weight: bold;">{}</span>', count)
    response_count.short_description = "Responses"
    
    def accuracy_rate(self, obj):
        responses = MCQResponse.objects.filter(mcq=obj)
        total = responses.count()
        if total == 0:
            return "No responses"
        
        correct = responses.filter(is_correct=True).count()
        rate = (correct / total) * 100
        color = 'green' if rate >= 70 else 'orange' if rate >= 50 else 'red'
        
        return format_html(
            '<span style="color: {};">{:.1f}% ({}/{})</span>',
            color, rate, correct, total
        )
    accuracy_rate.short_description = "Accuracy"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('mcq_set__problem')

@admin.register(MCQResponse)
class MCQResponseAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'user', 'mcq_problem', 'mcq_question_preview', 
        'selected_answer', 'correct_answer', 'is_correct', 
        'time_taken_seconds', 'attempted_at'
    ]
    list_filter = [
        'is_correct', 'attempted_at', 'selected_answer', 
        'mcq__difficulty_level', 'learning_session__status'
    ]
    search_fields = [
        'user__username', 'mcq__mcq_set__problem__title', 
        'mcq__question_text'
    ]
    readonly_fields = ['attempted_at', 'correct_answer', 'mcq_question_preview']
    date_hierarchy = 'attempted_at'
    
    fieldsets = (
        ('Response Information', {
            'fields': ('user', 'mcq', 'learning_session')
        }),
        ('Answer Details', {
            'fields': (
                'selected_answer', 'correct_answer', 'is_correct', 
                'time_taken_seconds'
            )
        }),
        ('Additional Info', {
            'fields': ('attempted_at', 'mcq_question_preview')
        }),
    )
    
    def mcq_problem(self, obj):
        return obj.mcq.mcq_set.problem.title
    mcq_problem.short_description = "Problem"
    
    def mcq_question_preview(self, obj):
        return obj.mcq.question_text[:100] + "..." if len(obj.mcq.question_text) > 100 else obj.mcq.question_text
    mcq_question_preview.short_description = "Question"
    
    def correct_answer(self, obj):
        return obj.mcq.correct_answer
    correct_answer.short_description = "Correct"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'user', 'mcq__mcq_set__problem', 'learning_session'
        )