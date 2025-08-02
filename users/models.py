from django.contrib.auth.models import AbstractUser
from django.db import models, transaction
from django.utils.crypto import get_random_string
from django.db.models import Count, Q

class User(AbstractUser):
    """
    — email must stay unique
    — username may be left blank by the registrant;
      we will auto-populate it right after the first save
    """
    email = models.EmailField(unique=True)

    username = models.CharField(
        max_length=150,
        unique=True,
        blank=True,          # user may omit it
        null=True,           # db allows NULL during first INSERT
    )

    # Profile fields
    bio = models.TextField(max_length=500, blank=True, help_text="Tell us about yourself")
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    location = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True)
    github_username = models.CharField(max_length=100, blank=True)
    linkedin_url = models.URLField(blank=True)
    
    # Preferences
    preferred_language = models.CharField(
        max_length=10, 
        choices=[('py', 'Python'), ('cpp', 'C++'), ('java', 'Java')],
        default='py'
    )
    theme_preference = models.CharField(
        max_length=10,
        choices=[('light', 'Light'), ('dark', 'Dark'), ('auto', 'Auto')],
        default='light'
    )
    
    # Statistics (will be updated by signals or periodic tasks)
    total_submissions = models.IntegerField(default=0)
    accepted_submissions = models.IntegerField(default=0)
    current_streak = models.IntegerField(default=0)
    max_streak = models.IntegerField(default=0)
    last_activity_date = models.DateField(null=True, blank=True)
    # Contest fields - REMOVED
    # contest_rating = models.IntegerField(null=True, blank=True, help_text="Rating from contests (null if no contests participated)")
    # total_contest_time = models.DurationField(null=True, blank=True)
    
    # Timestamps
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(null=True, blank=True)

    USERNAME_FIELD = "email"        # users still log in by email OR username
    REQUIRED_FIELDS = ['username']  # createsuperuser asks only for email+pwd

    def save(self, *args, **kwargs):
        """
        Two-phase save:
        1) insert row → pk generated
        2) if username is missing, set it to a slug based on pk
        """
        is_new = self.pk is None
        super().save(*args, **kwargs)          # phase-1: row exists, pk known

        if is_new and not self.username:       # phase-2: auto-fill once
            with transaction.atomic():
                self.username = f"user_{self.pk}"
                # collision extremely unlikely, but guard anyway with atomic check
                while User.objects.select_for_update().filter(username=self.username).exists():
                    self.username = f"user_{self.pk}_{get_random_string(4)}"
                # save only that field to avoid recursion
                User.objects.filter(pk=self.pk).update(username=self.username)

    @property
    def problems_solved(self):
        """Get count of unique problems solved by user"""
        from submit.models import Submission
        return Submission.objects.filter(
            user=self, 
            status='ACCEPTED'
        ).values('problem').distinct().count()

    @property
    def acceptance_rate(self):
        """Calculate user's overall acceptance rate"""
        if self.total_submissions == 0:
            return 0
        return (self.accepted_submissions / self.total_submissions) * 100

    @property
    def difficulty_stats(self):
        """Get breakdown of problems solved by difficulty"""
        from submit.models import Submission
        from problems.models import Problem
        
        solved_problems = Submission.objects.filter(
            user=self, 
            status='ACCEPTED'
        ).values_list('problem_id', flat=True).distinct()
        
        difficulty_counts = Problem.objects.filter(
            id__in=solved_problems
        ).values('difficulty').annotate(count=Count('id'))
        
        return {item['difficulty']: item['count'] for item in difficulty_counts}

    @property
    def recent_activity(self):
        """Get user's recent submissions"""
        from submit.models import Submission
        return Submission.objects.filter(user=self).order_by('-submitted_at')[:10]

    def get_avatar_url(self):
        """Get avatar URL or return default"""
        if self.avatar:
            return self.avatar.url
        return f"https://ui-avatars.com/api/?name={self.username}&background=3b82f6&color=fff&size=128"

    def __str__(self):
        return self.username or self.email