from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.db import transaction
from django.urls import reverse
from django.utils import timezone
import json
import random
import logging

from .models import LearningSession
from mcq_generation.models import MCQSet, MCQ, MCQResponse
from problems.models import Problem

logger = logging.getLogger(__name__)

@login_required
def session_list(request):
    """Display user's learning sessions"""
    sessions = LearningSession.objects.filter(user=request.user).select_related('problem')
    
    context = {
        'sessions': sessions,
        'active_sessions': sessions.filter(status__in=['started', 'mcq_generation', 'mcq_ready', 'in_progress']),
        'completed_sessions': sessions.filter(status='completed')
    }
    
    return render(request, 'learning_sessions/session_list.html', context)

@login_required
def start_session(request, problem_id):
    """Start a new learning session for a problem"""
    problem = get_object_or_404(Problem, id=problem_id)
    
    # Check if user already has a session for this problem
    existing_session = LearningSession.objects.filter(user=request.user, problem=problem).first()
    
    if existing_session and not existing_session.is_completed:
        messages.info(request, f"You already have an active learning session for {problem.title}.")
        return redirect('learning_sessions:session_detail', session_id=existing_session.id)
    
    # Create new session
    session = LearningSession.objects.create(
        user=request.user,
        problem=problem,
        status='started'
    )
    
    messages.success(request, f"Learning session started for {problem.title}!")
    return redirect('learning_sessions:session_detail', session_id=session.id)

@login_required
def session_detail(request, session_id):
    """Display learning session details and current MCQ"""
    session = get_object_or_404(LearningSession, id=session_id, user=request.user)
    
    # Generate MCQs if not already generated
    if session.status == 'started':
        return redirect('learning_sessions:generate_mcqs', session_id=session.id)
    
    # Get current MCQ
    current_mcq = None
    if session.mcq_set and session.current_mcq_index < session.total_mcqs:
        try:
            current_mcq = session.mcq_set.questions.all()[session.current_mcq_index]
        except IndexError:
            pass
    
    # Get user's previous responses for this session
    responses = MCQResponse.objects.filter(
        learning_session=session,
        user=request.user
    ).select_related('mcq')
    
    context = {
        'session': session,
        'current_mcq': current_mcq,
        'responses': responses,
        'progress': (session.current_mcq_index / session.total_mcqs * 100) if session.total_mcqs > 0 else 0
    }
    
    return render(request, 'learning_sessions/session_detail.html', context)

@login_required
def generate_mcqs(request, session_id):
    """Generate MCQs for a learning session"""
    session = get_object_or_404(LearningSession, id=session_id, user=request.user)
    
    if session.status != 'started':
        return redirect('learning_sessions:session_detail', session_id=session.id)
    
    # Update session status
    session.status = 'mcq_generation'
    session.save()
    
    try:
        # Check if MCQs already exist for this problem
        existing_mcq_set = MCQSet.objects.filter(problem=session.problem, is_active=True).first()
        
        if existing_mcq_set:
            # Use existing MCQ set
            session.mcq_set = existing_mcq_set
            session.total_mcqs = existing_mcq_set.questions.count()
        else:
            # Generate new MCQs
            mcq_set = generate_mcqs_for_problem(session.problem)
            session.mcq_set = mcq_set
            session.total_mcqs = mcq_set.questions.count()
        
        session.status = 'mcq_ready'
        session.save()
        
        messages.success(request, "MCQs generated successfully! You can now start the learning session.")
        
    except Exception as e:
        logger.error(f"Error generating MCQs for session {session.id}: {str(e)}")
        session.status = 'failed'
        session.save()
        messages.error(request, "Failed to generate MCQs. Please try again.")
    
    return redirect('learning_sessions:session_detail', session_id=session.id)

@require_POST
@login_required
def submit_answer(request, session_id):
    """Submit answer for current MCQ"""
    session = get_object_or_404(LearningSession, id=session_id, user=request.user)
    
    try:
        data = json.loads(request.body)
        selected_answer = data.get('answer')
        time_taken = data.get('time_taken', 0)
        
        if not selected_answer or selected_answer not in ['A', 'B', 'C', 'D']:
            return JsonResponse({'error': 'Invalid answer'}, status=400)
        
        # Get current MCQ
        if not session.mcq_set or session.current_mcq_index >= session.total_mcqs:
            return JsonResponse({'error': 'No current MCQ available'}, status=400)
        
        current_mcq = session.mcq_set.questions.all()[session.current_mcq_index]
        
        # Check if already answered
        existing_response = MCQResponse.objects.filter(
            learning_session=session,
            mcq=current_mcq,
            user=request.user
        ).first()
        
        if existing_response:
            return JsonResponse({'error': 'Already answered this question'}, status=400)
        
        # Save response
        is_correct = selected_answer == current_mcq.correct_answer
        
        MCQResponse.objects.create(
            user=request.user,
            mcq=current_mcq,
            learning_session=session,
            selected_answer=selected_answer,
            is_correct=is_correct,
            time_taken_seconds=time_taken
        )
        
        # Update session stats
        if is_correct:
            session.correct_answers += 1
        
        session.current_mcq_index += 1
        
        # Check if session is completed
        if session.current_mcq_index >= session.total_mcqs:
            session.status = 'completed'
            session.completed_at = timezone.now()
        else:
            session.status = 'in_progress'
        
        session.save()
        
        response_data = {
            'correct': is_correct,
            'correct_answer': current_mcq.correct_answer,
            'explanation': current_mcq.explanation,
            'session_completed': session.status == 'completed',
            'next_question': session.current_mcq_index < session.total_mcqs,
            'accuracy': session.accuracy,
            'progress': (session.current_mcq_index / session.total_mcqs * 100)
        }
        
        return JsonResponse(response_data)
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        logger.error(f"Error submitting answer for session {session.id}: {str(e)}")
        return JsonResponse({'error': 'An error occurred'}, status=500)

