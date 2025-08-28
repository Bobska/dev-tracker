from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse, HttpResponse, Http404
from django.db.models import Q, Count, Avg, Sum
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models.functions import TruncMonth
import json
from datetime import datetime, timedelta

from .models import Project, Application, Artifact, Task, Decision, Integration
from .forms import (
    ProjectForm, ApplicationForm, ArtifactForm, TaskForm, 
    SearchForm, BulkTaskForm, DecisionForm, IntegrationForm
)


# ==========================================
# DASHBOARD VIEWS
# ==========================================

@login_required
def dashboard_view(request):
    """Main dashboard with overview statistics and recent activity."""
    
    # Date range filter
    date_range = request.GET.get('date_range', '30')
    try:
        days_back = int(date_range)
    except (ValueError, TypeError):
        days_back = 30
    
    cutoff_date = timezone.now() - timedelta(days=days_back)
    
    # Project filter
    project_filter = request.GET.get('project')
    projects_queryset = Project.objects.all()
    if project_filter:
        projects_queryset = projects_queryset.filter(pk=project_filter)
    
    # Overview Statistics
    stats = {
        'total_projects': projects_queryset.count(),
        'total_applications': Application.objects.filter(
            project__in=projects_queryset
        ).count(),
        'total_tasks': Task.objects.filter(
            application__project__in=projects_queryset
        ).count(),
        'total_artifacts': Artifact.objects.filter(
            application__project__in=projects_queryset
        ).count(),
    }
    
    # Completion rates
    completed_projects = projects_queryset.filter(status='completed').count()
    completed_apps = Application.objects.filter(
        project__in=projects_queryset, status='production'
    ).count()
    completed_tasks = Task.objects.filter(
        application__project__in=projects_queryset, status='completed'
    ).count()
    
    stats.update({
        'project_completion_rate': (
            (completed_projects / stats['total_projects'] * 100) 
            if stats['total_projects'] > 0 else 0
        ),
        'app_completion_rate': (
            (completed_apps / stats['total_applications'] * 100) 
            if stats['total_applications'] > 0 else 0
        ),
        'task_completion_rate': (
            (completed_tasks / stats['total_tasks'] * 100) 
            if stats['total_tasks'] > 0 else 0
        ),
    })
    
    # Recent activity
    recent_artifacts = Artifact.objects.filter(
        application__project__in=projects_queryset,
        updated_at__gte=cutoff_date
    ).order_by('-updated_at')[:10]
    
    # Overdue tasks
    overdue_tasks = Task.objects.filter(
        application__project__in=projects_queryset,
        due_date__lt=timezone.now().date(),
        status__in=['pending', 'in-progress']
    ).order_by('due_date')[:10]
    
    # Pending decisions
    pending_decisions = Decision.objects.filter(
        project__in=projects_queryset,
        status='pending'
    ).order_by('-created_at')[:10]
    
    # Progress charts data (Chart.js ready)
    # Monthly task completion data
    monthly_data = Task.objects.filter(
        application__project__in=projects_queryset,
        updated_at__gte=timezone.now() - timedelta(days=365)
    ).annotate(
        month=TruncMonth('updated_at')
    ).values('month').annotate(
        completed=Count('id', filter=Q(status='completed')),
        total=Count('id')
    ).order_by('month')
    
    chart_data = {
        'labels': [item['month'].strftime('%B %Y') for item in monthly_data],
        'completed': [item['completed'] for item in monthly_data],
        'total': [item['total'] for item in monthly_data],
    }
    
    # Status distribution for pie chart
    status_distribution = projects_queryset.values('status').annotate(
        count=Count('id')
    ).order_by('status')
    
    # Context for template
    context = {
        'stats': stats,
        'recent_artifacts': recent_artifacts,
        'overdue_tasks': overdue_tasks,
        'pending_decisions': pending_decisions,
        'chart_data': json.dumps(chart_data),
        'status_distribution': json.dumps(list(status_distribution)),
        'date_range': date_range,
        'project_filter': project_filter,
        'all_projects': Project.objects.all(),
    }
    
    return render(request, 'tracker/dashboard.html', context)


