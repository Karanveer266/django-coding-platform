from django.db import models
from django.contrib.auth import get_user_model
from problems.models import Problem

User = get_user_model()

class LearningSession(models.Model):
    """Tracks a user's learning session for a specific problem"""
    
    STATUS_CHOICES = [
        ('started', 'Started'),
        ('mcq_generation', 'Generating MCQs'),
        ('mcq_ready', 'MCQs Ready'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    mcq_set = models.ForeignKey('mcq_generation.MCQSet', on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='started')
    
    # MCQ tracking
    current_mcq_index = models.PositiveIntegerField(default=0)
    total_mcqs = models.PositiveIntegerField(default=0)
    correct_answers = models.PositiveIntegerField(default=0)
    
    # Timestamps
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.problem.title} - {self.status}"
    
    @property
    def accuracy(self):
        if self.total_mcqs == 0:
            return 0
        return (self.correct_answers / self.total_mcqs) * 100
    
    @property
    def is_completed(self):
        return self.status == 'completed'
    
    class Meta:
        ordering = ['-started_at']
        unique_together = ['user', 'problem']  # One session per user per problem