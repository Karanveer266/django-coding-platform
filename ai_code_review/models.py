from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class CodeReview(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.TextField()
    language = models.CharField(max_length=20)
    question = models.TextField(blank=True, null=True)
    review_result = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Code Review by {self.user.username} at {self.created_at}"
