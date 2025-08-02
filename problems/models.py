from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Problem(models.Model):
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]
    
    TYPE_CHOICES = [
        ('math', 'Mathematics'),
        ('dsa', 'Data Structures & Algorithms'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    difficulty = models.CharField(max_length=50, choices=DIFFICULTY_CHOICES)
    problem_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='math')
    
    # File uploads
    image_file = models.ImageField(upload_to='problems/images/', blank=True, null=True)
    pdf_file = models.FileField(upload_to='problems/pdfs/', blank=True, null=True)
    
    # Problem content
    input_format = models.TextField(blank=True, help_text="Description of input format")
    output_format = models.TextField(blank=True, help_text="Description of output format")
    constraints = models.TextField(blank=True, help_text="Constraints for the problem")
    
    # Test cases
    sample_input = models.TextField(blank=True)
    sample_output = models.TextField(blank=True)
    
    # New fields for enhanced judging
    time_limit = models.IntegerField(default=5, help_text="Time limit in seconds")
    memory_limit = models.CharField(max_length=10, default="128m", help_text="Memory limit (e.g., 128m, 256m)")
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    # Analytics
    total_attempts = models.IntegerField(default=0)
    successful_completions = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} ({self.get_difficulty_display()})"
    
    @property
    def success_rate(self):
        if self.total_attempts == 0:
            return 0
        return (self.successful_completions / self.total_attempts) * 100

class TestCase(models.Model):
    """Individual test cases for problems"""
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name='test_cases')
    input_data = models.TextField(help_text="Input for this test case")
    expected_output = models.TextField(help_text="Expected output for this test case")
    is_sample = models.BooleanField(default=False, help_text="Whether this is a sample test case")
    is_hidden = models.BooleanField(default=True, help_text="Whether this test case is hidden from users")
    points = models.IntegerField(default=1, help_text="Points awarded for passing this test case")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['id']
        
    def __str__(self):
        return f"{self.problem.title} - Test Case {self.id}"