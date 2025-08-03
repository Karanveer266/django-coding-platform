from django import template
from django.utils.safestring import mark_safe
from django.utils.html import escape
import re

register = template.Library()

@register.filter
def render_code_blocks(content):
    """
    Convert markdown-style code blocks to HTML with expandable functionality
    """
    if not content:
        return content
    
    # Pattern to match code blocks (```language code ```)
    code_block_pattern = r'```(\w+)?\n(.*?)```'
    
    def replace_code_block(match):
        language = match.group(1) or 'Code'
        code_content = match.group(2).strip()
        
        # Escape HTML in code content
        escaped_code = escape(code_content)
        
        # Always make code blocks expandable regardless of line count
        expandable_class = 'collapsed'
        
        # Generate unique ID
        import hashlib
        code_id = hashlib.md5(code_content.encode()).hexdigest()[:8]
        
        html = f'''
        <div class="code-block-container" data-language="{language.upper()}">
            <div class="code-header">
                <span>{language.upper()}</span>
                <button class="copy-btn" onclick="copyCodeToClipboard('{code_id}')">
                    <i class="fas fa-copy"></i> Copy
                </button>
            </div>
            <div class="code-block {expandable_class}" id="code-block-{code_id}">
                <pre><code>{escaped_code}</code></pre>
            </div>
            <button class="expand-btn" onclick="toggleCodeBlock('{code_id}')">
                <i class="fas fa-expand-arrows-alt"></i> Expand
            </button>
        </div>
        '''
        return html
    
    # Replace code blocks
    content = re.sub(code_block_pattern, replace_code_block, content, flags=re.DOTALL)
    
    # Also handle inline code
    inline_code_pattern = r'`([^`]+)`'
    content = re.sub(inline_code_pattern, r'<code class="inline-code">\1</code>', content)
    
    return mark_safe(content)

@register.filter
def linebreaks_with_code(content):
    """
    Apply linebreaks but preserve code blocks
    """
    content = render_code_blocks(content)
    # Apply basic paragraph formatting while preserving HTML
    paragraphs = content.split('\n\n')
    formatted_paragraphs = []
    
    for paragraph in paragraphs:
        paragraph = paragraph.strip()
        if paragraph:
            # Don't wrap code blocks in p tags
            if '<div class="code-block-container"' in paragraph:
                formatted_paragraphs.append(paragraph)
            else:
                formatted_paragraphs.append(f'<p>{paragraph.replace(chr(10), "<br>")}</p>')
    
    return mark_safe('\n'.join(formatted_paragraphs))