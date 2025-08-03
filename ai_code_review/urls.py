from django.urls import path
from . import views

app_name = 'ai_code_review'

urlpatterns = [
    path('review/', views.review_code, name='review_code'),
    path('history/', views.review_history, name='review_history'),
]