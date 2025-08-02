from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.db import transaction
from django.urls import reverse
import json
import logging

from .models import Submission, TestCaseResult
from .judge import judge
from problems.models import Problem, TestCase

logger = logging.getLogger(__name__)

@require_POST
@login_required
def submit_solution(request, problem_id):
    """Handle code submission for a problem"""
    problem = get_object_or_404(Problem, id=problem_id)
    
    try:
        data = json.loads(request.body)
        code = data.get('code', '').strip()
        language = data.get('language', 'py').lower()
        
        if not code:
            return JsonResponse({'error': 'Code cannot be empty'}, status=400)
            
        if language not in ['py', 'python', 'cpp', 'c++', 'java']:
            return JsonResponse({'error': 'Unsupported language'}, status=400)
        
        # Create submission
        submission = Submission.objects.create(
            user=request.user,
            problem=problem,
            code=code,
            language=language,
            status='JUDGING'
        )
        
        # Get test cases
        test_cases = TestCase.objects.filter(problem=problem).order_by('id')
        
        if not test_cases.exists():
            submission.status = 'ERROR'
            submission.error_data = 'No test cases available for this problem'
            submission.save()
            return JsonResponse({
                'submission_id': submission.id,
                'status': 'ERROR',
                'message': 'No test cases available'
            })
        
        # Judge the submission
        try:
            judge_results = judge.judge_submission(code, language, test_cases)
            
            # Update submission with results
            submission.status = judge_results['status']
            submission.total_test_cases = judge_results['total_tests']
            submission.passed_test_cases = judge_results['passed_tests']
            submission.max_execution_time = judge_results['max_time']
            submission.score = (judge_results['passed_tests'] / judge_results['total_tests']) * 100
            submission.save()
            
            # Save individual test case results
            with transaction.atomic():
                for test_result in judge_results['test_results']:
                    test_case = TestCase.objects.get(id=test_result['test_case_id'])
                    TestCaseResult.objects.create(
                        submission=submission,
                        test_case=test_case,
                        status=test_result['status'],
                        execution_time=test_result['execution_time'],
                        actual_output=test_result['actual_output'],
                        error_message=test_result['error']
                    )
            
            return JsonResponse({
                'submission_id': submission.id,
                'status': judge_results['status'],
                'passed_tests': judge_results['passed_tests'],
                'total_tests': judge_results['total_tests'],
                'max_time': judge_results['max_time'],
                'score': submission.score,
                'message': 'Submission judged successfully',
                'redirect_url': reverse('submit:submission_detail', args=[submission.id])
            })
            
        except Exception as e:
            logger.error(f"Error judging submission {submission.id}: {str(e)}")
            submission.status = 'ERROR'
            submission.error_data = str(e)
            submission.save()
            
            return JsonResponse({
                'submission_id': submission.id,
                'status': 'ERROR',
                'message': 'Error occurred during judging'
            })
            
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        logger.error(f"Error in submit_solution: {str(e)}")
        return JsonResponse({'error': 'An error occurred'}, status=500)

@login_required
def submission_detail(request, submission_id):
    """Display detailed results of a submission"""
    submission = get_object_or_404(Submission, id=submission_id)
    
    # Check if user can view this submission
    if submission.user != request.user and not request.user.is_staff:
        messages.error(request, "You don't have permission to view this submission.")
        return redirect('problems:list')
    
    # Get test case results
    test_results = TestCaseResult.objects.filter(submission=submission).select_related('test_case').order_by('test_case__id')
    
    context = {
        'submission': submission,
        'test_results': test_results,
        'can_resubmit': True,
    }
    
    return render(request, 'problems/submission_detail.html', context)

@login_required
def my_submissions(request):
    """Display user's submissions"""
    submissions = Submission.objects.filter(user=request.user).select_related('problem').order_by('-submitted_at')
    
    # Filter by problem if specified
    problem_id = request.GET.get('problem')
    if problem_id:
        submissions = submissions.filter(problem_id=problem_id)
    
    # Filter by status if specified
    status = request.GET.get('status')
    if status:
        submissions = submissions.filter(status=status)
    
    context = {
        'submissions': submissions,
        'selected_problem': problem_id,
        'selected_status': status,
        'status_choices': Submission.STATUS_CHOICES
    }
    
    return render(request, 'submit/my_submissions.html', context)

@login_required
def check_submission_status(request, submission_id):
    """AJAX endpoint to check submission status"""
    submission = get_object_or_404(Submission, id=submission_id)
    
    # Check permissions
    if submission.user != request.user and not request.user.is_staff:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    return JsonResponse({
        'status': submission.status,
        'passed_tests': submission.passed_test_cases,
        'total_tests': submission.total_test_cases,
        'score': submission.score,
        'max_time': submission.max_execution_time
    })