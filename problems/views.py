from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Count, Avg
from django.contrib import messages
from django.http import JsonResponse
from .models import Problem, TestCase
from submit.models import Submission, TestCaseResult
from submit.judge import judge
import json

def problem_list(request):
    """Display list of problems with filtering and pagination"""
    problems = Problem.objects.filter(is_active=True)
    
    # Filtering
    difficulty = request.GET.get('difficulty')
    problem_type = request.GET.get('type')
    search = request.GET.get('search')
    
    if difficulty:
        problems = problems.filter(difficulty=difficulty)
    if problem_type:
        problems = problems.filter(problem_type=problem_type)
    if search:
        problems = problems.filter(
            Q(title__icontains=search) | 
            Q(description__icontains=search)
        )
    
    # Add user submission status if authenticated
    if request.user.is_authenticated:
        user_submissions = Submission.objects.filter(
            user=request.user,
            status='ACCEPTED'  # Accepted
        ).values_list('problem_id', flat=True)
        
        for problem in problems:
            problem.is_solved = problem.id in user_submissions
    
    # Pagination
    paginator = Paginator(problems, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'problems': page_obj,
        'difficulty_choices': Problem.DIFFICULTY_CHOICES,
        'type_choices': Problem.TYPE_CHOICES,
        'current_difficulty': difficulty,
        'current_type': problem_type,
        'current_search': search or '',
    }
    
    return render(request, 'problems/problem_list.html', context)

def problem_detail(request, problem_id):
    """Display problem details"""
    problem = get_object_or_404(Problem, id=problem_id, is_active=True)
    
    # Get sample test cases
    sample_test_cases = problem.test_cases.filter(is_sample=True)
    
    # Get user's submissions for this problem if authenticated
    user_submissions = []
    if request.user.is_authenticated:
        user_submissions = Submission.objects.filter(
            user=request.user,
            problem=problem
        ).order_by('-submitted_at')[:10]
    
    # Get problem statistics
    stats = {
        'total_submissions': problem.total_attempts,
        'accepted_submissions': problem.successful_completions,
        'success_rate': problem.success_rate,
    }
    
    context = {
        'problem': problem,
        'sample_test_cases': sample_test_cases,
        'user_submissions': user_submissions,
        'stats': stats,
    }
    
    return render(request, 'problems/problem_detail.html', context)

@login_required
def submit_solution(request, problem_id):
    """Handle code submission"""
    problem = get_object_or_404(Problem, id=problem_id, is_active=True)
    
    if request.method == 'POST':
        if request.content_type == 'application/json':
            try:
                data = json.loads(request.body)
                code = data.get('code', '').strip()
                language = data.get('language', 'python')
                
                if not code:
                    return JsonResponse({
                        'error': 'Code cannot be empty'
                    }, status=400)
                
                # Create submission
                submission = Submission.objects.create(
                    user=request.user,
                    problem=problem,
                    code=code,
                    language=language,
                    status='JUDGING'  # Judging
                )
                
                try:
                    # Get test cases for the problem
                    test_cases = problem.test_cases.all()
                    
                    if test_cases.exists():
                        # Judge the submission
                        judge_result = judge.judge_submission(code, language, test_cases)
                        
                        # Update submission with results
                        submission.status = judge_result['status']
                        submission.total_test_cases = judge_result['total_tests']
                        submission.passed_test_cases = judge_result['passed_tests']
                        submission.execution_time = judge_result['max_time']
                        submission.score = (judge_result['passed_tests'] / judge_result['total_tests']) * 100
                        submission.save()
                        
                        # Save individual test case results
                        for test_result in judge_result['test_results']:
                            TestCaseResult.objects.create(
                                submission=submission,
                                test_case_id=test_result['test_case_id'],
                                status=test_result['status'],
                                execution_time=test_result['execution_time'],
                                actual_output=test_result['actual_output'],
                                error_message=test_result.get('error', '')
                            )
                        
                        # Update problem statistics if accepted
                        if submission.status == 'ACCEPTED':
                            problem.successful_completions += 1
                        problem.total_attempts += 1
                        problem.save()
                        
                        return JsonResponse({
                            'success': True,
                            'submission_id': submission.id,
                            'status': submission.status,
                            'passed_tests': submission.passed_test_cases,
                            'total_tests': submission.total_test_cases,
                            'score': submission.score,
                            'execution_time': submission.execution_time,
                            'message': f'Submission judged: {submission.get_status_display()}'
                        })
                    else:
                        submission.status = 'ERROR'
                        submission.error_data = 'No test cases available for this problem'
                        submission.save()
                        
                        return JsonResponse({
                            'error': 'No test cases available for this problem'
                        }, status=400)
                        
                except Exception as e:
                    submission.status = 'ERROR'
                    submission.error_data = str(e)
                    submission.save()
                    
                    return JsonResponse({
                        'error': f'Judging failed: {str(e)}'
                    }, status=500)
                
            except json.JSONDecodeError:
                return JsonResponse({'error': 'Invalid JSON'}, status=400)
        else:
            # Handle form submission
            code = request.POST.get('code', '').strip()
            language = request.POST.get('language', 'python')
            
            if not code:
                messages.error(request, 'Code cannot be empty')
                return redirect('problems:detail', problem_id=problem_id)
            
            submission = Submission.objects.create(
                user=request.user,
                problem=problem,
                code=code,
                language=language,
                status='PENDING'
            )
            
            messages.success(request, 'Code submitted successfully!')
            return redirect('problems:detail', problem_id=problem_id)
    
    return redirect('problems:detail', problem_id=problem_id)

def leaderboard(request):
    """Display global leaderboard"""
    # Get top users by problems solved
    top_users = Submission.objects.filter(
        status='ACCEPTED'
    ).values(
        'user__username',
        'user__id'
    ).annotate(
        problems_solved=Count('problem', distinct=True),
        total_submissions=Count('id'),
        avg_time=Avg('execution_time')
    ).order_by('-problems_solved', 'total_submissions')[:50]
    
    context = {
        'top_users': top_users,
    }
    
    return render(request, 'problems/leaderboard.html', context)

def contest_list(request):
    """Display list of contests"""
    # Placeholder for future contest functionality
    context = {
        'contests': [],
        'message': 'Contests feature coming soon!'
    }
    
    return render(request, 'problems/contest_list.html', context)

def problem_stats(request, problem_id):
    """Get problem statistics via AJAX"""
    problem = get_object_or_404(Problem, id=problem_id)
    
    # Get submission statistics
    submissions = Submission.objects.filter(problem=problem)
    
    stats = {
        'total_submissions': submissions.count(),
        'accepted': submissions.filter(status='ACCEPTED').count(),
        'wrong_answer': submissions.filter(status='WRONG_ANSWER').count(),
        'time_limit_exceeded': submissions.filter(status='TIME_LIMIT_EXCEEDED').count(),
        'runtime_error': submissions.filter(status='RUNTIME_ERROR').count(),
        'compilation_error': submissions.filter(status='COMPILATION_ERROR').count(),
    }
    
    # Calculate success rate
    if stats['total_submissions'] > 0:
        stats['success_rate'] = (stats['accepted'] / stats['total_submissions']) * 100
    else:
        stats['success_rate'] = 0
    
    return JsonResponse(stats)

@login_required
def submission_detail(request, submission_id):
    """Show detailed submission results"""
    submission = get_object_or_404(Submission, id=submission_id, user=request.user)
    test_results = submission.test_results.all().order_by('test_case__id')
    
    context = {
        'submission': submission,
        'test_results': test_results,
    }
    
    return render(request, 'problems/submission_detail.html', context)