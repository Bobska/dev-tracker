"""
FamilyHub Development Tracker - API URLs

RESTful API endpoints for AJAX functionality.
"""

from django.urls import path

from . import views

app_name = "api"

urlpatterns = [
    # Dashboard API endpoints
    path("stats/", views.api_stats, name="stats"),
    path("chart-data/", views.api_chart_data, name="chart_data"),
    # Search API (placeholder for future implementation)
    path("search/", views.search_view, name="search"),
]
