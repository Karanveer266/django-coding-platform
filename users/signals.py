from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import date, timedelta
from submit.models import Submission

@receiver(post_save, sender=Submission)
def update_user_statistics(sender, instance, created, **kwargs):
    """
    Update user statistics when a submission is saved
    """
    if not instance.user:
        return
    
    user = instance.user
    
    # Update total submissions count - only for completed submissions (not PENDING/JUDGING)
    user.total_submissions = Submission.objects.filter(
        user=user
    ).exclude(status__in=['PENDING', 'JUDGING']).count()
    
    # Update accepted submissions count
    user.accepted_submissions = Submission.objects.filter(
        user=user, 
        status='ACCEPTED'
    ).count()
    
    # Update activity streak
    if created and instance.status == 'ACCEPTED':
        today = date.today()
        yesterday = today - timedelta(days=1)
        
        # Check if user had activity yesterday
        had_activity_yesterday = Submission.objects.filter(
            user=user,
            status='ACCEPTED',
            submitted_at__date=yesterday
        ).exists()
        
        # Check if this is first activity today
        first_activity_today = not Submission.objects.filter(
            user=user,
            status='ACCEPTED',
            submitted_at__date=today
        ).exclude(id=instance.id).exists()
        
        if first_activity_today:
            if had_activity_yesterday or user.last_activity_date == yesterday:
                # Continue streak
                user.current_streak += 1
            else:
                # Start new streak
                user.current_streak = 1
            
            # Update max streak
            if user.current_streak > user.max_streak:
                user.max_streak = user.current_streak
            
            # Update last activity date
            user.last_activity_date = today
    
    user.save()

@receiver(post_save, sender='users.User')
def create_user_profile_defaults(sender, instance, created, **kwargs):
    """
    Set default values for new users
    """
    if created:
        # Set initial defaults (no contest rating until they participate in contests)
        instance.current_streak = 0
        instance.max_streak = 0
        instance.save()