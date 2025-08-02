from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.generic import ListView, DetailView
from .models import BlogPost, Category, Tag, Comment, BlogLike
from .forms import CommentForm, BlogPostForm
import json

def blog_list(request):
    """Display list of blog posts with filtering and pagination"""
    posts = BlogPost.objects.filter(status='published').select_related('author', 'category').prefetch_related('tags')
    
    # Filtering
    category_slug = request.GET.get('category')
    tag_slug = request.GET.get('tag')
    search = request.GET.get('search')
    
    if category_slug:
        posts = posts.filter(category__slug=category_slug)
    if tag_slug:
        posts = posts.filter(tags__slug=tag_slug)
    if search:
        posts = posts.filter(
            Q(title__icontains=search) | 
            Q(content__icontains=search) |
            Q(excerpt__icontains=search)
        )
    
    # Get sidebar data
    categories = Category.objects.all()
    popular_tags = Tag.objects.annotate(
        post_count=Count('blogpost')
    ).filter(post_count__gt=0).order_by('-post_count')[:10]
    featured_posts = BlogPost.objects.filter(
        status='published', 
        is_featured=True
    )[:3]
    recent_posts = BlogPost.objects.filter(status='published')[:5]
    
    # Pagination
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'posts': page_obj,
        'categories': categories,
        'popular_tags': popular_tags,
        'featured_posts': featured_posts,
        'recent_posts': recent_posts,
        'current_category': category_slug,
        'current_tag': tag_slug,
        'current_search': search or '',
    }
    
    return render(request, 'blogs/blog_list.html', context)

def blog_detail(request, slug):
    """Display blog post detail"""
    post = get_object_or_404(
        BlogPost.objects.select_related('author', 'category').prefetch_related('tags', 'comments__author', 'comments__replies__author'),
        slug=slug,
        status='published'
    )
    
    # Increment view count
    post.increment_view_count()
    
    # Get comments
    comments = post.comments.filter(is_approved=True, parent=None).order_by('-created_at')
    
    # Get related posts
    related_posts = post.get_related_posts()
    
    # Check if user has liked this post
    user_has_liked = False
    if request.user.is_authenticated:
        user_has_liked = BlogLike.objects.filter(user=request.user, post=post).exists()
    
    # Handle comment form
    comment_form = CommentForm()
    if request.method == 'POST' and request.user.is_authenticated:
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.post = post
            comment.author = request.user
            
            # Handle reply
            parent_id = request.POST.get('parent_id')
            if parent_id:
                try:
                    parent_comment = Comment.objects.get(id=parent_id, post=post)
                    comment.parent = parent_comment
                except Comment.DoesNotExist:
                    pass
            
            comment.save()
            messages.success(request, 'Your comment has been added!')
            return redirect('blogs:detail', slug=slug)
    
    context = {
        'post': post,
        'comments': comments,
        'related_posts': related_posts,
        'user_has_liked': user_has_liked,
        'comment_form': comment_form,
        'reading_time': post.get_reading_time(),
        'comment_count': post.comments.filter(is_approved=True).count(),
    }
    
    return render(request, 'blogs/blog_detail.html', context)

@require_POST
@login_required
def like_post(request, slug):
    """Toggle like on a blog post"""
    post = get_object_or_404(BlogPost, slug=slug, status='published')
    
    try:
        like = BlogLike.objects.get(user=request.user, post=post)
        like.delete()
        liked = False
        post.like_count = max(0, post.like_count - 1)
    except BlogLike.DoesNotExist:
        BlogLike.objects.create(user=request.user, post=post)
        liked = True
        post.like_count += 1
    
    post.save(update_fields=['like_count'])
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'liked': liked,
            'like_count': post.like_count
        })
    
    return redirect('blogs:detail', slug=slug)

def category_detail(request, slug):
    """Display posts in a specific category"""
    category = get_object_or_404(Category, slug=slug)
    posts = BlogPost.objects.filter(
        status='published', 
        category=category
    ).select_related('author').prefetch_related('tags')
    
    # Pagination
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'posts': page_obj,
    }
    
    return render(request, 'blogs/category_detail.html', context)

def tag_detail(request, slug):
    """Display posts with a specific tag"""
    tag = get_object_or_404(Tag, slug=slug)
    posts = BlogPost.objects.filter(
        status='published', 
        tags=tag
    ).select_related('author', 'category').prefetch_related('tags')
    
    # Pagination
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'tag': tag,
        'posts': page_obj,
    }
    
    return render(request, 'blogs/tag_detail.html', context)

@login_required
def create_post(request):
    """Create a new blog post"""
    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            form.save_m2m()  # Save tags
            messages.success(request, 'Your blog post has been created!')
            return redirect('blogs:detail', slug=post.slug)
    else:
        form = BlogPostForm()
    
    context = {
        'form': form,
        'title': 'Create New Post'
    }
    
    return render(request, 'blogs/create_post.html', context)

@login_required
def edit_post(request, slug):
    """Edit an existing blog post"""
    post = get_object_or_404(BlogPost, slug=slug, author=request.user)
    
    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your blog post has been updated!')
            return redirect('blogs:detail', slug=post.slug)
    else:
        form = BlogPostForm(instance=post)
    
    context = {
        'form': form,
        'post': post,
        'title': 'Edit Post'
    }
    
    return render(request, 'blogs/create_post.html', context)

@login_required
def delete_post(request, slug):
    """Delete a blog post"""
    post = get_object_or_404(BlogPost, slug=slug, author=request.user)
    
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Your blog post has been deleted!')
        return redirect('blogs:list')
    
    context = {
        'post': post
    }
    
    return render(request, 'blogs/delete_post.html', context)

@login_required
def my_posts(request):
    """Display user's own blog posts"""
    posts = BlogPost.objects.filter(author=request.user).order_by('-created_at')
    
    # Pagination
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'posts': page_obj,
    }
    
    return render(request, 'blogs/my_posts.html', context)