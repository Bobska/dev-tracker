"""
FamilyHub Development Tracker - Populate Sample Data

Management command to create realistic sample data for the FamilyHub project.
Creates projects, applications, tasks, artifacts, and decisions for development and testing.

Usage:
    python manage.py populate_sample_data
    python manage.py populate_sample_data --reset  # Delete existing data first
    python manage.py populate_sample_data --minimal  # Create minimal dataset
"""

import random
from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from tracker.models import Application, Artifact, Decision, Integration, Project, Task

User = get_user_model()


class Command(BaseCommand):
    help = "Populate the database with sample FamilyHub development data"

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete all existing data before creating sample data",
        )
        parser.add_argument(
            "--minimal",
            action="store_true",
            help="Create minimal dataset for testing",
        )
        parser.add_argument(
            "--user",
            type=str,
            default="admin",
            help="Username of the project owner (default: admin)",
        )

    def handle(self, *args, **options):
        if options["reset"]:
            self.stdout.write(self.style.WARNING("Deleting existing data..."))
            self.delete_existing_data()

        try:
            # Get or create the project owner
            owner_username = options["user"]
            try:
                owner = User.objects.get(username=owner_username)
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(
                        f'User "{owner_username}" not found. Creating user...'
                    )
                )
                owner = User.objects.create_user(
                    username=owner_username,
                    email=f"{owner_username}@familyhub.dev",
                    password="password123",
                    first_name="Project",
                    last_name="Owner",
                )
                self.stdout.write(self.style.SUCCESS(f"Created user: {owner_username}"))

            if options["minimal"]:
                self.create_minimal_data(owner)
            else:
                self.create_comprehensive_data(owner)

            self.stdout.write(self.style.SUCCESS("Successfully populated sample data!"))

        except Exception as e:
            raise CommandError(f"Error creating sample data: {str(e)}")

    def delete_existing_data(self):
        """Delete all existing tracker data."""
        models_to_delete = [Integration, Decision, Artifact, Task, Application, Project]

        for model in models_to_delete:
            count = model.objects.count()
            if count > 0:
                model.objects.all().delete()
                self.stdout.write(f"Deleted {count} {model.__name__} records")

    def create_minimal_data(self, owner):
        """Create minimal dataset for basic testing."""
        self.stdout.write("Creating minimal sample data...")

        # Create FamilyHub main project
        project = Project.objects.create(
            name="FamilyHub",
            description="Integrated family management platform combining multiple Django applications.",
            status="development",
            owner=owner,
            start_date=timezone.now().date() - timedelta(days=30),
            target_date=timezone.now().date() + timedelta(days=90),
        )

        # Create core applications
        timesheet_app = Application.objects.create(
            project=project,
            name="Timesheet Tracker",
            description="Track work hours and calculate payments for multiple jobs.",
            complexity="medium",
            status="development",
            estimated_weeks=8,
            features=["Time tracking", "Job management", "Payment calculation"],
        )

        daycare_app = Application.objects.create(
            project=project,
            name="Daycare Invoice Tracker",
            description="Track daycare payments and generate monthly reports.",
            complexity="simple",
            status="production",
            estimated_weeks=4,
            features=["Invoice tracking", "Payment history", "Monthly reports"],
        )

        # Create sample tasks
        tasks_data = [
            {
                "title": "Implement time entry validation",
                "description": "Add validation to prevent overlapping time entries",
                "application": timesheet_app,
                "status": "in-progress",
                "priority": "high",
            },
            {
                "title": "Create job management interface",
                "description": "CRUD interface for managing job information",
                "application": timesheet_app,
                "status": "pending",
                "priority": "medium",
            },
            {
                "title": "Deploy daycare app to production",
                "description": "Configure production environment and deploy",
                "application": daycare_app,
                "status": "completed",
                "priority": "high",
            },
        ]

        for task_data in tasks_data:
            Task.objects.create(
                **task_data,
                due_date=timezone.now().date() + timedelta(days=random.randint(1, 30)),
            )

        self.stdout.write(f"Created minimal data:")
        self.stdout.write(f"  - 1 project: {project.name}")
        self.stdout.write(f"  - 2 applications")
        self.stdout.write(f"  - 3 tasks")

    def create_comprehensive_data(self, owner):
        """Create comprehensive dataset with full FamilyHub project structure."""
        self.stdout.write("Creating comprehensive sample data...")

        # Create main FamilyHub project
        familyhub_project = Project.objects.create(
            name="FamilyHub",
            description="Unified family management platform integrating multiple Django applications for comprehensive household management.",
            status="active",
            owner=owner,
            start_date=timezone.now().date() - timedelta(days=90),
            target_date=timezone.now().date() + timedelta(days=180),
        )

        # Create applications with detailed information
        applications_data = [
            {
                "name": "Timesheet Tracker",
                "description": "Track work hours across multiple jobs with automatic payment calculations and detailed reporting.",
                "status": "development",
                "features": [
                    "Multi-job time tracking",
                    "Overlap validation",
                    "Payment calculation",
                    "Weekly/monthly reports",
                    "Break time management",
                    "Export to PDF/Excel",
                ],
            },
            {
                "name": "Daycare Invoice Tracker",
                "description": "Complete daycare payment management with invoice tracking and financial reporting.",
                "status": "production",
                "features": [
                    "Invoice management",
                    "Payment tracking",
                    "Monthly summaries",
                    "Tax reporting",
                    "Provider management",
                    "Receipt storage",
                ],
            },
            {
                "name": "AutoCraftCV",
                "description": "Automated CV generation and job application tracking system.",
                "status": "production",
                "features": [
                    "CV template management",
                    "Auto-generation",
                    "Job application tracking",
                    "Company research",
                    "Interview scheduling",
                    "Document storage",
                ],
            },
            {
                "name": "Employment History",
                "description": "Comprehensive employment history tracking with performance metrics.",
                "status": "planning",
                "features": [
                    "Employment timeline",
                    "Performance tracking",
                    "Skills development",
                    "Reference management",
                    "Career progression analysis",
                ],
            },
            {
                "name": "Upcoming Payments",
                "description": "Payment scheduling and reminder system for all recurring expenses.",
                "status": "planning",
                "features": [
                    "Payment scheduling",
                    "Automatic reminders",
                    "Category management",
                    "Budget tracking",
                    "Bank integration",
                ],
            },
            {
                "name": "Credit Card Management",
                "description": "Credit card tracking with spending analysis and fraud detection.",
                "status": "planning",
                "features": [
                    "Transaction tracking",
                    "Spending analysis",
                    "Credit utilization monitoring",
                    "Fraud alerts",
                    "Payment optimization",
                ],
            },
            {
                "name": "Household Budget",
                "description": "Complete household budget management with predictive analytics.",
                "status": "planning",
                "features": [
                    "Budget creation",
                    "Expense tracking",
                    "Income forecasting",
                    "Savings goals",
                    "Financial reports",
                ],
            },
        ]

        applications = []
        for app_data in applications_data:
            app_data.setdefault('estimated_weeks', 4)
            app = Application.objects.create(project=familyhub_project, **app_data)
            applications.append(app)
            self.stdout.write(f"Created application: {app.name}")

        self.create_detailed_tasks(applications)
        self.create_sample_artifacts(applications)
        self.create_architecture_decisions(familyhub_project)
        self.create_integration_plans(applications)
        self.display_summary(familyhub_project)

    def create_detailed_tasks(self, applications):
        """Create detailed tasks for each application."""
        task_templates = {
            "development": [
                ("Setup project structure", "Initialize Django project with proper directory structure", "completed", "medium"),
                ("Create models and database schema", "Design and implement database models", "completed", "high"),
                ("Implement core views", "Create main application views and logic", "in-progress", "high"),
                ("Design user interface", "Create responsive UI using Bootstrap 5", "in-progress", "medium"),
                ("Add form validation", "Implement client and server-side validation", "pending", "medium"),
                ("Write unit tests", "Create comprehensive test suite", "pending", "high"),
                ("Add user authentication", "Implement login/logout functionality", "pending", "high"),
                ("Performance optimization", "Optimize database queries and caching", "pending", "low"),
            ],
            "production": [
                ("Production deployment", "Deploy application to production environment", "completed", "high"),
                ("Monitor application performance", "Set up monitoring and alerting", "completed", "medium"),
                ("Bug fixes and maintenance", "Ongoing maintenance and bug resolution", "in-progress", "medium"),
                ("Feature enhancement requests", "Implement user-requested features", "pending", "low"),
                ("Security audit", "Conduct security review and updates", "pending", "high"),
                ("Database backup strategy", "Implement automated backup system", "completed", "high"),
            ],
            "planning": [
                ("Requirements gathering", "Define functional and technical requirements", "in-progress", "high"),
                ("Architecture design", "Design system architecture and data flow", "pending", "high"),
                ("Technology stack selection", "Choose appropriate technologies and frameworks", "pending", "medium"),
                ("UI/UX mockups", "Create user interface mockups and wireframes", "pending", "medium"),
                ("Project timeline", "Create detailed development timeline", "pending", "medium"),
                ("Resource allocation", "Determine development resources needed", "pending", "low"),
            ],
        }

        for app in applications:
            templates = task_templates.get(app.status, task_templates["development"])
            for title, description, status, priority in templates:
                if status == "completed":
                    due_date = timezone.now().date() - timedelta(days=random.randint(1, 30))
                elif status == "in-progress":
                    due_date = timezone.now().date() + timedelta(days=random.randint(1, 14))
                else:
                    due_date = timezone.now().date() + timedelta(days=random.randint(15, 60))
                Task.objects.create(
                    application=app,
                    title=f"{app.name}: {title}",
                    description=description,
                    status=status,
                    priority=priority,
                    due_date=due_date,
                )

    def create_sample_artifacts(self, applications):
        """Create sample artifacts for applications."""
        artifact_templates = [
            ("Requirements Document", "documentation", "complete", "Comprehensive functional and technical requirements"),
            ("Architecture Diagram", "design", "complete", "System architecture and component relationships"),
            ("Database Schema", "design", "complete", "Database design and entity relationships"),
            ("API Documentation", "documentation", "in-progress", "RESTful API endpoint documentation"),
            ("User Manual", "documentation", "draft", "End-user documentation and guides"),
            ("Test Plan", "documentation", "draft", "Testing strategy and test cases"),
            ("Deployment Guide", "documentation", "in-progress", "Production deployment instructions"),
        ]

        for app in applications[:3]:
            for name, type, status, description in artifact_templates:
                Artifact.objects.create(
                    application=app,
                    name=f"{app.name} - {name}",
                    type=type,
                    status=status,
                    description=description,
                    version="1.0",
                    content=f"Sample content for {name} of {app.name}.",
                )

    def create_architecture_decisions(self, project):
        """Create sample architecture decisions."""
        decisions_data = [
            {
                "title": "Choose Django as Primary Framework",
                "description": "After evaluating Flask, FastAPI, and Django, we decided on Django for its comprehensive feature set, admin interface, and ORM capabilities. Rationale: Django provides built-in authentication, admin interface, and ORM which will accelerate development. The project complexity justifies the framework overhead.",
                "status": "decided",
                "impact": "high",
            },
            {
                "title": "Implement Microservices Architecture",
                "description": "Structure FamilyHub as separate Django applications that can be developed and deployed independently. Rationale: Allows for independent development cycles, easier maintenance, and selective deployment of applications.",
                "status": "decided",
                "impact": "high",
            },
            {
                "title": "Use PostgreSQL for Production Database",
                "description": "Standardize on PostgreSQL for all production deployments while using SQLite for development. Rationale: PostgreSQL provides better performance, JSON field support, and advanced features needed for complex queries.",
                "status": "decided",
                "impact": "medium",
            },
            {
                "title": "Implement Shared Authentication System",
                "description": "Create a unified authentication system across all FamilyHub applications. Rationale: Users should be able to access all family management tools with a single login.",
                "status": "pending",
                "impact": "high",
            },
            {
                "title": "Bootstrap 5 for UI Consistency",
                "description": "Standardize on Bootstrap 5 for all user interface components across applications. Rationale: Ensures consistent look and feel, responsive design, and faster development with pre-built components.",
                "status": "decided",
                "impact": "medium",
            },
        ]
        for decision_data in decisions_data:
            Decision.objects.create(project=project, **decision_data)

    def create_integration_plans(self, applications):
        """Create integration plans between applications."""
        timesheet_app = next((app for app in applications if "Timesheet" in app.name), None)
        daycare_app = next((app for app in applications if "Daycare" in app.name), None)
        autocraftcv_app = next((app for app in applications if "AutoCraftCV" in app.name), None)

        if timesheet_app and daycare_app:
            Integration.objects.create(
                from_app=timesheet_app,
                to_app=daycare_app,
                integration_type="data-sharing",
                description="Share user authentication and profile data between timesheet and daycare applications.",
                status="planned",
                complexity="medium",
                estimated_weeks=2,
            )
        if autocraftcv_app and timesheet_app:
            Integration.objects.create(
                from_app=autocraftcv_app,
                to_app=timesheet_app,
                integration_type="api-integration",
                description="Import work history from timesheet app to automatically populate CV employment section.",
                status="planned",
                complexity="complex",
                estimated_weeks=3,
            )

    def display_summary(self, project):
        """Display a summary of created data."""
        stats = {
            "projects": Project.objects.count(),
            "applications": Application.objects.filter(project=project).count(),
            "tasks": Task.objects.filter(application__project=project).count(),
            "artifacts": Artifact.objects.filter(application__project=project).count(),
            "decisions": Decision.objects.filter(project=project).count(),
            "integrations": Integration.objects.filter(from_app__project=project).count(),
        }
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("=== SAMPLE DATA CREATION SUMMARY ==="))
        self.stdout.write(f'Projects created: {stats["projects"]}')
        self.stdout.write(f'Applications created: {stats["applications"]}')
        self.stdout.write(f'Tasks created: {stats["tasks"]}')
        self.stdout.write(f'Artifacts created: {stats["artifacts"]}')
        self.stdout.write(f'Decisions created: {stats["decisions"]}')
        self.stdout.write(f'Integrations created: {stats["integrations"]}')
        self.stdout.write("")
        self.stdout.write("You can now access the development tracker at:")
        self.stdout.write("http://127.0.0.1:8000/tracker/")
        self.stdout.write("")
        self.stdout.write("Login credentials:")
        self.stdout.write(f"Username: {project.owner.username}")
        self.stdout.write("Password: password123")
