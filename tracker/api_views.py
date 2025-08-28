"""
FamilyHub Development Tracker - API Views

RESTful API endpoints for AJAX functionality and real-time updates.
All endpoints return JSON responses and require authentication.
"""

import json
from datetime import datetime, timedelta

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.core.serializers import serialize
from django.db.models import Avg, Count, Q, Sum
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .models import Application, Artifact, Decision, Integration, Project, Task
from .views import api_chart_data, api_stats, dashboard_view

# ==========================================
# DASHBOARD API ENDPOINTS
# ==========================================


@login_required
def api_dashboard_stats(request):
    """Get dashboard statistics."""
    return api_stats(request)


@login_required
def api_dashboard_chart_data(request):
    """Get chart data for dashboard."""
    return api_chart_data(request)


# ==========================================
# SEARCH API ENDPOINTS
# ==========================================


@login_required
def api_search(request):
    """Global search across all models."""
    query = request.GET.get("q", "").strip()

    if not query:
        return JsonResponse({"results": []})

    results = []

    # Search projects
    projects = Project.objects.filter(
        Q(name__icontains=query) | Q(description__icontains=query)
    )[:5]

    for project in projects:
        results.append(
            {
                "type": "project",
                "id": project.id,
                "title": project.name,
                "description": project.description[:100],
                "url": f"/tracker/projects/{project.id}/",
                "status": project.status,
            }
        )

    # Search applications
    applications = Application.objects.filter(
        Q(name__icontains=query) | Q(description__icontains=query)
    )[:5]

    for app in applications:
        results.append(
            {
                "type": "application",
                "id": app.id,
                "title": app.name,
                "description": app.description[:100],
                "url": f"/tracker/apps/{app.id}/",
                "project": app.project.name,
            }
        )

    # Search tasks
    tasks = Task.objects.filter(
        Q(title__icontains=query) | Q(description__icontains=query)
    )[:5]

    for task in tasks:
        results.append(
            {
                "type": "task",
                "id": task.id,
                "title": task.title,
                "description": task.description[:100],
                "url": f"/tracker/tasks/{task.id}/",
                "status": task.status,
                "priority": task.priority,
            }
        )

    return JsonResponse({"results": results})


@login_required
def api_search_suggestions(request):
    """Get search suggestions based on partial query."""
    query = request.GET.get("q", "").strip()

    if len(query) < 2:
        return JsonResponse({"suggestions": []})

    suggestions = []

    # Project suggestions
    projects = Project.objects.filter(name__icontains=query)[:3]
    suggestions.extend([f"Project: {p.name}" for p in projects])

    # Application suggestions
    apps = Application.objects.filter(name__icontains=query)[:3]
    suggestions.extend([f"App: {a.name}" for a in apps])

    return JsonResponse({"suggestions": suggestions})


# ==========================================
# TASK API ENDPOINTS
# ==========================================


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def api_task_bulk_update(request):
    """Bulk update task status or assignment."""
    try:
        data = json.loads(request.body)
        task_ids = data.get("task_ids", [])
        action = data.get("action")
        value = data.get("value")

        tasks = Task.objects.filter(id__in=task_ids)

        if action == "status":
            tasks.update(status=value, updated_at=timezone.now())
        elif action == "priority":
            tasks.update(priority=value, updated_at=timezone.now())
        elif action == "assigned_to":
            tasks.update(assigned_to_id=value, updated_at=timezone.now())

        return JsonResponse(
            {"success": True, "message": f"Updated {tasks.count()} tasks"}
        )

    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=400)


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def api_task_status_update(request, pk):
    """Update individual task status."""
    try:
        task = Task.objects.get(pk=pk)
        data = json.loads(request.body)
        new_status = data.get("status")

        task.status = new_status
        task.updated_at = timezone.now()
        task.save()

        return JsonResponse({"success": True, "status": task.get_status_display()})

    except Task.DoesNotExist:
        return JsonResponse({"success": False, "message": "Task not found"}, status=404)
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=400)


