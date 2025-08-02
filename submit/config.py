"""
Dynamic configuration for the code judge system
"""
from django.conf import settings
import os

class JudgeConfig:
    """Configuration class for dynamic judge settings"""
    
    # Default values that can be overridden
    DEFAULT_TIME_LIMIT = 5  # seconds
    DEFAULT_MEMORY_LIMIT = "128m"  # megabytes
    DEFAULT_COMPILE_TIMEOUT = 15  # seconds for compilation
    
    # Language-specific overrides
    LANGUAGE_CONFIGS = {
        'python': {
            'time_limit': 10,  # Python might need more time
            'memory_limit': "256m",
            'compile_timeout': None
        },
        'py': {
            'time_limit': 10,
            'memory_limit': "256m", 
            'compile_timeout': None
        },
        'cpp': {
            'time_limit': 5,
            'memory_limit': "128m",
            'compile_timeout': 15
        },
        'java': {
            'time_limit': 8,
            'memory_limit': "512m",  # Java needs more memory
            'compile_timeout': 20
        },
        'javascript': {
            'time_limit': 10,
            'memory_limit': "256m",
            'compile_timeout': None
        }
    }
    
    @classmethod
    def get_time_limit(cls, language=None, problem_time_limit=None):
        """Get time limit for a language, with problem override"""
        if problem_time_limit:
            return problem_time_limit
            
        if language and language.lower() in cls.LANGUAGE_CONFIGS:
            return cls.LANGUAGE_CONFIGS[language.lower()].get('time_limit', cls.DEFAULT_TIME_LIMIT)
        
        return getattr(settings, 'JUDGE_DEFAULT_TIME_LIMIT', cls.DEFAULT_TIME_LIMIT)
    
    @classmethod
    def get_memory_limit(cls, language=None, problem_memory_limit=None):
        """Get memory limit for a language, with problem override"""
        if problem_memory_limit:
            return problem_memory_limit
            
        if language and language.lower() in cls.LANGUAGE_CONFIGS:
            return cls.LANGUAGE_CONFIGS[language.lower()].get('memory_limit', cls.DEFAULT_MEMORY_LIMIT)
        
        return getattr(settings, 'JUDGE_DEFAULT_MEMORY_LIMIT', cls.DEFAULT_MEMORY_LIMIT)
    
    @classmethod
    def get_compile_timeout(cls, language=None):
        """Get compilation timeout for a language"""
        if language and language.lower() in cls.LANGUAGE_CONFIGS:
            timeout = cls.LANGUAGE_CONFIGS[language.lower()].get('compile_timeout')
            if timeout is not None:
                return timeout
        
        return getattr(settings, 'JUDGE_COMPILE_TIMEOUT', cls.DEFAULT_COMPILE_TIMEOUT)
    
    @classmethod
    def memory_limit_to_bytes(cls, memory_str):
        """Convert memory limit string (e.g., '128m') to bytes"""
        if isinstance(memory_str, (int, float)):
            return int(memory_str)
        
        memory_str = str(memory_str).lower()
        if memory_str.endswith('m'):
            return int(memory_str[:-1]) * 1024 * 1024
        elif memory_str.endswith('g'):
            return int(memory_str[:-1]) * 1024 * 1024 * 1024
        elif memory_str.endswith('k'):
            return int(memory_str[:-1]) * 1024
        else:
            return int(memory_str)  # Assume bytes
    
    @classmethod
    def is_contest_mode_enabled(cls):
        """Check if contest mode is enabled"""
        return getattr(settings, 'CONTEST_MODE_ENABLED', False)
    
    @classmethod
    def get_supported_languages(cls):
        """Get list of supported programming languages"""
        default_languages = ['python', 'py', 'cpp', 'java', 'javascript']
        return getattr(settings, 'JUDGE_SUPPORTED_LANGUAGES', default_languages)