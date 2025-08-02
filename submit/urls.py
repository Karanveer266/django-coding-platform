from django.urls import path
from . import views

app_name = 'submit'

urlpatterns = [
    path('submit/<int:problem_id>/', views.submit_solution, name='submit_solution'),
    path('submission/<int:submission_id>/', views.submission_detail, name='submission_detail'),
    path('my-submissions/', views.my_submissions, name='my_submissions'),
    path('status/<int:submission_id>/', views.check_submission_status, name='check_status'),
]