from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import random

from problems.models import Problem, TestCase
from blogs.models import BlogPost, Category, Tag as BlogTag
from submit.models import Submission
from learning_sessions.models import LearningSession
from mcq_generation.models import MCQSet, MCQ

User = get_user_model()

class Command(BaseCommand):
    help = 'Populate the database with sample data for testing and demonstration'

    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            type=int,
            default=10,
            help='Number of sample users to create',
        )
        parser.add_argument(
            '--problems',
            type=int,
            default=20,
            help='Number of sample problems to create',
        )
        parser.add_argument(
            '--blogs',
            type=int,
            default=15,
            help='Number of sample blog posts to create',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting data population...'))
        
        # Create users
        self.create_users(options['users'])
        
        # Create problems
        self.create_problems(options['problems'])
        
        # Create blog categories and tags
        self.create_blog_categories_and_tags()
        
        # Create blog posts
        self.create_blog_posts(options['blogs'])
        
        # Create sample submissions
        self.create_sample_submissions()
        
        # Create learning sessions
        self.create_learning_sessions()
        
        self.stdout.write(self.style.SUCCESS('Data population completed successfully!'))

    def create_users(self, count):
        self.stdout.write('Creating sample users...')
        
        # Create admin user if doesn't exist
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_superuser(
                username='admin',
                email='admin@codeplatform.com',
                password='admin123',
                first_name='Admin',
                last_name='User'
            )
            admin.bio = 'Platform administrator and coding enthusiast.'
            admin.location = 'San Francisco, CA'
            admin.save()
            self.stdout.write(f'Created admin user')

        # Sample user data
        sample_users = [
            {
                'username': 'alice_coder',
                'email': 'alice@example.com',
                'first_name': 'Alice',
                'last_name': 'Johnson',
                'bio': 'Software engineer passionate about algorithms and data structures.',
                'location': 'New York, NY',
                'github_username': 'alice-codes',
                'preferred_language': 'py'
            },
            {
                'username': 'bob_pythonista',
                'email': 'bob@example.com',
                'first_name': 'Bob',
                'last_name': 'Smith',
                'bio': 'Python developer and machine learning enthusiast.',
                'location': 'Austin, TX',
                'github_username': 'bob-ml',
                'preferred_language': 'py'
            },
            {
                'username': 'charlie_cpp',
                'email': 'charlie@example.com',
                'first_name': 'Charlie',
                'last_name': 'Brown',
                'bio': 'C++ expert focusing on competitive programming.',
                'location': 'Seattle, WA',
                'github_username': 'charlie-cpp',
                'preferred_language': 'cpp'
            }
        ]
        
        for i, user_data in enumerate(sample_users):
            if not User.objects.filter(username=user_data['username']).exists():
                user = User.objects.create_user(
                    username=user_data['username'],
                    email=user_data['email'],
                    password='password123',
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name']
                )
                
                # Set additional fields
                for field, value in user_data.items():
                    if field not in ['username', 'email', 'first_name', 'last_name']:
                        setattr(user, field, value)
                
                user.save()
                self.stdout.write(f'Created user: {user.username}')
        
        # Create additional random users
        for i in range(len(sample_users), count):
            username = f'user_{i+1}'
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(
                    username=username,
                    email=f'{username}@example.com',
                    password='password123',
                    first_name=f'User',
                    last_name=f'{i+1}'
                )
                user.bio = f'Coding enthusiast #{i+1}'
                user.preferred_language = random.choice(['py', 'cpp', 'java'])
                user.save()

    def create_problems(self, count):
        self.stdout.write('Creating sample problems...')
        
        admin_user = User.objects.filter(is_superuser=True).first()
        
        sample_problems = [
            {
                'title': 'Two Sum',
                'description': '''Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.

You may assume that each input would have exactly one solution, and you may not use the same element twice.

You can return the answer in any order.''',
                'difficulty': 'easy',
                'problem_type': 'algorithm',
                'input_format': 'First line contains n, the number of elements.\nSecond line contains n space-separated integers.\nThird line contains the target integer.',
                'output_format': 'Two space-separated integers representing the indices.',
                'constraints': '2 ≤ n ≤ 10^4\n-10^9 ≤ nums[i] ≤ 10^9\n-10^9 ≤ target ≤ 10^9',
                'sample_input': '4\n2 7 11 15\n9',
                'sample_output': '0 1',
            },
            {
                'title': 'Reverse String',
                'description': '''Write a function that reverses a string. The input string is given as an array of characters s.

You must do this by modifying the input array in-place with O(1) extra memory.''',
                'difficulty': 'easy',
                'problem_type': 'algorithm',
                'input_format': 'A string s consisting of printable ASCII characters.',
                'output_format': 'The reversed string.',
                'constraints': '1 ≤ s.length ≤ 10^5',
                'sample_input': 'hello',
                'sample_output': 'olleh',
            },
            {
                'title': 'Fibonacci Number',
                'description': '''The Fibonacci numbers, commonly denoted F(n) form a sequence, called the Fibonacci sequence, such that each number is the sum of the two preceding ones, starting from 0 and 1.

Given n, calculate F(n).''',
                'difficulty': 'easy',
                'problem_type': 'algorithm',
                'input_format': 'A single integer n.',
                'output_format': 'The nth Fibonacci number.',
                'constraints': '0 ≤ n ≤ 30',
                'sample_input': '4',
                'sample_output': '3',
            },
            {
                'title': 'Binary Tree Inorder Traversal',
                'description': '''Given the root of a binary tree, return the inorder traversal of its nodes' values.''',
                'difficulty': 'medium',
                'problem_type': 'algorithm',
                'input_format': 'The root of a binary tree.',
                'output_format': 'A list of integers representing the inorder traversal.',
                'constraints': 'The number of nodes in the tree is in the range [0, 100].\n-100 ≤ Node.val ≤ 100',
                'sample_input': '[1,null,2,3]',
                'sample_output': '[1,3,2]',
            },
            {
                'title': 'Longest Palindromic Substring',
                'description': '''Given a string s, return the longest palindromic substring in s.''',
                'difficulty': 'medium',
                'problem_type': 'algorithm',
                'input_format': 'A string s.',
                'output_format': 'The longest palindromic substring.',
                'constraints': '1 ≤ s.length ≤ 1000\ns consist of only digits and English letters.',
                'sample_input': 'babad',
                'sample_output': 'bab',
            }
        ]
        
        for problem_data in sample_problems:
            if not Problem.objects.filter(title=problem_data['title']).exists():
                problem = Problem.objects.create(
                    created_by=admin_user,
                    **problem_data
                )
                
                # Create test cases
                self.create_test_cases_for_problem(problem)
                
                self.stdout.write(f'Created problem: {problem.title}')
        
        # Create additional random problems
        difficulties = ['easy', 'medium', 'hard']
        problem_types = ['algorithm', 'data_structure', 'math']
        
        for i in range(len(sample_problems), count):
            title = f'Sample Problem {i+1}'
            if not Problem.objects.filter(title=title).exists():
                problem = Problem.objects.create(
                    title=title,
                    description=f'This is a sample problem #{i+1} for testing purposes. Solve this problem using appropriate algorithms and data structures.',
                    difficulty=random.choice(difficulties),
                    problem_type=random.choice(problem_types),
                    input_format='Input format for the problem.',
                    output_format='Output format for the problem.',
                    constraints='Constraints for the problem.',
                    sample_input='Sample input',
                    sample_output='Sample output',
                    created_by=admin_user
                )
                
                
                # Create test cases
                self.create_test_cases_for_problem(problem)

    def create_test_cases_for_problem(self, problem):
        """Create sample test cases for a problem"""
        # Create sample test case
        TestCase.objects.create(
            problem=problem,
            input_data=problem.sample_input,
            expected_output=problem.sample_output,
            is_sample=True,
            is_hidden=False,
            points=10
        )
        
        # Create additional hidden test cases
        for i in range(3):
            TestCase.objects.create(
                problem=problem,
                input_data=f'Hidden test case {i+1} input',
                expected_output=f'Hidden test case {i+1} output',
                is_sample=False,
                is_hidden=True,
                points=20
            )

    def create_blog_categories_and_tags(self):
        self.stdout.write('Creating blog categories and tags...')
        
        categories = [
            'Algorithms', 'Data Structures', 'Programming Languages',
            'Software Engineering', 'Career Advice', 'Tutorials'
        ]
        
        for cat_name in categories:
            category, created = Category.objects.get_or_create(
                name=cat_name,
                defaults={'description': f'Posts about {cat_name.lower()}'}
            )
            if created:
                self.stdout.write(f'Created category: {cat_name}')
        
        blog_tags = [
            'Python', 'JavaScript', 'C++', 'Java', 'Algorithm',
            'Tutorial', 'Beginner', 'Advanced', 'Tips', 'Best Practices'
        ]
        
        for tag_name in blog_tags:
            tag, created = BlogTag.objects.get_or_create(name=tag_name)
            if created:
                self.stdout.write(f'Created blog tag: {tag_name}')

    def create_blog_posts(self, count):
        self.stdout.write('Creating sample blog posts...')
        
        users = list(User.objects.all())
        categories = list(Category.objects.all())
        tags = list(BlogTag.objects.all())
        
        sample_posts = [
            {
                'title': 'Getting Started with Dynamic Programming',
                'content': '''Dynamic Programming is one of the most important algorithmic techniques in competitive programming. In this post, we'll explore the fundamentals of DP and how to approach DP problems systematically.

## What is Dynamic Programming?

Dynamic Programming is an algorithmic paradigm that solves complex problems by breaking them down into simpler subproblems. It is applicable to problems exhibiting the properties of overlapping subproblems and optimal substructure.

## Key Concepts

1. **Overlapping Subproblems**: The same subproblems are solved multiple times
2. **Optimal Substructure**: An optimal solution contains optimal solutions to subproblems

## Common DP Patterns

### 1. Linear DP
Problems where the state depends on previous states in a linear fashion.

### 2. Grid DP
Problems involving 2D grids where you can move in certain directions.

### 3. Interval DP
Problems where you break intervals into smaller intervals.

## Practice Problems

1. Fibonacci Numbers
2. Longest Common Subsequence
3. 0/1 Knapsack
4. Edit Distance

Happy coding!''',
                'excerpt': 'Learn the fundamentals of Dynamic Programming and master this essential algorithmic technique.',
                'category': 'Algorithms',
                'tag_names': ['Algorithm', 'Tutorial', 'Advanced'],
                'is_featured': True
            },
            {
                'title': 'Top 10 Python Tips for Competitive Programming',
                'content': '''Python is a great language for competitive programming due to its simplicity and powerful built-in functions. Here are my top 10 tips to make your Python code faster and more efficient.

## 1. Use Built-in Functions

Python's built-in functions are implemented in C and are much faster than writing your own implementations.

```python
# Use sum() instead of manual loops
total = sum(numbers)

# Use max() and min()
maximum = max(numbers)
minimum = min(numbers)
```

## 2. List Comprehensions

List comprehensions are not only more readable but also faster than traditional loops.

```python
# Instead of:
squares = []
for x in range(10):
    squares.append(x**2)

# Use:
squares = [x**2 for x in range(10)]
```

## 3. Use collections.Counter

For counting elements, Counter is much more efficient than manual counting.

```python
from collections import Counter
count = Counter(items)
```

Continue reading for more tips...''',
                'excerpt': 'Boost your competitive programming performance with these essential Python tips and tricks.',
                'category': 'Programming Languages',
                'tag_names': ['Python', 'Tips', 'Beginner'],
                'is_featured': False
            }
        ]
        
        for post_data in sample_posts:
            if not BlogPost.objects.filter(title=post_data['title']).exists():
                tag_names = post_data.pop('tag_names')
                category_name = post_data.pop('category')
                
                category = Category.objects.get(name=category_name)
                author = random.choice(users)
                
                post = BlogPost.objects.create(
                    author=author,
                    category=category,
                    status='published',
                    published_date=timezone.now() - timedelta(days=random.randint(1, 30)),
                    **post_data
                )
                
                # Add tags
                for tag_name in tag_names:
                    tag = BlogTag.objects.get(name=tag_name)
                    post.tags.add(tag)
                
                self.stdout.write(f'Created blog post: {post.title}')
        
        # Create additional random posts
        for i in range(len(sample_posts), count):
            title = f'Sample Blog Post {i+1}'
            if not BlogPost.objects.filter(title=title).exists():
                post = BlogPost.objects.create(
                    title=title,
                    content=f'This is sample blog post content #{i+1}. It contains information about programming and algorithms.',
                    excerpt=f'Sample excerpt for blog post #{i+1}.',
                    author=random.choice(users),
                    category=random.choice(categories),
                    status='published',
                    published_date=timezone.now() - timedelta(days=random.randint(1, 60))
                )
                
                # Add random tags
                random_tags = random.sample(tags, random.randint(1, 3))
                for tag in random_tags:
                    post.tags.add(tag)

    def create_sample_submissions(self):
        self.stdout.write('Creating sample submissions...')
        
        users = list(User.objects.filter(is_superuser=False))
        problems = list(Problem.objects.all())
        
        if not users or not problems:
            return
        
        # Create some sample submissions
        for _ in range(50):
            user = random.choice(users)
            problem = random.choice(problems)
            
            # Skip if submission already exists
            if Submission.objects.filter(user=user, problem=problem).exists():
                continue
            
            status = random.choices(
                ['ACCEPTED', 'WRONG_ANSWER', 'TIME_LIMIT_EXCEEDED', 'RUNTIME_ERROR'],
                weights=[40, 30, 20, 10]
            )[0]
            
            submission = Submission.objects.create(
                user=user,
                problem=problem,
                code=f'# Sample solution for {problem.title}\ndef solve():\n    pass\n\nsolve()',
                language=random.choice(['py', 'cpp', 'java']),
                status=status,
                total_test_cases=4,
                passed_test_cases=4 if status == 'ACCEPTED' else random.randint(0, 3),
                max_execution_time=random.uniform(0.1, 2.0),
                score=100 if status == 'ACCEPTED' else random.uniform(0, 75),
                submitted_at=timezone.now() - timedelta(days=random.randint(1, 30))
            )
            
            # Update problem statistics
            problem.total_attempts += 1
            if status == 'ACCEPTED':
                problem.successful_completions += 1
            problem.save()

    def create_learning_sessions(self):
        self.stdout.write('Creating sample learning sessions...')
        
        users = list(User.objects.filter(is_superuser=False))
        problems = list(Problem.objects.all()[:5])  # Use first 5 problems
        
        if not users or not problems:
            return
        
        for user in users[:3]:  # Create sessions for first 3 users
            for problem in problems[:2]:  # 2 problems each
                # Skip if session already exists
                if LearningSession.objects.filter(user=user, problem=problem).exists():
                    continue
                
                session = LearningSession.objects.create(
                    user=user,
                    problem=problem,
                    status=random.choice(['completed', 'in_progress', 'mcq_ready']),
                    current_mcq_index=random.randint(3, 5),
                    total_mcqs=5,
                    correct_answers=random.randint(2, 5),
                    started_at=timezone.now() - timedelta(days=random.randint(1, 7))
                )
                
                if session.status == 'completed':
                    session.completed_at = session.started_at + timedelta(minutes=random.randint(10, 30))
                    session.save()