# ==========================================
# PROJECT VIEWS
# ==========================================

class ProjectListView(LoginRequiredMixin, ListView):
    """List all projects with filtering and search."""
    model = Project
    template_name = 'tracker/project_list.html'
    context_object_name = 'projects'
    paginate_by = 10

    def get_queryset(self):
        queryset = Project.objects.all().prefetch_related('applications', 'applications__tasks')
        
        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query)
            )
        
        # Status filter
        status_filter = self.request.GET.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Owner filter
        owner_filter = self.request.GET.get('owner')
        if owner_filter:
            queryset = queryset.filter(owner_id=owner_filter)
        
        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['status_filter'] = self.request.GET.get('status', '')
        context['owner_filter'] = self.request.GET.get('owner', '')
        context['status_choices'] = Project.STATUS_CHOICES
        # Get unique owners (User objects) who have projects
        owner_ids = Project.objects.values_list('owner_id', flat=True).distinct()
        context['owners'] = User.objects.filter(id__in=owner_ids)
        return context


class ProjectDetailView(LoginRequiredMixin, DetailView):
    """Detailed project view with related apps, tasks, and progress."""
    model = Project
    template_name = 'tracker/project_detail.html'
    context_object_name = 'project'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = self.object
        
        # Related applications with task counts
        applications = project.applications.annotate(
            total_tasks=Count('tasks'),
            completed_tasks=Count('tasks', filter=Q(tasks__status='completed')),
            overdue_tasks=Count('tasks', filter=Q(
                tasks__due_date__lt=timezone.now().date(),
                tasks__status__in=['pending', 'in-progress']
            ))
        ).order_by('name')
        
        # Recent artifacts
        recent_artifacts = Artifact.objects.filter(
            application__project=project
        ).order_by('-updated_at')[:5]
        
        # Project timeline data
        timeline_data = []
        for app in applications:
            for task in app.tasks.order_by('due_date')[:3]:
                timeline_data.append({
                    'date': task.due_date,
                    'title': task.title,
                    'app': app.name,
                    'status': task.status,
                    'type': 'task'
                })
        
        # Pending decisions
        pending_decisions = project.decisions.filter(status='pending').order_by('decided_date')
        
        context.update({
            'applications': applications,
            'recent_artifacts': recent_artifacts,
            'timeline_data': sorted(timeline_data, key=lambda x: x['date'] or timezone.now().date()),
            'pending_decisions': pending_decisions,
        })
        
        return context


class ProjectCreateView(LoginRequiredMixin, CreateView):
    """Create new project."""
    model = Project
    form_class = ProjectForm
    template_name = 'tracker/project_form.html'

    def form_valid(self, form):
        messages.success(self.request, f'Project "{form.instance.name}" created successfully!')
        return super().form_valid(form)


class ProjectUpdateView(LoginRequiredMixin, UpdateView):
    """Update existing project."""
    model = Project
    form_class = ProjectForm
    template_name = 'tracker/project_form.html'

    def form_valid(self, form):
        messages.success(self.request, f'Project "{form.instance.name}" updated successfully!')
        return super().form_valid(form)


@login_required
def project_dashboard_view(request, pk):
    """Project-specific dashboard with app integration status."""
    project = get_object_or_404(Project, pk=pk)
    
    # Integration status data
    integrations = Integration.objects.filter(
        Q(from_app__project=project) | Q(to_app__project=project)
    ).select_related('from_app', 'to_app')
    
    # App status summary
    app_status = project.applications.values('status').annotate(
        count=Count('id')
    ).order_by('status')
    
    # Task distribution by app
    task_distribution = project.applications.annotate(
        total_tasks=Count('tasks'),
        completed_tasks=Count('tasks', filter=Q(tasks__status='completed'))
    ).order_by('name')
    
    context = {
        'project': project,
        'integrations': integrations,
        'app_status': app_status,
        'task_distribution': task_distribution,
    }
    
    return render(request, 'tracker/project_dashboard.html', context)


# ==========================================
# APPLICATION VIEWS
# ==========================================

