from django.core.management.base import BaseCommand
from django.db import transaction
from problems.models import Problem
from mcq_generation.models import MCQSet, MCQ
from learning_sessions.views import generate_sample_mcqs

class Command(BaseCommand):
    help = 'Generate MCQs for all problems that don\'t have them'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force regenerate MCQs even if they already exist',
        )
    
    def handle(self, *args, **options):
        force = options['force']
        
        problems = Problem.objects.filter(is_active=True)
        
        if not force:
            # Only get problems without MCQs
            existing_mcq_problems = MCQSet.objects.filter(is_active=True).values_list('problem_id', flat=True)
            problems = problems.exclude(id__in=existing_mcq_problems)
        
        total_problems = problems.count()
        
        if total_problems == 0:
            if force:
                self.stdout.write(self.style.WARNING('No problems found to process.'))
            else:
                self.stdout.write(self.style.SUCCESS('All problems already have MCQs!'))
            return
        
        self.stdout.write(f'Generating MCQs for {total_problems} problems...')
        
        success_count = 0
        error_count = 0
        
        for problem in problems:
            try:
                with transaction.atomic():
                    if force:
                        # Deactivate existing MCQ sets
                        MCQSet.objects.filter(problem=problem).update(is_active=False)
                    
                    # Create new MCQ set
                    mcq_set = MCQSet.objects.create(
                        problem=problem,
                        total_questions=5
                    )
                    
                    # Generate sample MCQs
                    sample_questions = generate_sample_mcqs(problem)
                    
                    for i, mcq_data in enumerate(sample_questions):
                        MCQ.objects.create(
                            mcq_set=mcq_set,
                            sequence_order=i + 1,
                            **mcq_data
                        )
                    
                    success_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ Generated MCQs for: {problem.title}')
                    )
                    
            except Exception as e:
                error_count += 1
                self.stdout.write(
                    self.style.ERROR(f'✗ Failed to generate MCQs for {problem.title}: {str(e)}')
                )
        
        self.stdout.write('\n' + '='*50)
        self.stdout.write(f'Summary:')
        self.stdout.write(f'  Successfully generated: {success_count}')
        self.stdout.write(f'  Errors: {error_count}')
        self.stdout.write(f'  Total processed: {success_count + error_count}')
        
        if success_count > 0:
            self.stdout.write(self.style.SUCCESS('\nMCQ generation completed successfully!'))