@login_required
def api_task_kanban_data(request):
    """Get tasks organized by status for kanban board."""
    tasks_by_status = {}

    statuses = ["todo", "in_progress", "testing", "completed"]

    for status in statuses:
        tasks = Task.objects.filter(status=status).select_related(
            "project", "application", "assigned_to"
        )

        tasks_data = []
        for task in tasks:
            tasks_data.append(
                {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description[:100],
                    "priority": task.priority,
                    "assigned_to": (
                        task.assigned_to.username if task.assigned_to else None
                    ),
                    "project": task.project.name if task.project else None,
                    "application": task.application.name if task.application else None,
                    "due_date": task.due_date.isoformat() if task.due_date else None,
                }
            )

        tasks_by_status[status] = tasks_data

    return JsonResponse(tasks_by_status)


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def api_task_assign(request, pk):
    """Assign task to user."""
    try:
        task = Task.objects.get(pk=pk)
        data = json.loads(request.body)
        assigned_to_id = data.get("assigned_to_id")

        if assigned_to_id:
            from django.contrib.auth.models import User

            user = User.objects.get(pk=assigned_to_id)
            task.assigned_to = user
        else:
            task.assigned_to = None

        task.updated_at = timezone.now()
        task.save()

        return JsonResponse(
            {
                "success": True,
                "assigned_to": task.assigned_to.username if task.assigned_to else None,
            }
        )

    except (Task.DoesNotExist, User.DoesNotExist):
        return JsonResponse(
            {"success": False, "message": "Task or user not found"}, status=404
        )


# ==========================================
# PROJECT API ENDPOINTS
# ==========================================


@login_required
def api_project_progress(request, pk):
    """Get detailed project progress data."""
    try:
        project = Project.objects.get(pk=pk)

        # Calculate application progress
        apps_data = []
        for app in project.applications.all():
            total_tasks = app.task_set.count()
            completed_tasks = app.task_set.filter(status="completed").count()
            progress = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0

            apps_data.append(
                {
                    "name": app.name,
                    "progress": round(progress, 1),
                    "total_tasks": total_tasks,
                    "completed_tasks": completed_tasks,
                    "status": app.status,
                }
            )

        return JsonResponse(
            {
                "project": {
                    "name": project.name,
                    "completion_percentage": project.completion_percentage,
                    "applications": apps_data,
                    "total_tasks": project.total_tasks,
                    "completed_tasks": project.completed_tasks,
                }
            }
        )

    except Project.DoesNotExist:
        return JsonResponse({"error": "Project not found"}, status=404)


@login_required
def api_project_statistics(request, pk):
    """Get project statistics."""
    try:
        project = Project.objects.get(pk=pk)

        stats = {
            "applications_count": project.applications.count(),
            "total_tasks": project.total_tasks,
            "completed_tasks": project.completed_tasks,
            "overdue_tasks": project.task_set.filter(
                due_date__lt=timezone.now().date(), status__in=["todo", "in_progress"]
            ).count(),
            "artifacts_count": Artifact.objects.filter(
                application__project=project
            ).count(),
            "decisions_count": project.decision_set.count(),
            "team_size": (
                project.team_members.count() if hasattr(project, "team_members") else 1
            ),
        }

        return JsonResponse(stats)

    except Project.DoesNotExist:
        return JsonResponse({"error": "Project not found"}, status=404)


@login_required
def api_project_status_distribution(request):
    """Get distribution of projects by status."""
    distribution = (
        Project.objects.values("status").annotate(count=Count("id")).order_by("status")
    )

    return JsonResponse({"distribution": list(distribution)})


# ==========================================
# APPLICATION API ENDPOINTS
# ==========================================


@login_required
def api_application_metrics(request, pk):
    """Get application metrics."""
    try:
        app = Application.objects.get(pk=pk)

        metrics = {
            "tasks_total": app.task_set.count(),
            "tasks_completed": app.task_set.filter(status="completed").count(),
            "artifacts_count": app.artifact_set.count(),
            "latest_version": app.version,
            "features_count": len(app.features) if app.features else 0,
            "tech_stack_count": len(app.tech_stack) if app.tech_stack else 0,
        }

        return JsonResponse(metrics)

    except Application.DoesNotExist:
        return JsonResponse({"error": "Application not found"}, status=404)


@login_required
def api_application_technology_stats(request):
    """Get technology usage statistics."""
    # This would analyze tech_stack JSONField data
    # For now, return sample data
    return JsonResponse(
        {
            "technologies": [
                {"name": "Django", "count": 5, "percentage": 35.7},
                {"name": "React", "count": 3, "percentage": 21.4},
                {"name": "PostgreSQL", "count": 4, "percentage": 28.6},
                {"name": "Docker", "count": 2, "percentage": 14.3},
            ]
        }
    )


# ==========================================
# WIDGET API ENDPOINTS
# ==========================================


@login_required
def api_widget_recent_activity(request):
    """Get recent activity for dashboard widget."""
    limit = int(request.GET.get("limit", 10))

    # Get recent tasks, artifacts, and decisions
    recent_tasks = Task.objects.select_related("project", "application").order_by(
        "-updated_at"
    )[:limit]

    activities = []
    for task in recent_tasks:
        activities.append(
            {
                "type": "task",
                "title": task.title,
                "description": (
                    f"in {task.application.name}"
                    if task.application
                    else f"in {task.project.name}"
                ),
                "timestamp": task.updated_at.isoformat(),
                "url": f"/tracker/tasks/{task.id}/",
                "status": task.status,
            }
        )

    return JsonResponse({"activities": activities})


