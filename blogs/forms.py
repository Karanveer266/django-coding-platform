from django import forms
from django.utils.text import slugify
from .models import BlogPost, Comment, Category, Tag

class BlogPostForm(forms.ModelForm):
    tags = forms.CharField(
        max_length=255, 
        required=False,
        help_text="Enter tags separated by commas (e.g., python, web development, tutorial)"
    )
    
    class Meta:
        model = BlogPost
        fields = [
            'title', 'content', 'excerpt', 'featured_image', 
            'category', 'tags', 'status', 'is_featured',
            'meta_description', 'meta_keywords'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'Enter blog post title'
            }),
            'content': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500',
                'rows': 15,
                'placeholder': 'Write your blog post content here...'
            }),
            'excerpt': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500',
                'rows': 3,
                'placeholder': 'Brief description of your post (optional)'
            }),
            'featured_image': forms.ClearableFileInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500'
            }),
            'category': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500'
            }),
            'status': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500'
            }),
            'meta_description': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'SEO meta description (optional)'
            }),
            'meta_keywords': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'SEO keywords separated by commas (optional)'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Populate tags field if editing existing post
        if self.instance and self.instance.pk:
            tag_names = [tag.name for tag in self.instance.tags.all()]
            self.fields['tags'].initial = ', '.join(tag_names)
    
    def clean_title(self):
        title = self.cleaned_data['title']
        slug = slugify(title)
        
        # Check for duplicate slugs
        queryset = BlogPost.objects.filter(slug=slug)
        if self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)
        
        if queryset.exists():
            raise forms.ValidationError("A post with this title already exists. Please choose a different title.")
        
        return title
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        if commit:
            instance.save()
            
            # Handle tags
            tags_input = self.cleaned_data.get('tags', '')
            if tags_input:
                tag_names = [name.strip() for name in tags_input.split(',') if name.strip()]
                tags = []
                for tag_name in tag_names:
                    tag, created = Tag.objects.get_or_create(
                        name=tag_name.lower(),
                        defaults={'slug': slugify(tag_name)}
                    )
                    tags.append(tag)
                instance.tags.set(tags)
            else:
                instance.tags.clear()
        
        return instance

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500',
                'rows': 4,
                'placeholder': 'Write your comment here...'
            })
        }
    
    def clean_content(self):
        content = self.cleaned_data['content']
        if len(content.strip()) < 10:
            raise forms.ValidationError("Comment must be at least 10 characters long.")
        return content

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description', 'color']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'Category name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500',
                'rows': 3,
                'placeholder': 'Category description'
            }),
            'color': forms.TextInput(attrs={
                'type': 'color',
                'class': 'w-full h-10 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500'
            })
        }