from django.urls import path
from . import views

app_name = 'problems'

urlpatterns = [
    path('', views.problem_list, name='list'),
    path('<int:problem_id>/', views.problem_detail, name='detail'),
    path('<int:problem_id>/submit/', views.submit_solution, name='submit'),
    path('<int:problem_id>/stats/', views.problem_stats, name='stats'),
    path('submission/<int:submission_id>/', views.submission_detail, name='submission_detail'),
    path('leaderboard/', views.leaderboard_view, name='leaderboard'), # Added leaderboard URL
    path('contests/', views.contest_list, name='contests'),
]