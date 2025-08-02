from django.urls import path
from . import views

app_name = 'learning_sessions'

urlpatterns = [
    path('', views.session_list, name='session_list'),
    path('start/<int:problem_id>/', views.start_session, name='start_session'),
    path('<int:session_id>/', views.session_detail, name='session_detail'),
    path('<int:session_id>/generate/', views.generate_mcqs, name='generate_mcqs'),
    path('<int:session_id>/submit/', views.submit_answer, name='submit_answer'),
    path('<int:session_id>/results/', views.session_results, name='session_results'),
]