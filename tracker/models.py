from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.validators import FileExtensionValidator
from django.utils import timezone
import os

User = get_user_model()


def artifact_upload_path(instance, filename):
    """Generate upload path for artifacts."""
    return f'artifacts/{instance.application.project.name}/{instance.application.name}/{filename}'


class Project(models.Model):
    """
    Main project container (e.g., FamilyHub)
    """
    STATUS_CHOICES = [
        ('planning', 'Planning'),
        ('development', 'Development'),
        ('testing', 'Testing'),
        ('completed', 'Completed'),
        ('on-hold', 'On Hold'),
    ]

    name = models.CharField(max_length=100)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planning')
    start_date = models.DateField()
    target_date = models.DateField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_projects')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Project"
        verbose_name_plural = "Projects"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('tracker:project_detail', kwargs={'pk': self.pk})

    @property
    def completion_percentage(self):
        """Calculate project completion based on tasks across all applications."""
        total_tasks = 0
        completed_tasks = 0
        
        for app in self.applications.all():
            app_tasks = app.tasks.all()
            total_tasks += app_tasks.count()
            completed_tasks += app_tasks.filter(status='completed').count()
        
        if total_tasks == 0:
            return 0
        return round((completed_tasks / total_tasks) * 100, 1)

    @property
    def overdue_tasks_count(self):
        """Count overdue tasks across all applications in the project."""
        overdue_count = 0
        today = timezone.now().date()
        
        for app in self.applications.all():
            overdue_count += app.tasks.filter(
                due_date__lt=today,
                status__in=['pending', 'in-progress']
            ).count()
        
        return overdue_count

    @property
    def total_applications_count(self):
        """Total number of applications in this project."""
        return self.applications.count()

    @property
    def completed_applications_count(self):
        """Number of applications in production status."""
        return self.applications.filter(status='production').count()

    @property
    def days_remaining(self):
        """Days remaining until target date (negative if overdue)."""
        if self.target_date:
            delta = self.target_date - timezone.now().date()
            return delta.days
        return 0

    @property
    def is_overdue(self):
        """Check if project is past its target date."""
        if self.target_date:
            return timezone.now().date() > self.target_date
        return False

    @property
    def days_overdue(self):
        """Get number of days overdue (positive number)."""
        if self.is_overdue:
            return abs(self.days_remaining)
        return 0


class Application(models.Model):
    """
    Individual applications within a project (e.g., Timesheet, Daycare Tracker)
    """
    STATUS_CHOICES = [
        ('planning', 'Planning'),
        ('ready', 'Ready'),
        ('development', 'Development'),
        ('testing', 'Testing'),
        ('production', 'Production'),
    ]

    COMPLEXITY_CHOICES = [
        ('simple', 'Simple'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='applications')
    name = models.CharField(max_length=100)
    description = models.TextField()
    complexity = models.CharField(max_length=20, choices=COMPLEXITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planning')
    estimated_weeks = models.PositiveIntegerField()
    features = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['project', 'name']
        unique_together = ['project', 'name']
        verbose_name = "Application"
        verbose_name_plural = "Applications"

    def __str__(self):
        return f"{self.project.name} - {self.name}"

    def get_absolute_url(self):
        return reverse('tracker:application_detail', kwargs={'pk': self.pk})

    @property
    def tasks_completion_percentage(self):
        """Calculate application completion based on its tasks."""
        total_tasks = self.tasks.count()
        if total_tasks == 0:
            return 0
        completed_tasks = self.tasks.filter(status='completed').count()
        return round((completed_tasks / total_tasks) * 100, 1)

    @property
    def overdue_tasks_count(self):
        """Count overdue tasks for this application."""
        today = timezone.now().date()
        return self.tasks.filter(
            due_date__lt=today,
            status__in=['pending', 'in-progress']
        ).count()

    @property
    def days_to_target(self):
        """Calculate days to target completion (estimated based on weeks)."""
        if not self.estimated_weeks:
            return None
        target_date = self.created_at.date() + timezone.timedelta(weeks=self.estimated_weeks)
        today = timezone.now().date()
        return (target_date - today).days


class Artifact(models.Model):
    """
    Artifacts like requirements, code, documentation for applications
    """
    TYPE_CHOICES = [
        ('requirements', 'Requirements'),
        ('code', 'Code'),
        ('documentation', 'Documentation'),
        ('architecture', 'Architecture'),
        ('design', 'Design'),
    ]

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('in-progress', 'In Progress'),
        ('review', 'Review'),
        ('complete', 'Complete'),
    ]

    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='artifacts', null=True, blank=True)
    name = models.CharField(max_length=200)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, blank=True)
    description = models.TextField(blank=True)
    file_upload = models.FileField(
        upload_to=artifact_upload_path,
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx', 'txt', 'md', 'py', 'js', 'html', 'css'])]
    )
    content = models.TextField(help_text="Text content for the artifact")
    version = models.CharField(max_length=10, default='1.0', blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_artifacts', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']
        verbose_name = "Artifact"
        verbose_name_plural = "Artifacts"

    def __str__(self):
        if self.application:
            return f"{self.application.name} - {self.name} (v{self.version})"
        return f"{self.name} (v{self.version})"

    def get_absolute_url(self):
        return reverse('tracker:artifact_detail', kwargs={'pk': self.pk})

    @property
    def file_size_mb(self):
        """Get file size in MB if file exists."""
        if self.file_upload:
            return round(self.file_upload.size / (1024 * 1024), 2)
        return 0


