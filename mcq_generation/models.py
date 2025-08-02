from django.db import models
from django.contrib.auth import get_user_model
from problems.models import Problem

User = get_user_model()

class MCQSet(models.Model):
    """Represents a set of MCQs generated for a specific problem"""
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    generated_at = models.DateTimeField(auto_now_add=True)
    total_questions = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-generated_at']
    
    def __str__(self):
        return f"MCQ Set for {self.problem.title}"

class MCQ(models.Model):
    """Individual Multiple Choice Question"""
    mcq_set = models.ForeignKey(MCQSet, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    option_a = models.CharField(max_length=500)
    option_b = models.CharField(max_length=500)
    option_c = models.CharField(max_length=500)
    option_d = models.CharField(max_length=500)
    correct_answer = models.CharField(max_length=1, choices=[
        ('A', 'Option A'),
        ('B', 'Option B'),
        ('C', 'Option C'),
        ('D', 'Option D'),
    ])
    explanation = models.TextField()
    sequence_order = models.IntegerField()
    difficulty_level = models.CharField(max_length=20, default='medium')
    
    # Hint system
    hint_text = models.TextField(blank=True, help_text="Hint to guide learner thinking")
    
    class Meta:
        ordering = ['sequence_order']
        unique_together = ['mcq_set', 'sequence_order']
    
    def __str__(self):
        return f"MCQ {self.sequence_order}: {self.question_text[:50]}..."

class MCQResponse(models.Model):
    """User's response to an MCQ"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    mcq = models.ForeignKey(MCQ, on_delete=models.CASCADE)
    learning_session = models.ForeignKey('learning_sessions.LearningSession', on_delete=models.CASCADE)
    selected_answer = models.CharField(max_length=1, choices=[
        ('A', 'Option A'),
        ('B', 'Option B'),
        ('C', 'Option C'),
        ('D', 'Option D'),
    ])
    is_correct = models.BooleanField()
    time_taken_seconds = models.IntegerField(help_text="Time taken to answer in seconds")
    attempted_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'mcq', 'learning_session']
    
    def __str__(self):
        return f"{self.user.username} - MCQ {self.mcq.sequence_order} - {'✓' if self.is_correct else '✗'}"