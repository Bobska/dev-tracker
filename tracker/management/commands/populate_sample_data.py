"""
FamilyHub Development Tracker - Populate Sample Data

Management command to create realistic sample data for the FamilyHub project.
Creates projects, applications, tasks, artifacts, and decisions for development and testing.

Usage:
    python manage.py populate_sample_data
    python manage.py populate_sample_data --reset  # Delete existing data first
    python manage.py populate_sample_data --minimal  # Create minimal dataset
"""
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime, timedelta
import random

from tracker.models import Project, Application, Artifact, Task, Decision, Integration

User = get_user_model()


class Command(BaseCommand):
    help = 'Populate the database with sample FamilyHub development data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Delete all existing data before creating sample data',
        )
        parser.add_argument(
            '--minimal',
            action='store_true',
            help='Create minimal dataset for testing',
        )
        parser.add_argument(
            '--user',
            type=str,
            default='admin',
            help='Username of the project owner (default: admin)',
        )

    def handle(self, *args, **options):
        if options['reset']:
            self.stdout.write(self.style.WARNING('Deleting existing data...'))
            self.delete_existing_data()

        try:
            # Get or create the project owner
            owner_username = options['user']
            try:
                owner = User.objects.get(username=owner_username)
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'User "{owner_username}" not found. Creating user...')
                )
                owner = User.objects.create_user(
                    username=owner_username,
                    email=f'{owner_username}@familyhub.dev',
                    password='password123',
                    first_name='Project',
                    last_name='Owner'
                )
                self.stdout.write(
                    self.style.SUCCESS(f'Created user: {owner_username}')
                )

            if options['minimal']:
                self.create_minimal_data(owner)
            else:
                self.create_comprehensive_data(owner)

            self.stdout.write(
                self.style.SUCCESS('Successfully populated sample data!')
            )

        except Exception as e:
            raise CommandError(f'Error creating sample data: {str(e)}')

    def delete_existing_data(self):
        """Delete all existing tracker data."""
        models_to_delete = [Integration, Decision, Artifact, Task, Application, Project]
        
        for model in models_to_delete:
            count = model.objects.count()
            if count > 0:
                model.objects.all().delete()
                self.stdout.write(f'Deleted {count} {model.__name__} records')

    def create_minimal_data(self, owner):
        """Create minimal dataset for basic testing."""
        self.stdout.write('Creating minimal sample data...')

        # Create FamilyHub main project
        project = Project.objects.create(
            name='FamilyHub',
            description='Integrated family management platform combining multiple Django applications.',
            status='active',
            owner=owner,
            start_date=timezone.now().date() - timedelta(days=30),
            target_date=timezone.now().date() + timedelta(days=90),
        )

        # Create core applications
        timesheet_app = Application.objects.create(
            project=project,
            name='Timesheet Tracker',
            description='Track work hours and calculate payments for multiple jobs.',
            complexity='medium',
            status='development',
            estimated_weeks=8,
            features=['Time tracking', 'Job management', 'Payment calculation'],
        )

        daycare_app = Application.objects.create(
            project=project,
            name='Daycare Invoice Tracker',
            description='Track daycare payments and generate monthly reports.',
            complexity='simple',
            status='production',
            estimated_weeks=4,
            features=['Invoice tracking', 'Payment history', 'Monthly reports'],
        )

        # Create sample tasks
        tasks_data = [
            {
                'title': 'Implement time entry validation',
                'description': 'Add validation to prevent overlapping time entries',
                'application': timesheet_app,
                'status': 'in_progress',
                'priority': 'high'
            },
            {
                'title': 'Create job management interface',
                'description': 'CRUD interface for managing job information',
                'application': timesheet_app,
                'status': 'todo',
                'priority': 'medium'
            },
            {
                'title': 'Deploy daycare app to production',
                'description': 'Configure production environment and deploy',
                'application': daycare_app,
                'status': 'completed',
                'priority': 'high'
            },
        ]

        for task_data in tasks_data:
            Task.objects.create(
                project=project,
                **task_data,
                due_date=timezone.now().date() + timedelta(days=random.randint(1, 30)),
            )

        self.stdout.write(f'Created minimal data:')
        self.stdout.write(f'  - 1 project: {project.name}')
        self.stdout.write(f'  - 2 applications')
        self.stdout.write(f'  - 3 tasks')

    def create_comprehensive_data(self, owner):
        """Create comprehensive dataset with full FamilyHub project structure."""
        self.stdout.write('Creating comprehensive sample data...')

        # Create main FamilyHub project
        familyhub_project = Project.objects.create(
            name='FamilyHub',
            description='Unified family management platform integrating multiple Django applications for comprehensive household management.',
            status='active',
            owner=owner,
            start_date=timezone.now().date() - timedelta(days=90),
            target_date=timezone.now().date() + timedelta(days=180),
        )

        # Create applications with detailed information
        applications_data = [
            {
                'name': 'Timesheet Tracker',
                'description': 'Track work hours across multiple jobs with automatic payment calculations and detailed reporting.',
                'status': 'development',
                'features': [
                    'Multi-job time tracking',
                    'Overlap validation',
                    'Payment calculation',
                    'Weekly/monthly reports',
                    'Break time management',
                    'Export to PDF/Excel'
                ],
                'tech_stack': ['Django 5.2', 'SQLite', 'Bootstrap 5', 'Chart.js', 'Python 3.10'],
                'version': '1.2.0',
                'repository_url': 'https://github.com/Bobska/timesheet-tracker',
            },
            {
                'name': 'Daycare Invoice Tracker',
                'description': 'Complete daycare payment management with invoice tracking and financial reporting.',
                'status': 'production',
                'features': [
                    'Invoice management',
                    'Payment tracking',
                    'Monthly summaries',
                    'Tax reporting',
                    'Provider management',
                    'Receipt storage'
                ],
                'tech_stack': ['Django 5.2', 'PostgreSQL', 'Bootstrap 5', 'Chart.js', 'Redis'],
                'version': '2.3.1',
                'repository_url': 'https://github.com/Bobska/daycare-tracker',
            },
            {
                'name': 'AutoCraftCV',
                'description': 'Automated CV generation and job application tracking system.',
                'status': 'production',
                'features': [
                    'CV template management',
                    'Auto-generation',
                    'Job application tracking',
                    'Company research',
                    'Interview scheduling',
                    'Document storage'
                ],
                'tech_stack': ['Django 5.2', 'PostgreSQL', 'React', 'Docker', 'Celery'],
                'version': '3.0.2',
                'repository_url': 'https://github.com/Bobska/autocraftcv',
            },
            {
                'name': 'Employment History',
                'description': 'Comprehensive employment history tracking with performance metrics.',
                'status': 'planning',
                'features': [
                    'Employment timeline',
                    'Performance tracking',
                    'Skills development',
                    'Reference management',
                    'Career progression analysis'
                ],
                'tech_stack': ['Django 5.2', 'PostgreSQL', 'Vue.js', 'D3.js'],
                'version': '0.1.0',
            },
            {
                'name': 'Upcoming Payments',
                'description': 'Payment scheduling and reminder system for all recurring expenses.',
                'status': 'planning',
                'features': [
                    'Payment scheduling',
                    'Automatic reminders',
                    'Category management',
                    'Budget tracking',
                    'Bank integration'
                ],
                'tech_stack': ['Django 5.2', 'PostgreSQL', 'Celery', 'Bootstrap 5'],
                'version': '0.1.0',
            },
            {
                'name': 'Credit Card Management',
                'description': 'Credit card tracking with spending analysis and fraud detection.',
                'status': 'planning',
                'features': [
                    'Transaction tracking',
                    'Spending analysis',
                    'Credit utilization monitoring',
                    'Fraud alerts',
                    'Payment optimization'
                ],
                'tech_stack': ['Django 5.2', 'PostgreSQL', 'Machine Learning', 'API Integration'],
                'version': '0.1.0',
            },
            {
                'name': 'Household Budget',
                'description': 'Complete household budget management with predictive analytics.',
                'status': 'planning',
                'features': [
                    'Budget creation',
                    'Expense tracking',
                    'Income forecasting',
                    'Savings goals',
                    'Financial reports'
                ],
                'tech_stack': ['Django 5.2', 'PostgreSQL', 'Chart.js', 'Machine Learning'],
                'version': '0.1.0',
            },
        ]

        # Create applications
        applications = []
        for app_data in applications_data:
            app = Application.objects.create(
                project=familyhub_project,
                **app_data
            )
            applications.append(app)
            self.stdout.write(f'Created application: {app.name}')

        # Create detailed tasks for each application
        self.create_detailed_tasks(familyhub_project, applications)

        # Create artifacts for applications
        self.create_sample_artifacts(applications)

        # Create architecture decisions
        self.create_architecture_decisions(familyhub_project)

        # Create integration plans
        self.create_integration_plans(applications)

        # Display summary
        self.display_summary(familyhub_project)

    def create_detailed_tasks(self, project, applications):
        """Create detailed tasks for each application."""
        task_templates = {
            'development': [
                ('Setup project structure', 'Initialize Django project with proper directory structure', 'completed', 'medium'),
                ('Create models and database schema', 'Design and implement database models', 'completed', 'high'),
                ('Implement core views', 'Create main application views and logic', 'in_progress', 'high'),
                ('Design user interface', 'Create responsive UI using Bootstrap 5', 'in_progress', 'medium'),
                ('Add form validation', 'Implement client and server-side validation', 'todo', 'medium'),
                ('Write unit tests', 'Create comprehensive test suite', 'todo', 'high'),
                ('Add user authentication', 'Implement login/logout functionality', 'todo', 'high'),
                ('Performance optimization', 'Optimize database queries and caching', 'todo', 'low'),
            ],
            'production': [
                ('Production deployment', 'Deploy application to production environment', 'completed', 'high'),
                ('Monitor application performance', 'Set up monitoring and alerting', 'completed', 'medium'),
                ('Bug fixes and maintenance', 'Ongoing maintenance and bug resolution', 'in_progress', 'medium'),
                ('Feature enhancement requests', 'Implement user-requested features', 'todo', 'low'),
                ('Security audit', 'Conduct security review and updates', 'todo', 'high'),
                ('Database backup strategy', 'Implement automated backup system', 'completed', 'high'),
            ],
            'planning': [
                ('Requirements gathering', 'Define functional and technical requirements', 'in_progress', 'high'),
                ('Architecture design', 'Design system architecture and data flow', 'todo', 'high'),
                ('Technology stack selection', 'Choose appropriate technologies and frameworks', 'todo', 'medium'),
                ('UI/UX mockups', 'Create user interface mockups and wireframes', 'todo', 'medium'),
                ('Project timeline', 'Create detailed development timeline', 'todo', 'medium'),
                ('Resource allocation', 'Determine development resources needed', 'todo', 'low'),
            ]
        }

        for app in applications:
            templates = task_templates.get(app.status, task_templates['development'])
            
            for title, description, status, priority in templates:
                # Create due dates based on status
                if status == 'completed':
                    due_date = timezone.now().date() - timedelta(days=random.randint(1, 30))
                elif status == 'in_progress':
                    due_date = timezone.now().date() + timedelta(days=random.randint(1, 14))
                else:  # todo
                    due_date = timezone.now().date() + timedelta(days=random.randint(15, 60))

                Task.objects.create(
                    project=project,
                    application=app,
                    title=f'{app.name}: {title}',
                    description=description,
                    status=status,
                    priority=priority,
                    due_date=due_date,
                )

    def create_sample_artifacts(self, applications):
        """Create sample artifacts for applications."""
        artifact_templates = [
            ('Requirements Document', 'document', 'complete', 'Comprehensive functional and technical requirements'),
            ('Architecture Diagram', 'design', 'complete', 'System architecture and component relationships'),
            ('Database Schema', 'code', 'complete', 'Database design and entity relationships'),
            ('API Documentation', 'document', 'in-progress', 'RESTful API endpoint documentation'),
            ('User Manual', 'document', 'draft', 'End-user documentation and guides'),
            ('Test Plan', 'document', 'draft', 'Testing strategy and test cases'),
            ('Deployment Guide', 'document', 'in-progress', 'Production deployment instructions'),
        ]

        for app in applications[:3]:  # Only create artifacts for first 3 apps
            for name, artifact_type, status, description in artifact_templates:
                Artifact.objects.create(
                    application=app,
                    name=f'{app.name} - {name}',
                    artifact_type=artifact_type,
                    status=status,
                    description=description,
                    version='1.0',
                    content=f'Sample content for {name} of {app.name}.',
                )

    def create_architecture_decisions(self, project):
        """Create sample architecture decisions."""
        decisions_data = [
            {
                'title': 'Choose Django as Primary Framework',
                'description': 'After evaluating Flask, FastAPI, and Django, we decided on Django for its comprehensive feature set, admin interface, and ORM capabilities.',
                'rationale': 'Django provides built-in authentication, admin interface, and ORM which will accelerate development. The project complexity justifies the framework overhead.',
                'status': 'approved',
                'impact': 'All applications will use Django 5.2+ with consistent project structure and shared components.',
            },
            {
                'title': 'Implement Microservices Architecture',
                'description': 'Structure FamilyHub as separate Django applications that can be developed and deployed independently.',
                'rationale': 'Allows for independent development cycles, easier maintenance, and selective deployment of applications.',
                'status': 'approved',
                'impact': 'Each family management application (timesheet, daycare, etc.) will be a separate Django app with shared authentication.',
            },
            {
                'title': 'Use PostgreSQL for Production Database',
                'description': 'Standardize on PostgreSQL for all production deployments while using SQLite for development.',
                'rationale': 'PostgreSQL provides better performance, JSON field support, and advanced features needed for complex queries.',
                'status': 'approved',
                'impact': 'All applications must be designed to work with both SQLite (dev) and PostgreSQL (prod).',
            },
            {
                'title': 'Implement Shared Authentication System',
                'description': 'Create a unified authentication system across all FamilyHub applications.',
                'rationale': 'Users should be able to access all family management tools with a single login.',
                'status': 'in-review',
                'impact': 'Requires OAuth2 or JWT implementation for cross-application authentication.',
            },
            {
                'title': 'Bootstrap 5 for UI Consistency',
                'description': 'Standardize on Bootstrap 5 for all user interface components across applications.',
                'rationale': 'Ensures consistent look and feel, responsive design, and faster development with pre-built components.',
                'status': 'approved',
                'impact': 'All templates must use Bootstrap 5 classes and follow established design patterns.',
            },
        ]

        for decision_data in decisions_data:
            Decision.objects.create(
                project=project,
                **decision_data
            )

    def create_integration_plans(self, applications):
        """Create integration plans between applications."""
        # Get production and development apps for integration
        timesheet_app = next((app for app in applications if 'Timesheet' in app.name), None)
        daycare_app = next((app for app in applications if 'Daycare' in app.name), None)
        autocraftcv_app = next((app for app in applications if 'AutoCraftCV' in app.name), None)

        if timesheet_app and daycare_app:
            Integration.objects.create(
                from_application=timesheet_app,
                to_application=daycare_app,
                integration_type='data_sync',
                description='Share user authentication and profile data between timesheet and daycare applications.',
                status='planned',
                complexity='medium',
                estimated_hours=16,
                dependencies=['Shared authentication system', 'User profile API'],
                target_date=timezone.now().date() + timedelta(days=45),
            )

        if autocraftcv_app and timesheet_app:
            Integration.objects.create(
                from_application=autocraftcv_app,
                to_application=timesheet_app,
                integration_type='api',
                description='Import work history from timesheet app to automatically populate CV employment section.',
                status='planned',
                complexity='high',
                estimated_hours=24,
                dependencies=['Timesheet API endpoints', 'CV data model updates'],
                target_date=timezone.now().date() + timedelta(days=60),
            )

    def display_summary(self, project):
        """Display a summary of created data."""
        stats = {
            'projects': Project.objects.count(),
            'applications': Application.objects.filter(project=project).count(),
            'tasks': Task.objects.filter(project=project).count(),
            'artifacts': Artifact.objects.filter(application__project=project).count(),
            'decisions': Decision.objects.filter(project=project).count(),
            'integrations': Integration.objects.filter(from_application__project=project).count(),
        }

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=== SAMPLE DATA CREATION SUMMARY ==='))
        self.stdout.write(f'Projects created: {stats["projects"]}')
        self.stdout.write(f'Applications created: {stats["applications"]}')
        self.stdout.write(f'Tasks created: {stats["tasks"]}')
        self.stdout.write(f'Artifacts created: {stats["artifacts"]}')
        self.stdout.write(f'Decisions created: {stats["decisions"]}')
        self.stdout.write(f'Integrations created: {stats["integrations"]}')
        self.stdout.write('')
        self.stdout.write('You can now access the development tracker at:')
        self.stdout.write('http://127.0.0.1:8000/tracker/')
        self.stdout.write('')
        self.stdout.write('Login credentials:')
        self.stdout.write(f'Username: {project.owner.username}')
        self.stdout.write('Password: password123')
