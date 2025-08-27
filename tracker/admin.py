from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import Project, Application, Task, Artifact, Decision, Integration


# Custom admin site configuration
admin.site.site_header = "FamilyHub Development Tracker Admin"
admin.site.site_title = "Dev Tracker Admin"
admin.site.index_title = "Welcome to FamilyHub Development Tracker Administration"


# Inline admin classes for related models
class ApplicationInline(admin.TabularInline):
    model = Application
    extra = 0
    fields = ['name', 'status', 'complexity', 'estimated_weeks']
    show_change_link = True


class ArtifactInline(admin.TabularInline):
    model = Artifact
    extra = 0
    fields = ['name', 'artifact_type', 'status', 'version']
    show_change_link = True


class TaskInline(admin.TabularInline):
    model = Task
    extra = 0
    fields = ['title', 'status', 'priority', 'assignee', 'due_date']
    readonly_fields = ['is_overdue']
    show_change_link = True


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'status_badge', 'start_date', 'target_date', 'owner', 'completion_display', 'applications_count']
    list_filter = ['status', 'owner', 'start_date', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at', 'completion_percentage', 'overdue_tasks_count']
    inlines = [ApplicationInline]
    
    fieldsets = [
        ('Basic Information', {
            'fields': ('name', 'description', 'owner')
        }),
        ('Project Timeline', {
            'fields': ('status', 'start_date', 'target_date')
        }),
        ('Statistics', {
            'fields': ('completion_percentage', 'overdue_tasks_count'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    ]

    actions = ['mark_as_active', 'mark_as_completed', 'mark_as_on_hold']

    def status_badge(self, obj):
        colors = {
            'planning': '#17a2b8',  # info blue
            'active': '#28a745',    # success green
            'on-hold': '#ffc107',   # warning yellow
            'completed': '#6c757d', # secondary gray
            'cancelled': '#dc3545'  # danger red
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
            colors.get(obj.status, '#6c757d'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def completion_display(self, obj):
        percentage = obj.completion_percentage
        if percentage >= 90:
            color = '#28a745'  # green
        elif percentage >= 50:
            color = '#ffc107'  # yellow
        else:
            color = '#dc3545'  # red
        return format_html(
            '<div style="width: 100px; background-color: #e9ecef; border-radius: 3px; overflow: hidden;">'
            '<div style="width: {}%; background-color: {}; height: 20px; text-align: center; color: white; font-size: 11px; line-height: 20px;">'
            '{:.0f}%</div></div>',
            percentage, color, percentage
        )
    completion_display.short_description = 'Completion'

    def applications_count(self, obj):
        return obj.applications.count()
    applications_count.short_description = 'Apps'

    def mark_as_active(self, request, queryset):
        updated = queryset.update(status='active')
        self.message_user(request, f'{updated} projects marked as active.')
    mark_as_active.short_description = "Mark selected projects as active"

    def mark_as_completed(self, request, queryset):
        updated = queryset.update(status='completed')
        self.message_user(request, f'{updated} projects marked as completed.')
    mark_as_completed.short_description = "Mark selected projects as completed"

    def mark_as_on_hold(self, request, queryset):
        updated = queryset.update(status='on-hold')
        self.message_user(request, f'{updated} projects marked as on-hold.')
    mark_as_on_hold.short_description = "Mark selected projects as on-hold"


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ['name', 'project', 'status_badge', 'complexity_badge', 'estimated_weeks', 'task_completion_display']
    list_filter = ['project', 'status', 'complexity', 'created_at']
    search_fields = ['name', 'description', 'project__name']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [ArtifactInline, TaskInline]
    
    fieldsets = [
        ('Basic Information', {
            'fields': ('project', 'name', 'description')
        }),
        ('Development Details', {
            'fields': ('application_type', 'status', 'complexity', 'estimated_weeks')
        }),
        ('Features', {
            'fields': ('features',),
            'description': 'JSON field for storing feature list'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    ]

    actions = ['mark_as_ready', 'mark_as_development', 'mark_as_production']

    def status_badge(self, obj):
        colors = {
            'planning': '#6c757d',     # gray
            'ready': '#17a2b8',       # info blue
            'development': '#ffc107',  # warning yellow
            'testing': '#fd7e14',     # orange
            'production': '#28a745'   # success green
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
            colors.get(obj.status, '#6c757d'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def complexity_badge(self, obj):
        colors = {
            'simple': '#28a745',   # green
            'medium': '#ffc107',   # yellow
            'high': '#dc3545'      # red
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
            colors.get(obj.complexity, '#6c757d'),
            obj.get_complexity_display()
        )
    complexity_badge.short_description = 'Complexity'

    def task_completion_display(self, obj):
        # Calculate task completion for this application
        total_tasks = obj.tasks.count()
        if total_tasks == 0:
            return format_html('<span style="color: #6c757d;">No tasks</span>')
        
        completed_tasks = obj.tasks.filter(status='completed').count()
        percentage = (completed_tasks / total_tasks) * 100
        
        if percentage >= 90:
            color = '#28a745'  # green
        elif percentage >= 50:
            color = '#ffc107'  # yellow
        else:
            color = '#dc3545'  # red
        return format_html(
            '<div style="width: 80px; background-color: #e9ecef; border-radius: 3px; overflow: hidden;">'
            '<div style="width: {}%; background-color: {}; height: 18px; text-align: center; color: white; font-size: 10px; line-height: 18px;">'
            '{:.0f}%</div></div>',
            percentage, color, percentage
        )
    task_completion_display.short_description = 'Tasks'

    def mark_as_ready(self, request, queryset):
        updated = queryset.update(status='ready')
        self.message_user(request, f'{updated} applications marked as ready.')
    mark_as_ready.short_description = "Mark selected applications as ready"

    def mark_as_development(self, request, queryset):
        updated = queryset.update(status='development')
        self.message_user(request, f'{updated} applications marked as in development.')
    mark_as_development.short_description = "Mark selected applications as in development"

    def mark_as_production(self, request, queryset):
        updated = queryset.update(status='production')
        self.message_user(request, f'{updated} applications marked as production.')
    mark_as_production.short_description = "Mark selected applications as production"


@admin.register(Artifact)
class ArtifactAdmin(admin.ModelAdmin):
    list_display = ['name', 'application', 'type_badge', 'status_badge', 'version', 'file_size_display', 'created_at']
    list_filter = ['application', 'type', 'status', 'created_at']
    search_fields = ['name', 'description', 'application__name']
    readonly_fields = ['created_at', 'updated_at', 'file_size_mb']
    
    fieldsets = [
        ('Basic Information', {
            'fields': ('application', 'name', 'description')
        }),
        ('Artifact Details', {
            'fields': ('type', 'status', 'version')
        }),
        ('Content', {
            'fields': ('file_upload', 'content', 'url'),
            'description': 'Upload a file, add text content, or provide a URL'
        }),
        ('File Information', {
            'fields': ('file_size_mb',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    ]

    def type_badge(self, obj):
        colors = {
            'requirements': '#17a2b8',   # info blue
            'code': '#28a745',          # success green
            'documentation': '#6f42c1', # purple
            'architecture': '#fd7e14',   # orange
            'design': '#e83e8c'         # pink
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
            colors.get(obj.type, '#6c757d'),
            obj.get_type_display()
        )
    type_badge.short_description = 'Type'

    def status_badge(self, obj):
        colors = {
            'draft': '#6c757d',        # gray
            'in-progress': '#ffc107',  # yellow
            'review': '#fd7e14',       # orange
            'complete': '#28a745'      # green
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
            colors.get(obj.status, '#6c757d'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def file_size_display(self, obj):
        size = obj.file_size_mb
        if size > 0:
            if size > 5:
                color = '#dc3545'  # red for large files
            elif size > 1:
                color = '#ffc107'  # yellow for medium files
            else:
                color = '#28a745'  # green for small files
            return format_html(
                '<span style="color: {}; font-weight: bold;">{:.1f} MB</span>',
                color, size
            )
        return format_html('<span style="color: #6c757d;">No file</span>')
    file_size_display.short_description = 'File Size'


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'application', 'priority_badge', 'status_badge', 'assignee_badge', 'due_date', 'overdue_indicator']
    list_filter = ['application', 'priority', 'status', 'assignee', 'due_date', 'created_at']
    search_fields = ['title', 'description', 'application__name']
    readonly_fields = ['created_at', 'updated_at', 'is_overdue']
    
    fieldsets = [
        ('Basic Information', {
            'fields': ('application', 'title', 'description')
        }),
        ('Task Details', {
            'fields': ('priority', 'status', 'assignee', 'due_date')
        }),
        ('Time Tracking', {
            'fields': ('estimated_hours', 'actual_hours'),
            'classes': ('collapse',)
        }),
        ('Status Information', {
            'fields': ('is_overdue',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    ]

    actions = ['mark_as_pending', 'mark_as_in_progress', 'mark_as_completed', 'mark_as_blocked']

    def priority_badge(self, obj):
        colors = {
            'low': '#28a745',       # green
            'medium': '#ffc107',    # yellow
            'high': '#fd7e14',      # orange
            'critical': '#dc3545'   # red
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px; font-weight: bold;">{}</span>',
            colors.get(obj.priority, '#6c757d'),
            obj.get_priority_display().upper()
        )
    priority_badge.short_description = 'Priority'

    def status_badge(self, obj):
        colors = {
            'pending': '#6c757d',      # gray
            'in-progress': '#17a2b8',  # info blue
            'completed': '#28a745',    # green
            'blocked': '#dc3545'       # red
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
            colors.get(obj.status, '#6c757d'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def assignee_badge(self, obj):
        colors = {
            'claude': '#6f42c1',         # purple
            'github-copilot': '#0366d6', # github blue
            'human': '#28a745',          # green
            'team': '#fd7e14'            # orange
        }
        icons = {
            'claude': '🤖',
            'github-copilot': '🧑‍💻',
            'human': '👤',
            'team': '👥'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">{} {}</span>',
            colors.get(obj.assignee, '#6c757d'),
            icons.get(obj.assignee, ''),
            obj.get_assignee_display()
        )
    assignee_badge.short_description = 'Assignee'

    def overdue_indicator(self, obj):
        if obj.is_overdue:
            return format_html('<span style="color: #dc3545; font-size: 16px;" title="Task is overdue">⚠️</span>')
        elif obj.due_date:
            days_left = (obj.due_date - timezone.now().date()).days
            if days_left <= 1:
                return format_html('<span style="color: #ffc107; font-size: 16px;" title="Due soon">⏰</span>')
            else:
                return format_html('<span style="color: #28a745; font-size: 16px;" title="On track">✅</span>')
        return format_html('<span style="color: #6c757d;" title="No due date">➖</span>')
    overdue_indicator.short_description = 'Due Status'

    def mark_as_pending(self, request, queryset):
        updated = queryset.update(status='pending')
        self.message_user(request, f'{updated} tasks marked as pending.')
    mark_as_pending.short_description = "Mark selected tasks as pending"

    def mark_as_in_progress(self, request, queryset):
        updated = queryset.update(status='in-progress')
        self.message_user(request, f'{updated} tasks marked as in progress.')
    mark_as_in_progress.short_description = "Mark selected tasks as in progress"

    def mark_as_completed(self, request, queryset):
        updated = queryset.update(status='completed')
        self.message_user(request, f'{updated} tasks marked as completed.')
    mark_as_completed.short_description = "Mark selected tasks as completed"

    def mark_as_blocked(self, request, queryset):
        updated = queryset.update(status='blocked')
        self.message_user(request, f'{updated} tasks marked as blocked.')
    mark_as_blocked.short_description = "Mark selected tasks as blocked"


@admin.register(Decision)
class DecisionAdmin(admin.ModelAdmin):
    list_display = ['title', 'project', 'status_badge', 'impact_badge', 'age_display', 'created_at']
    list_filter = ['project', 'status', 'impact', 'created_at']
    search_fields = ['title', 'description', 'rationale']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = [
        ('Basic Information', {
            'fields': ('project', 'title', 'description')
        }),
        ('Decision Details', {
            'fields': ('status', 'impact', 'rationale', 'alternatives')
        }),
        ('Timeline', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    ]

    def status_badge(self, obj):
        colors = {
            'pending': '#ffc107',     # yellow
            'approved': '#28a745',    # green
            'rejected': '#dc3545',    # red
            'deferred': '#6c757d'     # gray
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
            colors.get(obj.status, '#6c757d'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def impact_badge(self, obj):
        colors = {
            'low': '#28a745',      # green
            'medium': '#ffc107',   # yellow
            'high': '#fd7e14',     # orange
            'critical': '#dc3545'  # red
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px; font-weight: bold;">{}</span>',
            colors.get(obj.impact, '#6c757d'),
            obj.get_impact_display().upper()
        )
    impact_badge.short_description = 'Impact'

    def age_display(self, obj):
        days = obj.age_in_days
        if days > 30:
            color = '#dc3545'  # red
        elif days > 7:
            color = '#ffc107'  # yellow
        else:
            color = '#28a745'  # green
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} days</span>',
            color, days
        )
    age_display.short_description = 'Age'


@admin.register(Integration)
class IntegrationAdmin(admin.ModelAdmin):
    list_display = ['integration_name', 'from_application', 'to_application', 'integration_type_badge', 'complexity_badge', 'estimated_hours']
    list_filter = ['integration_type', 'complexity', 'from_app__project']
    search_fields = ['name', 'description', 'from_app__name', 'to_app__name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = [
        ('Integration Overview', {
            'fields': ('name', 'description')
        }),
        ('Integration Details', {
            'fields': ('from_app', 'to_app', 'integration_type')
        }),
        ('Planning', {
            'fields': ('complexity', 'estimated_hours')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    ]

    def from_application(self, obj):
        return format_html(
            '<a href="{}" title="View application">{}</a>',
            reverse('admin:tracker_application_change', args=[obj.from_app.pk]),
            obj.from_app.name
        )
    from_application.short_description = 'From App'

    def to_application(self, obj):
        return format_html(
            '<a href="{}" title="View application">{}</a>',
            reverse('admin:tracker_application_change', args=[obj.to_app.pk]),
            obj.to_app.name
        )
    to_application.short_description = 'To App'

    def integration_name(self, obj):
        return obj.name or f"{obj.from_app.name} → {obj.to_app.name}"
    integration_name.short_description = 'Integration'

    def integration_type_badge(self, obj):
        colors = {
            'api': '#17a2b8',        # info blue
            'database': '#28a745',   # green
            'ui': '#6f42c1',         # purple
            'file': '#fd7e14',       # orange
            'messaging': '#e83e8c'   # pink
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
            colors.get(obj.integration_type, '#6c757d'),
            obj.get_integration_type_display()
        )
    integration_type_badge.short_description = 'Type'

    def complexity_badge(self, obj):
        colors = {
            'simple': '#28a745',   # green
            'medium': '#ffc107',   # yellow
            'complex': '#dc3545'   # red
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px; font-weight: bold;">{}</span>',
            colors.get(obj.complexity, '#6c757d'),
            obj.get_complexity_display().upper()
        )
    complexity_badge.short_description = 'Complexity'
