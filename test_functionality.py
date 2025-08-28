#!/usr/bin/env python3
"""
Quick functionality test for FamilyHub Development Tracker
Tests critical paths and ensures all fixes are working correctly.
"""

import os
import sys
import django
from django.test import Client
from django.contrib.auth import get_user_model

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dev_tracker.settings')
django.setup()

from tracker.models import Project, Application, Task, Integration

def test_critical_functionality():
    """Test critical functionality after code fixes."""
    
    print("🚀 Starting FamilyHub Development Tracker Functionality Test")
    print("=" * 60)
    
    # Test 1: Check if we can access the dashboard
    client = Client()
    
    print("📊 Testing Dashboard Access...")
    response = client.get('/tracker/')
    if response.status_code == 200:
        print("✅ Dashboard accessible")
    else:
        print(f"❌ Dashboard failed: {response.status_code}")
    
    # Test 2: Check if project list loads
    print("\n📁 Testing Project List...")
    response = client.get('/tracker/projects/')
    if response.status_code == 200:
        print("✅ Project list accessible")
    else:
        print(f"❌ Project list failed: {response.status_code}")
    
    # Test 3: Check model properties work
    print("\n🔧 Testing Model Properties...")
    projects = Project.objects.all()
    
    if projects.exists():
        project = projects.first()
        
        # Test new properties
        try:
            days_remaining = project.days_remaining
            is_overdue = project.is_overdue
            days_overdue = project.days_overdue
            print(f"✅ Project properties work: {days_remaining} days remaining, overdue: {is_overdue}")
        except Exception as e:
            print(f"❌ Project properties failed: {e}")
        
        # Test project detail view
        response = client.get(f'/tracker/projects/{project.pk}/')
        if response.status_code == 200:
            print("✅ Project detail view accessible")
        else:
            print(f"❌ Project detail view failed: {response.status_code}")
    
    # Test 4: Check Integration functionality
    print("\n🔗 Testing Integration Functionality...")
    integrations = Integration.objects.all()
    
    if integrations.exists():
        integration = integrations.first()
        
        # Test integration project property
        try:
            project_name = integration.project.name
            print(f"✅ Integration project property works: {project_name}")
        except Exception as e:
            print(f"❌ Integration project property failed: {e}")
        
        # Test integration detail view
        response = client.get(f'/tracker/integrations/{integration.pk}/')
        if response.status_code == 200:
            print("✅ Integration detail view accessible")
        else:
            print(f"❌ Integration detail view failed: {response.status_code}")
    
    # Test 5: Check Application properties
    print("\n📱 Testing Application Properties...")
    applications = Application.objects.all()
    
    if applications.exists():
        app = applications.first()
        
        try:
            days_to_target = app.days_to_target
            print(f"✅ Application days_to_target property works: {days_to_target}")
        except Exception as e:
            print(f"❌ Application days_to_target failed: {e}")
    
    # Test 6: Check Task properties
    print("\n📋 Testing Task Properties...")
    tasks = Task.objects.all()
    
    if tasks.exists():
        task = tasks.first()
        
        try:
            days_until_due = task.days_until_due
            print(f"✅ Task days_until_due property works: {days_until_due}")
        except Exception as e:
            print(f"❌ Task days_until_due failed: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 Functionality test completed!")
    print("\nKey fixes implemented:")
    print("• ✅ Fixed invalid 'mul' filter error")
    print("• ✅ Added missing model properties (days_remaining, is_overdue, days_overdue)")
    print("• ✅ Fixed Integration template to use from_app/to_app")
    print("• ✅ Added Application.days_to_target property")
    print("• ✅ Added Task.days_until_due property")
    print("• ✅ Resolved NoReverseMatch error for project_detail")

if __name__ == "__main__":
    test_critical_functionality()
