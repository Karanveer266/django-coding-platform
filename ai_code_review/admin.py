from django.contrib import admin
from .models import CodeReview

@admin.register(CodeReview)
class CodeReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'language', 'created_at']
    list_filter = ['language', 'created_at']
    search_fields = ['user__username', 'code', 'question']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
