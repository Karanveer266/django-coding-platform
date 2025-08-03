import json
import os
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.conf import settings
from .models import CodeReview
import requests

@csrf_exempt
@login_required
@require_http_methods(["POST"])
def review_code(request):
    try:
        data = json.loads(request.body)
        code = data.get('code', '').strip()
        language = data.get('language', 'python')
        question = data.get('question', '').strip()
        
        if not code:
            return JsonResponse({'error': 'Code is required'}, status=400)
        
        # Get AI review
        review_result = get_ai_code_review(code, language, question)
        
        # Save to database
        code_review = CodeReview.objects.create(
            user=request.user,
            code=code,
            language=language,
            question=question,
            review_result=review_result
        )
        
        return JsonResponse({
            'success': True,
            'review': review_result,
            'review_id': code_review.id
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def get_ai_code_review(code, language, question=None):
    """Get AI code review using OpenRouter API"""
    
    # Check if API key is configured
    api_key = getattr(settings, 'OPENROUTER_API_KEY', None)
    if not api_key:
        return "AI code review is not configured. Please add OPENROUTER_API_KEY to your .env file."
    
    # Prepare the prompt
    base_prompt = f"""Please review the following {language} code and provide constructive feedback:

Code:
```{language}
{code}
```

Please provide:
1. Code quality assessment
2. Potential bugs or issues
3. Performance improvements
4. Best practices recommendations
5. Security considerations (if applicable)
6. Readability and maintainability suggestions

Make your review helpful and educational."""

    if question:
        base_prompt += f"\n\nSpecific question from the user: {question}\n\nPlease also address this specific question in your review."
    
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "HTTP-Referer": getattr(settings, 'OPENROUTER_SITE_URL', 'http://localhost:8000'),
                "X-Title": getattr(settings, 'OPENROUTER_SITE_NAME', 'EdPlatform'),
                "Content-Type": "application/json"
            },
            json={
                "model": "anthropic/claude-3.5-sonnet",
                "messages": [
                    {
                        "role": "user",
                        "content": base_prompt
                    }
                ],
                "max_tokens": 2000,
                "temperature": 0.7
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content']
        else:
            return f"AI service error: {response.status_code} - {response.text}"
            
    except requests.exceptions.Timeout:
        return "AI review service timed out. Please try again."
    except requests.exceptions.RequestException as e:
        return f"Error connecting to AI service: {str(e)}"
    except Exception as e:
        return f"Unexpected error during AI review: {str(e)}"

@login_required
def review_history(request):
    """Get user's code review history"""
    reviews = CodeReview.objects.filter(user=request.user)[:10]  # Last 10 reviews
    
    review_data = []
    for review in reviews:
        review_data.append({
            'id': review.id,
            'language': review.language,
            'question': review.question or '',
            'created_at': review.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'code_preview': review.code[:100] + '...' if len(review.code) > 100 else review.code,
        })
    
    return JsonResponse({
        'reviews': review_data
    })
