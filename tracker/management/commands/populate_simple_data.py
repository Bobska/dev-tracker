"""
FamilyHub Development Tracker - Populate Sample Data (Simplified)

Simple management command to create basic sample data for testing.
"""

import random
from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from tracker.models import Application, Artifact, Decision, Integration, Project, Task

User = get_user_model()


class Command(BaseCommand):
    help = "Populate the database with basic sample data"

    def handle(self, *args, **options):
        try:
            self.stdout.write("Creating sample data...")

            # Get or create a user
            admin_user, created = User.objects.get_or_create(
                username="admin",
                defaults={
                    "email": "admin@familyhub.local",
                    "is_staff": True,
                    "is_superuser": True,
                },
            )
            if created:
                admin_user.set_password("admin123")
                admin_user.save()
                self.stdout.write("Created admin user")

            # Create FamilyHub project
            project, created = Project.objects.get_or_create(
                name="FamilyHub",
                defaults={
                    "description": "Integrated family management platform combining multiple Django applications",
                    "owner": admin_user,
                    "status": "development",
                    "start_date": timezone.now().date() - timedelta(days=30),
                    "target_date": timezone.now().date() + timedelta(days=180),
                    "features": [
                        "Timesheet tracking",
                        "Daycare management",
                        "CV automation",
                        "Payment tracking",
                        "Budget management",
                    ],
                },
            )
            self.stdout.write(f"Project: {project.name}")

            # Create sample applications
            apps_data = [
                {
                    "name": "Timesheet Tracker",
                    "description": "Employee time tracking and payroll calculation",
                    "complexity": "medium",
                    "status": "development",
                    "estimated_weeks": 8,
                    "features": [
                        "Time tracking",
                        "Job management",
                        "Payment calculation",
                    ],
                },
                {
                    "name": "Daycare Invoice Tracker",
                    "description": "Track daycare payments and invoices",
                    "complexity": "simple",
                    "status": "production",
                    "estimated_weeks": 4,
                    "features": ["Invoice tracking", "Payment history", "Reports"],
                },
                {
                    "name": "AutoCraftCV",
                    "description": "Automated CV generation and management",
                    "complexity": "high",
                    "status": "production",
                    "estimated_weeks": 12,
                    "features": [
                        "CV generation",
                        "Template management",
                        "Export formats",
                    ],
                },
                {
                    "name": "Employment History",
                    "description": "Track employment history and career progression",
                    "complexity": "medium",
                    "status": "planning",
                    "estimated_weeks": 6,
                    "features": ["Job history", "Career tracking", "Analytics"],
                },
                {
                    "name": "Upcoming Payments",
                    "description": "Track and schedule upcoming payments",
                    "complexity": "simple",
                    "status": "planning",
                    "estimated_weeks": 3,
                    "features": ["Payment scheduling", "Reminders", "Categories"],
                },
                {
                    "name": "Credit Card Management",
                    "description": "Manage credit cards and track spending",
                    "complexity": "medium",
                    "status": "planning",
                    "estimated_weeks": 8,
                    "features": [
                        "Card tracking",
                        "Spending analysis",
                        "Payment tracking",
                    ],
                },
                {
                    "name": "Household Budget",
                    "description": "Complete household budget management",
                    "complexity": "high",
                    "status": "planning",
                    "estimated_weeks": 10,
                    "features": [
                        "Budget planning",
                        "Expense tracking",
                        "Financial reports",
                    ],
                },
            ]

            applications = []
            for app_data in apps_data:
                app, created = Application.objects.get_or_create(
                    project=project, name=app_data["name"], defaults=app_data
                )
                applications.append(app)
                if created:
                    self.stdout.write(f"Created application: {app.name}")

            # Create sample tasks
            task_data = [
                {
                    "title": "Implement time entry validation",
                    "description": "Add validation to prevent overlapping time entries",
                    "application": applications[0],  # Timesheet
                    "status": "in-progress",
                    "priority": "high",
                },
                {
                    "title": "Create job management interface",
                    "description": "CRUD interface for managing job information",
                    "application": applications[0],  # Timesheet
                    "status": "pending",
                    "priority": "medium",
                },
                {
                    "title": "Deploy daycare app to production",
                    "description": "Configure production environment and deploy",
                    "application": applications[1],  # Daycare
                    "status": "completed",
                    "priority": "high",
                },
                {
                    "title": "Design CV template system",
                    "description": "Create flexible template system for CV generation",
                    "application": applications[2],  # AutoCraftCV
                    "status": "in-progress",
                    "priority": "high",
                },
                {
                    "title": "Plan database schema for employment history",
                    "description": "Design database models for tracking employment",
                    "application": applications[3],  # Employment History
                    "status": "pending",
                    "priority": "medium",
                },
            ]

            for task_info in task_data:
                task, created = Task.objects.get_or_create(
                    title=task_info["title"],
                    defaults={
                        "description": task_info["description"],
                        "application": task_info["application"],
                        "status": task_info["status"],
                        "priority": task_info["priority"],
                        "due_date": timezone.now().date()
                        + timedelta(days=random.randint(7, 30)),
                    },
                )
                if created:
                    self.stdout.write(f"Created task: {task.title}")

            # Create sample decisions
            decisions_data = [
                {
                    "title": "Choose Django 5.2 as framework",
                    "description": "Selected Django 5.2 for all applications due to consistency and LTS support. Long-term support, consistent architecture, team expertise.",
                    "status": "decided",
                    "impact": "high",
                    "decision_maker": "Tech Lead",
                    "decided_date": timezone.now().date() - timedelta(days=14),
                },
                {
                    "title": "Use Bootstrap 5 for UI framework",
                    "description": "Standardize on Bootstrap 5 for responsive design across all apps. Rapid development, consistent look, mobile-first approach.",
                    "status": "decided",
                    "impact": "medium",
                    "decision_maker": "UI Team",
                    "decided_date": timezone.now().date() - timedelta(days=7),
                },
            ]

            for decision_info in decisions_data:
                decision, created = Decision.objects.get_or_create(
                    title=decision_info["title"],
                    defaults={
                        "project": project,
                        "description": decision_info["description"],
                        "status": decision_info["status"],
                        "impact": decision_info["impact"],
                        "decision_maker": decision_info["decision_maker"],
                        "decided_date": decision_info["decided_date"],
                    },
                )
                if created:
                    self.stdout.write(f"Created decision: {decision.title}")

            # Create sample artifacts
            artifacts_data = [
                {
                    "name": "Timesheet Requirements Document",
                    "description": "Complete requirements specification for timesheet application",
                    "application": applications[0],
                    "type": "requirements",
                    "version": "1.0",
                    "created_by": admin_user,
                },
                {
                    "name": "Database Schema Design",
                    "description": "ERD and database design documentation",
                    "application": applications[0],
                    "type": "architecture",
                    "version": "1.1",
                    "created_by": admin_user,
                },
            ]

            for artifact_info in artifacts_data:
                artifact, created = Artifact.objects.get_or_create(
                    name=artifact_info["name"],
                    defaults={
                        "application": artifact_info["application"],
                        "description": artifact_info["description"],
                        "type": artifact_info["type"],
                        "version": artifact_info["version"],
                        "created_by": artifact_info["created_by"],
                    },
                )
                if created:
                    self.stdout.write(f"Created artifact: {artifact.name}")

            # Create sample integrations
            if len(applications) >= 2:
                integration, created = Integration.objects.get_or_create(
                    from_app=applications[0],  # Timesheet
                    to_app=applications[1],  # Daycare
                    defaults={
                        "integration_type": "data-sharing",
                        "status": "planned",
                        "complexity": "medium",
                        "description": "Share user data between timesheet and daycare applications",
                        "estimated_weeks": 3,
                    },
                )
                if created:
                    self.stdout.write(
                        f"Created integration: {integration.from_app.name} -> {integration.to_app.name}"
                    )

            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully created sample data:\n"
                    f"- 1 Project: {project.name}\n"
                    f"- {len(applications)} Applications\n"
                    f"- {Task.objects.count()} Tasks\n"
                    f"- {Decision.objects.count()} Decisions\n"
                    f"- {Artifact.objects.count()} Artifacts\n"
                    f"- {Integration.objects.count()} Integrations"
                )
            )

        except Exception as e:
            raise CommandError(f"Error creating sample data: {str(e)}")
