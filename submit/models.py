from django.db import models
from django.contrib.auth import get_user_model
from problems.models import Problem, TestCase

User = get_user_model()

class Submission(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('JUDGING', 'Judging'),
        ('ACCEPTED', 'Accepted'),
        ('WRONG_ANSWER', 'Wrong Answer'),
        ('TIME_LIMIT_EXCEEDED', 'Time Limit Exceeded'),
        ('MEMORY_LIMIT_EXCEEDED', 'Memory Limit Exceeded'),
        ('RUNTIME_ERROR', 'Runtime Error'),
        ('COMPILATION_ERROR', 'Compilation Error'),
        ('ERROR', 'System Error'),
    ]
    
    LANGUAGE_CHOICES = [
        ('cpp', 'C++'),
        ('py', 'Python'),
        ('java', 'Java'),
    ]
    
    # Relations
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    
    # Submission data
    code = models.TextField()
    language = models.CharField(max_length=50, choices=LANGUAGE_CHOICES)
    input_data = models.TextField(blank=True, null=True)
    
    # Enhanced results
    total_test_cases = models.IntegerField(default=0)
    passed_test_cases = models.IntegerField(default=0)
    score = models.FloatField(default=0.0, help_text="Score based on passed test cases")
    max_execution_time = models.FloatField(null=True, blank=True)
    max_memory_used = models.BigIntegerField(null=True, blank=True, help_text="Memory in bytes")
    
    output_data = models.TextField(blank=True, null=True)
    error_data = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='PENDING')
    
    # Timing
    execution_time = models.FloatField(null=True, blank=True, help_text="Execution time in seconds")
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-submitted_at']

    def __str__(self):
        user_display = self.user.username if self.user else "Anonymous"
        return f"{user_display} - {self.problem.title} - {self.status}"

class TestCaseResult(models.Model):
    """Results for individual test cases"""
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE, related_name='test_results')
    test_case = models.ForeignKey(TestCase, on_delete=models.CASCADE)
    status = models.CharField(max_length=50, choices=Submission.STATUS_CHOICES)
    execution_time = models.FloatField(null=True, blank=True)
    memory_used = models.BigIntegerField(null=True, blank=True)
    actual_output = models.TextField(blank=True)
    error_message = models.TextField(blank=True)
    
    class Meta:
        unique_together = ['submission', 'test_case']
        
    def __str__(self):
        return f"{self.submission} - {self.test_case} - {self.status}"