class Task(models.Model):
    """
    Development tasks with assignment tracking
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in-progress', 'In Progress'),
        ('completed', 'Completed'),
        ('blocked', 'Blocked'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]

    ASSIGNEE_CHOICES = [
        ('claude', 'Claude'),
        ('github-copilot', 'GitHub Copilot'),
        ('human', 'Human'),
        ('team', 'Team'),
    ]

    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    assignee = models.CharField(max_length=20, choices=ASSIGNEE_CHOICES, default='human')
    due_date = models.DateField(null=True, blank=True)
    estimated_hours = models.PositiveIntegerField(null=True, blank=True)
    actual_hours = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Task"
        verbose_name_plural = "Tasks"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('tracker:task_detail', kwargs={'pk': self.pk})

    @property
    def is_overdue(self):
        """Check if task is overdue."""
        if not self.due_date:
            return False
        return self.due_date < timezone.now().date() and self.status in ['pending', 'in-progress']

    @property
    def days_until_due(self):
        """Calculate days until due date."""
        if not self.due_date:
            return None
        today = timezone.now().date()
        return (self.due_date - today).days

    @property
    def hours_variance(self):
        """Calculate variance between estimated and actual hours."""
        if self.estimated_hours and self.actual_hours:
            return self.actual_hours - self.estimated_hours
        return None


class Decision(models.Model):
    """
    Project decisions and architecture choices
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('decided', 'Decided'),
        ('implemented', 'Implemented'),
        ('changed', 'Changed'),
    ]

    IMPACT_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='decisions')
    title = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    impact = models.CharField(max_length=10, choices=IMPACT_CHOICES, default='medium')
    decided_date = models.DateField(null=True, blank=True)
    decision_maker = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Decision"
        verbose_name_plural = "Decisions"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('tracker:decision_detail', kwargs={'pk': self.pk})

    @property
    def days_since_creation(self):
        """Calculate days since decision was created."""
        return (timezone.now().date() - self.created_at.date()).days

    @property
    def is_pending_too_long(self):
        """Check if decision has been pending for more than 30 days."""
        return self.status == 'pending' and self.days_since_creation > 30


class Integration(models.Model):
    """
    Integration plans between applications
    """
    INTEGRATION_TYPE_CHOICES = [
        ('data-sharing', 'Data Sharing'),
        ('ui-integration', 'UI Integration'),
        ('api-integration', 'API Integration'),
        ('full-merge', 'Full Merge'),
    ]

    STATUS_CHOICES = [
        ('planned', 'Planned'),
        ('in-progress', 'In Progress'),
        ('completed', 'Completed'),
        ('blocked', 'Blocked'),
    ]

    COMPLEXITY_CHOICES = [
        ('simple', 'Simple'),
        ('medium', 'Medium'),
        ('complex', 'Complex'),
    ]

    from_app = models.ForeignKey(
        Application, 
        on_delete=models.CASCADE, 
        related_name='integrations_from'
    )
    to_app = models.ForeignKey(
        Application, 
        on_delete=models.CASCADE, 
        related_name='integrations_to'
    )
    integration_type = models.CharField(max_length=20, choices=INTEGRATION_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planned')
    complexity = models.CharField(max_length=10, choices=COMPLEXITY_CHOICES, default='medium')
    description = models.TextField()
    estimated_weeks = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['from_app', 'to_app', 'integration_type']
        verbose_name = "Integration"
        verbose_name_plural = "Integrations"

    def __str__(self):
        return f"{self.from_app.name} → {self.to_app.name} ({self.integration_type})"

    def get_absolute_url(self):
        return reverse('tracker:integration_detail', kwargs={'pk': self.pk})

    @property
    def project(self):
        """Get the project from the from_app (assuming both apps are in the same project)."""
        return self.from_app.project

    @property
    def complexity_multiplier(self):
        """Get complexity multiplier for time estimates."""
        multipliers = {
            'simple': 1.0,
            'medium': 1.5,
            'complex': 2.5
        }
        return multipliers.get(self.complexity, 1.0)

    @property
    def estimated_hours(self):
        """Convert estimated weeks to hours with complexity factor."""
        base_hours = self.estimated_weeks * 40  # 40 hours per week
        return round(base_hours * self.complexity_multiplier)

    def clean(self):
        """Validate that from_app and to_app are different and from same project."""
        from django.core.exceptions import ValidationError
        
        if self.from_app == self.to_app:
            raise ValidationError("Cannot integrate an application with itself.")
        
        if self.from_app.project != self.to_app.project:
            raise ValidationError("Can only integrate applications within the same project.")


class Requirement(models.Model):
    """
    Requirements documentation with Claude Artifact-style formatting
    """
    name = models.CharField(max_length=200, help_text="Requirement name or title")
    content = models.TextField(help_text="Requirement content in Markdown format for Claude Artifact display")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']
        verbose_name = "Requirement"
        verbose_name_plural = "Requirements"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('tracker:requirement_detail', kwargs={'pk': self.pk})
