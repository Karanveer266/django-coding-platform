from django.urls import path
from . import views

app_name = 'blogs'

urlpatterns = [
    # Blog list and detail
    path('', views.blog_list, name='list'),
    path('post/<slug:slug>/', views.blog_detail, name='detail'),
    
    # Categories and tags
    path('category/<slug:slug>/', views.category_detail, name='category'),
    path('tag/<slug:slug>/', views.tag_detail, name='tag'),
    
    # Post management
    path('create/', views.create_post, name='create'),
    path('post/<slug:slug>/edit/', views.edit_post, name='edit'),
    path('post/<slug:slug>/delete/', views.delete_post, name='delete'),
    path('my-posts/', views.my_posts, name='my_posts'),
    
    # Post interactions
    path('post/<slug:slug>/like/', views.like_post, name='like'),
]