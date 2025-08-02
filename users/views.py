from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.forms import UserCreationForm
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.db.models import Count, Q
from django.core.exceptions import ValidationError
from .models import User
import json
import logging

logger = logging.getLogger(__name__)

def login_view(request):
    if request.method == 'POST':
        if request.content_type == 'application/json':
            # Handle API login
            try:
                data = json.loads(request.body)
                username = data.get('username')
                email = data.get('email')
                password = data.get('password')
                
                # Authenticate by email or username
                user = None
                if email:
                    try:
                        user_obj = User.objects.get(email=email)
                        user = authenticate(request, username=user_obj.username, password=password)
                    except User.DoesNotExist:
                        pass
                elif username:
                    user = authenticate(request, username=username, password=password)
                
                if user is not None:
                    login(request, user)
                    return JsonResponse({
                        'status': 'success',
                        'message': 'Login successful',
                        'redirect_url': '/dashboard/'
                    })
                else:
                    return JsonResponse({
                        'status': 'error',
                        'non_field_errors': ['Invalid credentials']
                    }, status=400)
            except json.JSONDecodeError:
                return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
        else:
            # Handle form login
            username = request.POST.get('username')
            password = request.POST.get('password')
            
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
            else:
                messages.error(request, 'Invalid username or password.')
    
    return render(request, 'login.html')

def signup_view(request):
    if request.method == 'POST':
        if request.content_type == 'application/json':
            # Handle API signup
            try:
                data = json.loads(request.body)
                username = data.get('username')
                email = data.get('email')
                password1 = data.get('password1')
                password2 = data.get('password2')
                
                # Validation
                errors = {}
                if User.objects.filter(email=email).exists():
                    errors['email'] = ['User with this email already exists.']
                
                if User.objects.filter(username=username).exists():
                    errors['username'] = ['User with this username already exists.']
                
                if password1 != password2:
                    errors['password1'] = ['Passwords do not match.']
                
                if len(password1) < 8:
                    errors['password1'] = ['Password must be at least 8 characters long.']
                
                if errors:
                    return JsonResponse({
                        'status': 'error',
                        **errors
                    }, status=400)
                
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password1
                )
                login(request, user)
                return JsonResponse({
                    'status': 'success',
                    'message': 'Registration successful',
                    'redirect_url': '/dashboard/'
                })
            except json.JSONDecodeError:
                return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
        else:
            # Handle form signup
            username = request.POST.get('username')
            email = request.POST.get('email')
            password = request.POST.get('password')
            
            if User.objects.filter(email=email).exists():
                messages.error(request, 'User with this email already exists.')
            else:
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password
                )
                login(request, user)
                return redirect('dashboard')
    
    return render(request, 'signup.html')