@login_required
def api_widget_overdue_tasks(request):
    """Get overdue tasks for dashboard widget."""
    overdue_tasks = Task.objects.filter(
        due_date__lt=timezone.now().date(), status__in=["todo", "in_progress"]
    ).select_related("project", "application")[:10]

    tasks_data = []
    for task in overdue_tasks:
        tasks_data.append(
            {
                "id": task.id,
                "title": task.title,
                "project": task.project.name if task.project else None,
                "application": task.application.name if task.application else None,
                "due_date": task.due_date.isoformat(),
                "days_overdue": (timezone.now().date() - task.due_date).days,
                "url": f"/tracker/tasks/{task.id}/",
            }
        )

    return JsonResponse({"overdue_tasks": tasks_data})


@login_required
def api_widget_project_health(request):
    """Get project health indicators."""
    projects = Project.objects.all()

    health_data = []
    for project in projects:
        # Calculate health score based on multiple factors
        completion_score = project.completion_percentage / 100

        # Check if project is on schedule
        if project.target_date and project.start_date:
            total_days = (project.target_date - project.start_date).days
            elapsed_days = (timezone.now().date() - project.start_date).days
            expected_progress = (
                (elapsed_days / total_days) * 100 if total_days > 0 else 0
            )
            schedule_score = (
                min(1.0, project.completion_percentage / expected_progress)
                if expected_progress > 0
                else 1.0
            )
        else:
            schedule_score = 1.0

        # Overall health score (0-100)
        health_score = (completion_score * 0.6 + schedule_score * 0.4) * 100

        health_data.append(
            {
                "project_id": project.id,
                "project_name": project.name,
                "health_score": round(health_score, 1),
                "completion_percentage": project.completion_percentage,
                "status": project.status,
                "is_overdue": (
                    project.target_date < timezone.now().date()
                    if project.target_date
                    else False
                ),
            }
        )

    return JsonResponse({"project_health": health_data})


# ==========================================
# UTILITY API ENDPOINTS
# ==========================================


@login_required
def api_notifications(request):
    """Get user notifications."""
    # Placeholder for notification system
    notifications = [
        {
            "id": 1,
            "title": "Task Overdue",
            "message": "You have 3 overdue tasks",
            "type": "warning",
            "timestamp": timezone.now().isoformat(),
            "read": False,
        }
    ]

    return JsonResponse({"notifications": notifications})


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def api_notifications_mark_read(request):
    """Mark notifications as read."""
    try:
        data = json.loads(request.body)
        notification_ids = data.get("notification_ids", [])

        # Placeholder implementation
        return JsonResponse({"success": True, "marked_count": len(notification_ids)})

    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=400)


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def api_user_theme_toggle(request):
    """Toggle user theme preference."""
    try:
        data = json.loads(request.body)
        theme = data.get("theme", "light")

        # Store theme preference (could be in user profile)
        request.session["theme"] = theme

        return JsonResponse({"success": True, "theme": theme})

    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=400)


@login_required
def api_user_preferences(request):
    """Get user preferences."""
    preferences = {
        "theme": request.session.get("theme", "light"),
        "dashboard_layout": request.session.get("dashboard_layout", "grid"),
        "notifications_enabled": True,
        "timezone": str(timezone.get_current_timezone()),
    }

    return JsonResponse({"preferences": preferences})


# ==========================================
# PLACEHOLDER ENDPOINTS
# ==========================================


@login_required
def api_artifact_upload(request):
    """Placeholder for artifact upload API."""
    return JsonResponse({"message": "Artifact upload API - to be implemented"})


@login_required
def api_artifact_versions(request, pk):
    """Placeholder for artifact versions API."""
    return JsonResponse({"message": "Artifact versions API - to be implemented"})


@login_required
def api_integration_timeline(request):
    """Placeholder for integration timeline API."""
    return JsonResponse({"message": "Integration timeline API - to be implemented"})


@login_required
def api_integration_dependencies(request):
    """Placeholder for integration dependencies API."""
    return JsonResponse({"message": "Integration dependencies API - to be implemented"})


@login_required
def api_export_project(request, pk):
    """Placeholder for project export API."""
    return JsonResponse({"message": "Project export API - to be implemented"})


@login_required
def api_export_tasks(request):
    """Placeholder for task export API."""
    return JsonResponse({"message": "Task export API - to be implemented"})
