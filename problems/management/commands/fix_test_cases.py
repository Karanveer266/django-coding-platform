from django.core.management.base import BaseCommand
from problems.models import Problem, TestCase

class Command(BaseCommand):
    help = 'Fix test cases for existing problems'

    def handle(self, *args, **options):
        self.stdout.write('Fixing test cases for existing problems...')
        
        # Delete existing placeholder test cases
        TestCase.objects.filter(input_data__startswith='Hidden test case').delete()
        
        # Fix specific problems
        self.fix_two_sum()
        self.fix_fibonacci()
        self.fix_reverse_string()
        
        self.stdout.write(self.style.SUCCESS('Test cases fixed successfully!'))
    
    def fix_two_sum(self):
        """Fix Two Sum problem test cases"""
        problem = Problem.objects.filter(title='Two Sum').first()
        if not problem:
            return
            
        # Update problem sample data
        problem.sample_input = '4\n2 7 11 15\n9'
        problem.sample_output = '0 1'
        problem.save()
        
        # Delete existing test cases and recreate
        TestCase.objects.filter(problem=problem).delete()
        
        # Sample test case
        TestCase.objects.create(
            problem=problem,
            input_data='4\n2 7 11 15\n9',
            expected_output='0 1',
            is_sample=True,
            is_hidden=False,
            points=10
        )
        
        # Additional test cases
        test_cases = [
            ('3\n3 2 4\n6', '1 2'),
            ('2\n3 3\n6', '0 1'),
            ('5\n1 2 3 4 5\n9', '3 4'),
        ]
        
        for input_data, expected_output in test_cases:
            TestCase.objects.create(
                problem=problem,
                input_data=input_data,
                expected_output=expected_output,
                is_sample=False,
                is_hidden=True,
                points=20
            )
        
        self.stdout.write(f'Fixed Two Sum problem with {len(test_cases) + 1} test cases')
    
    def fix_fibonacci(self):
        """Fix Fibonacci problem test cases"""
        problem = Problem.objects.filter(title='Fibonacci Number').first()
        if not problem:
            return
            
        # Update problem sample data
        problem.sample_input = '4'
        problem.sample_output = '3'
        problem.save()
        
        # Delete existing test cases and recreate
        TestCase.objects.filter(problem=problem).delete()
        
        # Sample test case
        TestCase.objects.create(
            problem=problem,
            input_data='4',
            expected_output='3',
            is_sample=True,
            is_hidden=False,
            points=10
        )
        
        # Additional test cases
        test_cases = [
            ('0', '0'),
            ('1', '1'),
            ('2', '1'),
            ('5', '5'),
            ('10', '55'),
        ]
        
        for input_data, expected_output in test_cases:
            TestCase.objects.create(
                problem=problem,
                input_data=input_data,
                expected_output=expected_output,
                is_sample=False,
                is_hidden=True,
                points=15
            )
        
        self.stdout.write(f'Fixed Fibonacci problem with {len(test_cases) + 1} test cases')
    
    def fix_reverse_string(self):
        """Fix Reverse String problem test cases"""
        problem = Problem.objects.filter(title='Reverse String').first()
        if not problem:
            return
            
        # Update problem sample data
        problem.sample_input = 'hello'
        problem.sample_output = 'olleh'
        problem.save()
        
        # Delete existing test cases and recreate
        TestCase.objects.filter(problem=problem).delete()
        
        # Sample test case
        TestCase.objects.create(
            problem=problem,
            input_data='hello',
            expected_output='olleh',
            is_sample=True,
            is_hidden=False,
            points=10
        )
        
        # Additional test cases
        test_cases = [
            ('a', 'a'),
            ('ab', 'ba'),
            ('abcd', 'dcba'),
            ('racecar', 'racecar'),
            ('python', 'nohtyp'),
        ]
        
        for input_data, expected_output in test_cases:
            TestCase.objects.create(
                problem=problem,
                input_data=input_data,
                expected_output=expected_output,
                is_sample=False,
                is_hidden=True,
                points=15
            )
        
        self.stdout.write(f'Fixed Reverse String problem with {len(test_cases) + 1} test cases')