@login_required
def dashboard_view(request):
    from django.db.models import Count, Q
    from problems.models import Problem
    from submit.models import Submission
    from blogs.models import BlogPost
    from datetime import datetime, timedelta
    
    user = request.user
    
    # Calculate user statistics
    total_submissions = Submission.objects.filter(user=user).count()
    accepted_submissions = Submission.objects.filter(user=user, status='ACCEPTED').count()
    
    # Problems solved (unique problems with accepted submissions)
    problems_solved = Submission.objects.filter(
        user=user, 
        status='ACCEPTED'
    ).values('problem').distinct().count()
    
    # Acceptance rate
    acceptance_rate = round((accepted_submissions / total_submissions * 100) if total_submissions > 0 else 0, 1)
    
    # Recent activity (last 10 submissions)
    recent_submissions = Submission.objects.filter(user=user).select_related('problem').order_by('-submitted_at')[:10]
    
    # Current streak calculation
    today = datetime.now().date()
    current_streak = 0
    check_date = today
    
    # Check consecutive days with accepted submissions
    while True:
        daily_accepted = Submission.objects.filter(
            user=user,
            status='ACCEPTED',
            submitted_at__date=check_date
        ).exists()
        
        if daily_accepted:
            current_streak += 1
            check_date -= timedelta(days=1)
        else:
            break
    
    # Time spent coding (sum of all submission times - approximation)
    total_time_spent = total_submissions * 15  # Assume 15 minutes per submission on average
    
    # Difficulty breakdown
    difficulty_stats = {}
    solved_problems = Submission.objects.filter(
        user=user, 
        status='ACCEPTED'
    ).values_list('problem_id', flat=True).distinct()
    
    difficulty_counts = Problem.objects.filter(
        id__in=solved_problems
    ).values('difficulty').annotate(count=Count('id'))
    
    for item in difficulty_counts:
        difficulty_stats[item['difficulty']] = item['count']
    
    # Recent blog posts for the dashboard
    recent_blog_posts = BlogPost.objects.filter(status='published').order_by('-published_date')[:3]
    
    # Upcoming contests (placeholder)
    upcoming_contests = [
        {
            'name': 'Weekly Contest #47',
            'date': 'Tomorrow at 2:00 PM',
            'type': 'weekly'
        },
        {
            'name': 'Algorithm Marathon',
            'date': 'Friday at 10:00 AM',
            'type': 'marathon'
        }
    ]
    
    # Popular problems (based on submission count)
    popular_problems = Problem.objects.annotate(
        submission_count=Count('submission')
    ).order_by('-submission_count')[:5]
    
    context = {
        'user': user,
        'stats': {
            'problems_solved': problems_solved,
            'total_submissions': total_submissions,
            'accepted_submissions': accepted_submissions,
            'acceptance_rate': acceptance_rate,
            'current_streak': current_streak,
            'max_streak': user.max_streak,
            'contest_rating': user.contest_rating,
            'time_spent': total_time_spent,
            'difficulty_stats': difficulty_stats,
        },
        'recent_submissions': recent_submissions,
        'recent_blog_posts': recent_blog_posts,
        'upcoming_contests': upcoming_contests,
        'popular_problems': popular_problems,
    }
    
    return render(request, 'dashboard.html', context)

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def profile_view(request, username=None):
    """Display user profile"""
    if username:
        profile_user = get_object_or_404(User, username=username)
    else:
        profile_user = request.user
    
    # Get user statistics
    from submit.models import Submission
    from problems.models import Problem
    from blogs.models import BlogPost
    
    # Submission stats
    total_submissions = Submission.objects.filter(user=profile_user).count()
    accepted_submissions = Submission.objects.filter(user=profile_user, status='ACCEPTED').count()
    
    # Problems solved
    problems_solved = Submission.objects.filter(
        user=profile_user, 
        status='ACCEPTED'
    ).values('problem').distinct().count()
    
    # Recent submissions
    recent_submissions = Submission.objects.filter(
        user=profile_user
    ).select_related('problem').order_by('-submitted_at')[:10]
    
    # Blog posts
    blog_posts = BlogPost.objects.filter(
        author=profile_user,
        status='published'
    ).order_by('-published_date')[:5]
    
    # Activity by difficulty
    difficulty_stats = {}
    solved_problems = Submission.objects.filter(
        user=profile_user, 
        status='ACCEPTED'
    ).values_list('problem_id', flat=True).distinct()
    
    difficulty_counts = Problem.objects.filter(
        id__in=solved_problems
    ).values('difficulty').annotate(count=Count('id'))
    
    for item in difficulty_counts:
        difficulty_stats[item['difficulty']] = item['count']
    
    context = {
        'profile_user': profile_user,
        'is_own_profile': request.user == profile_user,
        'stats': {
            'total_submissions': total_submissions,
            'accepted_submissions': accepted_submissions,
            'problems_solved': problems_solved,
            'acceptance_rate': round((accepted_submissions / total_submissions * 100) if total_submissions > 0 else 0, 1),
            'difficulty_stats': difficulty_stats,
        },
        'recent_submissions': recent_submissions,
        'blog_posts': blog_posts,
    }
    
    return render(request, 'users/profile.html', context)

@login_required
def settings_view(request):
    """User settings page"""
    if request.method == 'POST':
        # Handle profile update
        user = request.user
        
        # Basic info
        user.username = request.POST.get('username', user.username)
        user.email = request.POST.get('email', user.email)
        user.bio = request.POST.get('bio', user.bio)
        user.location = request.POST.get('location', user.location)
        user.website = request.POST.get('website', user.website)
        user.github_username = request.POST.get('github_username', user.github_username)
        user.linkedin_url = request.POST.get('linkedin_url', user.linkedin_url)
        
        # Preferences
        user.preferred_language = request.POST.get('preferred_language', user.preferred_language)
        user.theme_preference = request.POST.get('theme_preference', user.theme_preference)
        
        # Handle avatar upload
        if 'avatar' in request.FILES:
            user.avatar = request.FILES['avatar']
        
        try:
            user.save()
            messages.success(request, 'Your settings have been updated successfully!')
        except ValidationError as e:
            messages.error(request, f'Validation error: {str(e)}')
        except Exception as e:
            logger.error(f'Error updating user settings for {user.username}: {str(e)}')
            messages.error(request, 'An unexpected error occurred while updating your settings.')
        
        return redirect('users:settings')
    
    context = {
        'user': request.user,
    }
    
    return render(request, 'users/settings.html', context)

@login_required
def edit_profile_view(request):
    """Edit profile page"""
    if request.method == 'POST':
        user = request.user
        
        # Update user fields
        user.bio = request.POST.get('bio', '')
        user.location = request.POST.get('location', '')
        user.website = request.POST.get('website', '')
        user.github_username = request.POST.get('github_username', '')
        user.linkedin_url = request.POST.get('linkedin_url', '')
        
        # Handle avatar upload
        if 'avatar' in request.FILES:
            user.avatar = request.FILES['avatar']
        
        try:
            user.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('users:profile')
        except Exception as e:
            messages.error(request, f'Error updating profile: {str(e)}')
    
    return render(request, 'users/edit_profile.html', {'user': request.user})