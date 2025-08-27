from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.validators import FileExtensionValidator
import os

User = get_user_model()


class Project(models.Model):
    """
    Main project container (e.g., FamilyHub)
    """
    STATUS_CHOICES = [
        ('planning', 'Planning'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('on_hold', 'On Hold'),
        ('cancelled', 'Cancelled'),
    ]

    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planning')
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    repository_url = models.URLField(blank=True)
    documentation_url = models.URLField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_projects')
    team_members = models.ManyToManyField(User, related_name='projects', blank=True)
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
        """Calculate project completion based on tasks."""
        total_tasks = self.tasks.count()
        if total_tasks == 0:
            return 0
        completed_tasks = self.tasks.filter(status='completed').count()
        return round((completed_tasks / total_tasks) * 100, 1)


class Application(models.Model):
    """
    Individual applications within a project (e.g., Timesheet, Daycare Tracker)
    """
    STATUS_CHOICES = [
        ('planning', 'Planning'),
        ('development', 'Development'),
        ('testing', 'Testing'),
        ('production', 'Production'),
        ('maintenance', 'Maintenance'),
        ('deprecated', 'Deprecated'),
    ]

    TECHNOLOGY_CHOICES = [
        ('django', 'Django'),
        ('react', 'React'),
        ('vue', 'Vue.js'),
        ('angular', 'Angular'),
        ('flask', 'Flask'),
        ('fastapi', 'FastAPI'),
        ('nodejs', 'Node.js'),
        ('other', 'Other'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='applications')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planning')
    technology_stack = models.CharField(max_length=20, choices=TECHNOLOGY_CHOICES, default='django')
    version = models.CharField(max_length=20, default='1.0.0')
    repository_url = models.URLField(blank=True)
    demo_url = models.URLField(blank=True)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_applications')
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


class Task(models.Model):
    """
    Development tasks with assignment tracking
    """
    STATUS_CHOICES = [
        ('todo', 'To Do'),
        ('in_progress', 'In Progress'),
        ('review', 'In Review'),
        ('completed', 'Completed'),
        ('blocked', 'Blocked'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]

    ASSIGNEE_CHOICES = [
        ('human', 'Human Developer'),
        ('claude', 'Claude AI'),
        ('copilot', 'GitHub Copilot'),
        ('team', 'Development Team'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='tasks', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='todo')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    assignee_type = models.CharField(max_length=20, choices=ASSIGNEE_CHOICES, default='human')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tasks')
    estimated_hours = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    actual_hours = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tasks')
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
        from django.utils import timezone
        return self.due_date and self.due_date < timezone.now().date() and self.status != 'completed'


def artifact_upload_path(instance, filename):
    """Generate upload path for artifacts."""
    return f'artifacts/{instance.application.project.name}/{instance.application.name}/{filename}'


class Artifact(models.Model):
    """
    Project artifacts with versioning (requirements, code, documentation)
    """
    TYPE_CHOICES = [
        ('requirements', 'Requirements Document'),
        ('design', 'Design Document'),
        ('code', 'Source Code'),
        ('documentation', 'Documentation'),
        ('test', 'Test Files'),
        ('deployment', 'Deployment Scripts'),
        ('other', 'Other'),
    ]

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='artifacts')
    artifact_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='documentation')
    version = models.CharField(max_length=20, default='1.0')
    file = models.FileField(
        upload_to=artifact_upload_path,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx', 'txt', 'md', 'py', 'js', 'html', 'css', 'json'])],
        null=True,
        blank=True
    )
    content = models.TextField(blank=True, help_text="Text content for the artifact")
    url = models.URLField(blank=True, help_text="External URL for the artifact")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_artifacts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['application', 'name', 'version']
        verbose_name = "Artifact"
        verbose_name_plural = "Artifacts"

    def __str__(self):
        return f"{self.name} v{self.version} ({self.application})"

    def get_absolute_url(self):
        return reverse('tracker:artifact_detail', kwargs={'pk': self.pk})

    @property
    def file_size_mb(self):
        """Get file size in MB."""
        if self.file:
            return round(self.file.size / (1024 * 1024), 2)
        return 0


class Decision(models.Model):
    """
    Architecture and technical decision logging
    """
    STATUS_CHOICES = [
        ('proposed', 'Proposed'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('superseded', 'Superseded'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='decisions')
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='decisions', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='proposed')
    rationale = models.TextField(help_text="Why this decision was made")
    consequences = models.TextField(blank=True, help_text="Expected consequences of this decision")
    alternatives = models.TextField(blank=True, help_text="Alternative options considered")
    decision_maker = models.ForeignKey(User, on_delete=models.CASCADE, related_name='decisions_made')
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


class Integration(models.Model):
    """
    App-to-app integration planning and tracking
    """
    STATUS_CHOICES = [
        ('planned', 'Planned'),
        ('in_progress', 'In Progress'),
        ('testing', 'Testing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    COMPLEXITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('very_high', 'Very High'),
    ]

    name = models.CharField(max_length=200)
    description = models.TextField()
    source_application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='outgoing_integrations')
    target_application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='incoming_integrations')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planned')
    complexity = models.CharField(max_length=20, choices=COMPLEXITY_CHOICES, default='medium')
    estimated_hours = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    actual_hours = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    dependencies = models.TextField(blank=True, help_text="List any dependencies for this integration")
    notes = models.TextField(blank=True)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_integrations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['source_application', 'target_application', 'name']
        verbose_name = "Integration"
        verbose_name_plural = "Integrations"

    def __str__(self):
        return f"{self.source_application.name} → {self.target_application.name}: {self.name}"

    def get_absolute_url(self):
        return reverse('tracker:integration_detail', kwargs={'pk': self.pk})
