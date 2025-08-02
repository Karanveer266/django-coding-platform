from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import BlogPost

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'author', 'status', 'published_date', 
        'view_count', 'like_count', 'is_featured', 'view_post_link'
    ]
    list_filter = [
        'status', 'is_featured', 'published_date', 'created_at', 
        'category', 'tags'
    ]
    search_fields = ['title', 'content', 'author__username', 'excerpt']
    readonly_fields = [
        'slug', 'created_at', 'updated_at', 'view_count', 
        'like_count', 'view_post_link', 'post_summary'
    ]
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'published_date'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'author', 'status', 'is_featured')
        }),
        ('Content', {
            'fields': ('excerpt', 'content')
        }),
        ('Organization', {
            'fields': ('category', 'tags')
        }),
        ('SEO & Meta', {
            'fields': ('meta_title', 'meta_description', 'featured_image'),
            'classes': ('collapse',)
        }),
        ('Publishing', {
            'fields': ('published_date', 'allow_comments')
        }),
        ('Statistics', {
            'fields': ('view_count', 'like_count'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
        ('Actions & Summary', {
            'fields': ('view_post_link', 'post_summary')
        }),
    )
    
    filter_horizontal = ['tags']
    
    def view_post_link(self, obj):
        if obj.pk and obj.status == 'published':
            url = reverse('blogs:detail', args=[obj.slug])
            return format_html('<a href="{}" target="_blank">View Post</a>', url)
        elif obj.pk:
            return format_html('<span style="color: gray;">Not Published</span>')
        return "N/A"
    view_post_link.short_description = "View"
    
    def post_summary(self, obj):
        if obj.pk:
            status_color = {
                'draft': 'orange',
                'published': 'green',
                'archived': 'gray'
            }.get(obj.status, 'gray')
            
            reading_time = len(obj.content.split()) // 200  # Approximate reading time
            
            return format_html(
                '<div style="line-height: 1.4;">'
                '<span style="color: {};">● {}</span><br>'
                '<strong>Views:</strong> {} | <strong>Likes:</strong> {}<br>'
                '<strong>Reading time:</strong> ~{} min<br>'
                '<strong>Words:</strong> {}<br>'
                '{}'
                '</div>',
                status_color, obj.get_status_display().upper(),
                obj.view_count, obj.like_count,
                max(1, reading_time), len(obj.content.split()),
                '<span style="color: red;">★ FEATURED</span>' if obj.is_featured else ''
            )
        return "N/A"
    post_summary.short_description = "Summary"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('author', 'category').prefetch_related('tags')
    
    def save_model(self, request, obj, form, change):
        # Auto-set published_date when status changes to published
        if obj.status == 'published' and not obj.published_date:
            obj.published_date = timezone.now()
        
        # Auto-generate excerpt if not provided
        if not obj.excerpt and obj.content:
            # Get first paragraph or first 150 words
            words = obj.content.split()[:150]
            obj.excerpt = ' '.join(words) + ('...' if len(obj.content.split()) > 150 else '')
        
        super().save_model(request, obj, form, change)
    
    actions = ['make_published', 'make_draft', 'make_featured', 'remove_featured']
    
    def make_published(self, request, queryset):
        updated = queryset.update(status='published', published_date=timezone.now())
        self.message_user(request, f'{updated} posts were successfully published.')
    make_published.short_description = "Mark selected posts as published"
    
    def make_draft(self, request, queryset):
        updated = queryset.update(status='draft')
        self.message_user(request, f'{updated} posts were changed to draft.')
    make_draft.short_description = "Mark selected posts as draft"
    
    def make_featured(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} posts were marked as featured.')
    make_featured.short_description = "Mark selected posts as featured"
    
    def remove_featured(self, request, queryset):
        updated = queryset.update(is_featured=False)
        self.message_user(request, f'{updated} posts were removed from featured.')
    remove_featured.short_description = "Remove featured status from selected posts"