class ApplicationListView(LoginRequiredMixin, ListView):
    """List applications grouped by project."""
    model = Application
    template_name = 'tracker/application_list.html'
    context_object_name = 'applications'
    paginate_by = 15

    def get_queryset(self):
        queryset = Application.objects.select_related('project').prefetch_related('tasks', 'artifacts')
        
        # Project filter
        project_filter = self.request.GET.get('project')
        if project_filter:
            queryset = queryset.filter(project_id=project_filter)
        
        # Status filter
        status_filter = self.request.GET.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Complexity filter
        complexity_filter = self.request.GET.get('complexity')
        if complexity_filter:
            queryset = queryset.filter(complexity=complexity_filter)
        
        return queryset.order_by('project__name', 'name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['projects'] = Project.objects.all()
        context['status_choices'] = Application.STATUS_CHOICES
        context['complexity_choices'] = Application.COMPLEXITY_CHOICES
        context['project_filter'] = self.request.GET.get('project', '')
        context['status_filter'] = self.request.GET.get('status', '')
        context['complexity_filter'] = self.request.GET.get('complexity', '')
        return context


class ApplicationDetailView(LoginRequiredMixin, DetailView):
    """Detailed application view with artifacts, tasks, and integrations."""
    model = Application
    template_name = 'tracker/application_detail.html'
    context_object_name = 'application'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        application = self.object
        
        # Related artifacts grouped by type
        artifacts_by_type = {}
        for artifact in application.artifacts.all():
            artifact_type = artifact.get_type_display()
            if artifact_type not in artifacts_by_type:
                artifacts_by_type[artifact_type] = []
            artifacts_by_type[artifact_type].append(artifact)
        
        # Tasks by status
        tasks_by_status = {}
        for status_code, status_display in Task.STATUS_CHOICES:
            tasks_by_status[status_display] = application.tasks.filter(status=status_code)
        
        # Related integrations
        integrations = Integration.objects.filter(
            Q(from_app=application) | Q(to_app=application)
        )
        
        context.update({
            'artifacts_by_type': artifacts_by_type,
            'tasks_by_status': tasks_by_status,
            'integrations': integrations,
        })
        
        return context


class ApplicationCreateView(LoginRequiredMixin, CreateView):
    """Create new application."""
    model = Application
    form_class = ApplicationForm
    template_name = 'tracker/application_form.html'

    def form_valid(self, form):
        messages.success(self.request, f'Application "{form.instance.name}" created successfully!')
        return super().form_valid(form)


class ApplicationUpdateView(LoginRequiredMixin, UpdateView):
    """Update existing application."""
    model = Application
    form_class = ApplicationForm
    template_name = 'tracker/application_form.html'

    def form_valid(self, form):
        messages.success(self.request, f'Application "{form.instance.name}" updated successfully!')
        return super().form_valid(form)


# ==========================================
# ARTIFACT VIEWS
# ==========================================

class ArtifactListView(LoginRequiredMixin, ListView):
    """List artifacts with filtering by app, type, and status."""
    model = Artifact
    template_name = 'tracker/artifact_list.html'
    context_object_name = 'artifacts'
    paginate_by = 20

    def get_queryset(self):
        queryset = Artifact.objects.select_related('application', 'application__project')
        
        # Application filter
        app_filter = self.request.GET.get('application')
        if app_filter:
            queryset = queryset.filter(application_id=app_filter)
        
        # Type filter
        type_filter = self.request.GET.get('type')
        if type_filter:
            queryset = queryset.filter(type=type_filter)
        
        # Status filter
        status_filter = self.request.GET.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Search
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(content__icontains=search_query) |
                Q(description__icontains=search_query)
            )
        
        return queryset.order_by('-updated_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['applications'] = Application.objects.all()
        context['type_choices'] = Artifact.TYPE_CHOICES
        context['status_choices'] = Artifact.STATUS_CHOICES
        context['app_filter'] = self.request.GET.get('application', '')
        context['type_filter'] = self.request.GET.get('type', '')
        context['status_filter'] = self.request.GET.get('status', '')
        context['search_query'] = self.request.GET.get('search', '')
        return context


class ArtifactDetailView(LoginRequiredMixin, DetailView):
    """Detailed artifact view with file downloads and version history."""
    model = Artifact
    template_name = 'tracker/artifact_detail.html'
    context_object_name = 'artifact'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        artifact = self.object
        
        # Version history (other artifacts with same name in same app)
        version_history = Artifact.objects.filter(
            application=artifact.application,
            name=artifact.name
        ).exclude(pk=artifact.pk).order_by('-created_at')
        
        context['version_history'] = version_history
        return context


class ArtifactCreateView(LoginRequiredMixin, CreateView):
    """Create new artifact with file upload and text content."""
    model = Artifact
    form_class = ArtifactForm
    template_name = 'tracker/artifact_form.html'

    def form_valid(self, form):
        messages.success(self.request, f'Artifact "{form.instance.name}" created successfully!')
        return super().form_valid(form)


class ArtifactUpdateView(LoginRequiredMixin, UpdateView):
    """Update existing artifact with version increment logic."""
    model = Artifact
    form_class = ArtifactForm
    template_name = 'tracker/artifact_form.html'

    def form_valid(self, form):
        messages.success(self.request, f'Artifact "{form.instance.name}" updated successfully!')
        return super().form_valid(form)


@login_required
def artifact_download_view(request, pk):
    """Download artifact file."""
    artifact = get_object_or_404(Artifact, pk=pk)
    
    if not artifact.file_upload:
        raise Http404("File not found")
    
    # Serve file download
    response = HttpResponse(artifact.file_upload.read(), content_type='application/octet-stream')
    response['Content-Disposition'] = f'attachment; filename="{artifact.file_upload.name}"'
    return response


# ==========================================
# TASK VIEWS
# ==========================================

class TaskListView(LoginRequiredMixin, ListView):
    """List tasks with kanban-style display options."""
    model = Task
    template_name = 'tracker/task_list.html'
    context_object_name = 'tasks'
    paginate_by = 30

    def get_queryset(self):
        queryset = Task.objects.select_related('application', 'application__project')
        
        # Application filter
        app_filter = self.request.GET.get('application')
        if app_filter:
            queryset = queryset.filter(application_id=app_filter)
        
        # Status filter
        status_filter = self.request.GET.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Assignee filter
        assignee_filter = self.request.GET.get('assignee')
        if assignee_filter:
            queryset = queryset.filter(assignee=assignee_filter)
        
        # Priority filter
        priority_filter = self.request.GET.get('priority')
        if priority_filter:
            queryset = queryset.filter(priority=priority_filter)
        
        # Overdue filter
        if self.request.GET.get('overdue') == 'true':
            queryset = queryset.filter(
                due_date__lt=timezone.now().date(),
                status__in=['pending', 'in-progress']
            )
        
        return queryset.order_by('due_date', 'priority')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # For kanban view, group tasks by status
        if self.request.GET.get('view') == 'kanban':
            tasks_by_status = {}
            for status_code, status_display in Task.STATUS_CHOICES:
                tasks_by_status[status_display] = self.get_queryset().filter(status=status_code)
            context['tasks_by_status'] = tasks_by_status
            context['view_type'] = 'kanban'
        else:
            context['view_type'] = 'list'
        
        context['applications'] = Application.objects.all()
        context['status_choices'] = Task.STATUS_CHOICES
        context['assignee_choices'] = Task.ASSIGNEE_CHOICES
        context['priority_choices'] = Task.PRIORITY_CHOICES
        context['bulk_form'] = BulkTaskForm()
        
        # Filter values
        context.update({
            'app_filter': self.request.GET.get('application', ''),
            'status_filter': self.request.GET.get('status', ''),
            'assignee_filter': self.request.GET.get('assignee', ''),
            'priority_filter': self.request.GET.get('priority', ''),
            'overdue_filter': self.request.GET.get('overdue', ''),
        })
        
        return context


class TaskDetailView(LoginRequiredMixin, DetailView):
    """Detailed task view with time tracking."""
    model = Task
    template_name = 'tracker/task_detail.html'
    context_object_name = 'task'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        task = self.object
        
        # Calculate time variance
        if task.estimated_hours and task.actual_hours:
            variance = task.actual_hours - task.estimated_hours
            variance_percentage = (variance / task.estimated_hours) * 100
            context['time_variance'] = {
                'hours': variance,
                'percentage': variance_percentage
            }
        
        return context


class TaskCreateView(LoginRequiredMixin, CreateView):
    """Create new task."""
    model = Task
    form_class = TaskForm
    template_name = 'tracker/task_form.html'

    def form_valid(self, form):
        messages.success(self.request, f'Task "{form.instance.title}" created successfully!')
        return super().form_valid(form)


class TaskUpdateView(LoginRequiredMixin, UpdateView):
    """Update existing task."""
    model = Task
    form_class = TaskForm
    template_name = 'tracker/task_form.html'

    def form_valid(self, form):
        messages.success(self.request, f'Task "{form.instance.title}" updated successfully!')
        return super().form_valid(form)


@login_required
def bulk_task_operations_view(request):
    """Handle bulk operations on tasks."""
    if request.method == 'POST':
        form = BulkTaskForm(request.POST)
        if form.is_valid():
            action = form.cleaned_data['action']
            task_ids = form.cleaned_data['task_ids']
            
            tasks = Task.objects.filter(id__in=task_ids)
            updated_count = 0
            
            if action in ['complete', 'in_progress', 'pending']:
                tasks.update(status=action.replace('_', '-'))
                updated_count = tasks.count()
                messages.success(request, f'{updated_count} tasks updated to {action} status.')
            
            elif action == 'change_assignee':
                assignee = form.cleaned_data['new_assignee']
                tasks.update(assignee=assignee)
                updated_count = tasks.count()
                messages.success(request, f'{updated_count} tasks reassigned.')
            
            elif action == 'update_due_date':
                new_due_date = form.cleaned_data['new_due_date']
                tasks.update(due_date=new_due_date)
                updated_count = tasks.count()
                messages.success(request, f'{updated_count} tasks due date updated.')
        
        else:
            messages.error(request, 'Error in bulk operation form.')
    
    return redirect('tracker:task_list')


# ==========================================
# INTEGRATION VIEWS
# ==========================================

class IntegrationListView(LoginRequiredMixin, ListView):
    """Integration roadmap view with timeline visualization."""
    model = Integration
    template_name = 'tracker/integration_list.html'
    context_object_name = 'integrations'

    def get_queryset(self):
        return Integration.objects.select_related(
            'from_app', 'to_app', 'from_app__project', 'to_app__project'
        ).order_by('status', 'complexity')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Group integrations by status for roadmap view
        integrations_by_status = {}
        for status_code, status_display in Integration.STATUS_CHOICES:
            integrations_by_status[status_display] = self.get_queryset().filter(status=status_code)
        
        context['integrations_by_status'] = integrations_by_status
        return context


class IntegrationDetailView(LoginRequiredMixin, DetailView):
    """Integration detail with dependency tracking."""
    model = Integration
    template_name = 'tracker/integration_detail.html'
    context_object_name = 'integration'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        integration = self.object
        
        # Find dependent integrations
        dependent_integrations = Integration.objects.filter(
            Q(from_app=integration.to_app) | Q(to_app=integration.from_app)
        ).exclude(pk=integration.pk)
        
        context['dependent_integrations'] = dependent_integrations
        return context


class IntegrationCreateView(LoginRequiredMixin, CreateView):
    """Create integration plan."""
    model = Integration
    form_class = IntegrationForm
    template_name = 'tracker/integration_form.html'

    def form_valid(self, form):
        messages.success(self.request, f'Integration created successfully!')
        return super().form_valid(form)


class IntegrationUpdateView(LoginRequiredMixin, UpdateView):
    """Update integration plan."""
    model = Integration
    form_class = IntegrationForm
    template_name = 'tracker/integration_form.html'

    def form_valid(self, form):
        messages.success(self.request, f'Integration updated successfully!')
        return super().form_valid(form)


# ==========================================
# SEARCH AND UTILITY VIEWS
# ==========================================

@login_required
def search_view(request):
    """Global search across all models."""
    form = SearchForm(request.GET or None)
    results = {
        'projects': [],
        'applications': [],
        'artifacts': [],
        'tasks': [],
        'decisions': [],
        'integrations': [],
    }
    
    if form.is_valid():
        query = form.cleaned_data['query']
        search_type = form.cleaned_data['search_type']
        project_filter = form.cleaned_data['project']
        
        # Base filters
        project_q = Q()
        if project_filter:
            project_q = Q(project=project_filter)
        
        # Search in different models based on type
        if search_type in ['all', 'projects']:
            projects_q = Q(name__icontains=query) | Q(description__icontains=query)
            if project_filter:
                projects_q &= Q(pk=project_filter.pk)
            results['projects'] = Project.objects.filter(projects_q)[:10]
        
        if search_type in ['all', 'applications']:
            apps_q = Q(name__icontains=query) | Q(description__icontains=query)
            if project_filter:
                apps_q &= Q(project=project_filter)
            results['applications'] = Application.objects.filter(apps_q)[:10]
        
        if search_type in ['all', 'artifacts']:
            artifacts_q = (
                Q(name__icontains=query) | 
                Q(content__icontains=query) | 
                Q(description__icontains=query)
            )
            if project_filter:
                artifacts_q &= Q(application__project=project_filter)
            results['artifacts'] = Artifact.objects.filter(artifacts_q)[:10]
        
        if search_type in ['all', 'tasks']:
            tasks_q = Q(title__icontains=query) | Q(description__icontains=query)
            if project_filter:
                tasks_q &= Q(application__project=project_filter)
            results['tasks'] = Task.objects.filter(tasks_q)[:10]
        
        if search_type in ['all', 'decisions']:
            decisions_q = Q(title__icontains=query) | Q(description__icontains=query)
            if project_filter:
                decisions_q &= Q(project=project_filter)
            results['decisions'] = Decision.objects.filter(decisions_q)[:10]
        
        if search_type in ['all', 'integrations']:
            integrations_q = Q(description__icontains=query)
            if project_filter:
                integrations_q &= (
                    Q(from_app__project=project_filter) | 
                    Q(to_app__project=project_filter)
                )
            results['integrations'] = Integration.objects.filter(integrations_q)[:10]
    
    context = {
        'form': form,
        'results': results,
        'total_results': sum(len(result_list) for result_list in results.values()),
    }
    
    return render(request, 'tracker/search.html', context)


@login_required
def api_chart_data(request):
    """API endpoint for chart data (AJAX)."""
    chart_type = request.GET.get('type', 'monthly_tasks')
    
    if chart_type == 'monthly_tasks':
        # Monthly task completion data
        data = Task.objects.annotate(
            month=TruncMonth('updated_at')
        ).values('month').annotate(
            completed=Count('id', filter=Q(status='completed')),
            total=Count('id')
        ).order_by('month')
        
        return JsonResponse({
            'labels': [item['month'].strftime('%B %Y') for item in data],
            'datasets': [{
                'label': 'Completed Tasks',
                'data': [item['completed'] for item in data],
                'backgroundColor': 'rgba(75, 192, 192, 0.2)',
                'borderColor': 'rgba(75, 192, 192, 1)',
            }, {
                'label': 'Total Tasks',
                'data': [item['total'] for item in data],
                'backgroundColor': 'rgba(255, 99, 132, 0.2)',
                'borderColor': 'rgba(255, 99, 132, 1)',
            }]
        })
    
    elif chart_type == 'project_status':
        # Project status distribution
        data = Project.objects.values('status').annotate(count=Count('id'))
        
        return JsonResponse({
            'labels': [item['status'].title() for item in data],
            'data': [item['count'] for item in data],
            'backgroundColor': [
                '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF'
            ]
        })
    
    return JsonResponse({'error': 'Invalid chart type'}, status=400)


# ==========================================
# DECISION VIEWS (Additional)
# ==========================================

class DecisionListView(LoginRequiredMixin, ListView):
    """List project decisions."""
    model = Decision
    template_name = 'tracker/decision_list.html'
    context_object_name = 'decisions'
    paginate_by = 20

    def get_queryset(self):
        queryset = Decision.objects.select_related('project')
        
        # Project filter
        project_filter = self.request.GET.get('project')
        if project_filter:
            queryset = queryset.filter(project_id=project_filter)
        
        # Status filter
        status_filter = self.request.GET.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['projects'] = Project.objects.all()
        context['status_choices'] = Decision.STATUS_CHOICES
        return context


class DecisionDetailView(LoginRequiredMixin, DetailView):
    """Decision detail view."""
    model = Decision
    template_name = 'tracker/decision_detail.html'
    context_object_name = 'decision'


class DecisionCreateView(LoginRequiredMixin, CreateView):
    """Create new decision."""
    model = Decision
    form_class = DecisionForm
    template_name = 'tracker/decision_form.html'

    def form_valid(self, form):
        messages.success(self.request, f'Decision "{form.instance.title}" created successfully!')
        return super().form_valid(form)


class DecisionUpdateView(LoginRequiredMixin, UpdateView):
    """Update existing decision."""
    model = Decision
    form_class = DecisionForm
    template_name = 'tracker/decision_form.html'

    def form_valid(self, form):
        messages.success(self.request, f'Decision "{form.instance.title}" updated successfully!')
        return super().form_valid(form)


@login_required
def api_stats(request):
    """API endpoint for footer statistics."""
    try:
        stats = {
            'projects': Project.objects.count(),
            'applications': Application.objects.count(),
            'tasks': Task.objects.count(),
            'completion_rate': 0,
        }
        
        # Calculate overall completion rate
        total_tasks = Task.objects.count()
        if total_tasks > 0:
            completed_tasks = Task.objects.filter(status='completed').count()
            stats['completion_rate'] = round((completed_tasks / total_tasks) * 100, 1)
        
        return JsonResponse(stats)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# =============================================================================
# DELETE VIEWS
# =============================================================================

class ProjectDeleteView(LoginRequiredMixin, DeleteView):
    """Delete a project with confirmation."""
    model = Project
    template_name = 'tracker/project_confirm_delete.html'
    success_url = reverse_lazy('tracker:project_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Project deleted successfully.')
        return super().delete(request, *args, **kwargs)


class ApplicationDeleteView(LoginRequiredMixin, DeleteView):
    """Delete an application with confirmation."""
    model = Application
    template_name = 'tracker/application_confirm_delete.html'
    success_url = reverse_lazy('tracker:application_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Application deleted successfully.')
        return super().delete(request, *args, **kwargs)


class TaskDeleteView(LoginRequiredMixin, DeleteView):
    """Delete a task with confirmation."""
    model = Task
    template_name = 'tracker/task_confirm_delete.html'
    success_url = reverse_lazy('tracker:task_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Task deleted successfully.')
        return super().delete(request, *args, **kwargs)


class ArtifactDeleteView(LoginRequiredMixin, DeleteView):
    """Delete an artifact with confirmation."""
    model = Artifact
    template_name = 'tracker/artifact_confirm_delete.html'
    success_url = reverse_lazy('tracker:artifact_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Artifact deleted successfully.')
        return super().delete(request, *args, **kwargs)


class DecisionDeleteView(LoginRequiredMixin, DeleteView):
    """Delete a decision with confirmation."""
    model = Decision
    template_name = 'tracker/decision_confirm_delete.html'
    success_url = reverse_lazy('tracker:decision_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Decision deleted successfully.')
        return super().delete(request, *args, **kwargs)


class IntegrationDeleteView(LoginRequiredMixin, DeleteView):
    """Delete an integration with confirmation."""
    model = Integration
    template_name = 'tracker/integration_confirm_delete.html'
    success_url = reverse_lazy('tracker:integration_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Integration deleted successfully.')
        return super().delete(request, *args, **kwargs)