@login_required
def session_results(request, session_id):
    """Display session results and analysis"""
    session = get_object_or_404(LearningSession, id=session_id, user=request.user)
    
    if session.status != 'completed':
        messages.warning(request, "This session is not yet completed.")
        return redirect('learning_sessions:session_detail', session_id=session.id)
    
    # Get all responses for analysis
    responses = MCQResponse.objects.filter(
        learning_session=session,
        user=request.user
    ).select_related('mcq').order_by('mcq__sequence_order')
    
    # Calculate statistics
    correct_count = responses.filter(is_correct=True).count()
    total_count = responses.count()
    accuracy = (correct_count / total_count * 100) if total_count > 0 else 0
    
    # Calculate average time per question
    total_time = sum(response.time_taken_seconds for response in responses)
    avg_time = total_time / total_count if total_count > 0 else 0
    
    context = {
        'session': session,
        'responses': responses,
        'stats': {
            'correct_count': correct_count,
            'total_count': total_count,
            'accuracy': accuracy,
            'total_time': total_time,
            'avg_time': avg_time
        }
    }
    
    return render(request, 'learning_sessions/session_results.html', context)

def generate_mcqs_for_problem(problem):
    """Generate MCQs for a given problem (simplified version)"""
    mcq_set = MCQSet.objects.create(
        problem=problem,
        total_questions=5  # Generate 5 MCQs per problem
    )
    
    # Sample MCQ generation - in a real application, this would use AI/NLP
    sample_questions = generate_sample_mcqs(problem)
    
    for i, mcq_data in enumerate(sample_questions):
        MCQ.objects.create(
            mcq_set=mcq_set,
            sequence_order=i + 1,
            **mcq_data
        )
    
    return mcq_set

def generate_sample_mcqs(problem):
    """Generate sample MCQs based on problem content"""
    # This is a simplified version - in production, you'd use AI/NLP to generate contextual questions
    
    base_questions = [
        {
            'question_text': f'What is the time complexity of the optimal solution for "{problem.title}"?',
            'option_a': 'O(n)',
            'option_b': 'O(n log n)',
            'option_c': 'O(n²)',
            'option_d': 'O(1)',
            'correct_answer': 'B',
            'explanation': 'The optimal solution typically requires sorting or similar operations with O(n log n) complexity.',
            'difficulty_level': 'medium',
            'hint_text': 'Think about what operations are needed to solve this efficiently.'
        },
        {
            'question_text': f'Which data structure would be most appropriate for solving "{problem.title}"?',
            'option_a': 'Array',
            'option_b': 'Hash Map',
            'option_c': 'Binary Tree',
            'option_d': 'Stack',
            'correct_answer': 'B',
            'explanation': 'Hash maps provide O(1) lookup time which is often needed for optimal solutions.',
            'difficulty_level': 'medium',
            'hint_text': 'Consider what kind of lookups or storage you need.'
        },
        {
            'question_text': f'What is the space complexity of the optimal solution for "{problem.title}"?',
            'option_a': 'O(1)',
            'option_b': 'O(n)',
            'option_c': 'O(n log n)',
            'option_d': 'O(n²)',
            'correct_answer': 'B',
            'explanation': 'Most problems require additional space proportional to input size.',
            'difficulty_level': 'easy',
            'hint_text': 'Think about additional data structures needed.'
        },
        {
            'question_text': f'Which algorithmic approach is most suitable for solving "{problem.title}"?',
            'option_a': 'Brute Force',
            'option_b': 'Dynamic Programming',
            'option_c': 'Greedy Algorithm',
            'option_d': 'Divide and Conquer',
            'correct_answer': 'B',
            'explanation': 'Many coding problems can be optimized using dynamic programming techniques.',
            'difficulty_level': 'hard',
            'hint_text': 'Consider if the problem has overlapping subproblems.'
        },
        {
            'question_text': f'What edge case should you consider when solving "{problem.title}"?',
            'option_a': 'Empty input',
            'option_b': 'Single element',
            'option_c': 'Duplicate elements',
            'option_d': 'All of the above',
            'correct_answer': 'D',
            'explanation': 'Good solutions always handle edge cases including empty input, single elements, and duplicates.',
            'difficulty_level': 'medium',
            'hint_text': 'Think about unusual or boundary conditions.'
        }
    ]
    
    return base_questions