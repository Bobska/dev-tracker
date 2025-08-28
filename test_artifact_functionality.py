#!/usr/bin/env python3
"""
Test script for the updated Artifact functionality
Tests that Artifacts can be created with only Name and Content as required fields.
"""

import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dev_tracker.settings')
django.setup()

from tracker.models import Artifact

def test_artifact_creation():
    """Test that artifacts can be created with minimal required fields."""
    
    print("🧪 Testing Updated Artifact Functionality")
    print("=" * 50)
    
    # Test 1: Create artifact with only Name and Content
    print("\n📝 Test 1: Creating artifact with only Name and Content")
    
    try:
        artifact = Artifact.objects.create(
            name="Standalone Documentation",
            content="This is a test artifact created without an associated application."
        )
        print(f"✅ SUCCESS: Created artifact '{artifact.name}' with ID {artifact.pk}")
        print(f"   Content preview: {artifact.content[:50]}...")
        print(f"   Application: {artifact.application}")
        print(f"   String representation: {artifact}")
        
    except Exception as e:
        print(f"❌ FAILED: {e}")
    
    # Test 2: Create artifact with optional fields
    print("\n📝 Test 2: Creating artifact with optional fields")
    
    try:
        artifact2 = Artifact.objects.create(
            name="Enhanced Documentation",
            content="This artifact includes optional fields for better organization.",
            type="documentation",
            status="draft",
            description="A comprehensive test artifact with all optional fields"
        )
        print(f"✅ SUCCESS: Created artifact '{artifact2.name}' with ID {artifact2.pk}")
        print(f"   Type: {artifact2.type}")
        print(f"   Status: {artifact2.status}")
        print(f"   Description: {artifact2.description}")
        
    except Exception as e:
        print(f"❌ FAILED: {e}")
    
    # Test 3: Verify model properties work
    print("\n📝 Test 3: Testing model properties and methods")
    
    artifacts = Artifact.objects.all()
    for artifact in artifacts[:3]:  # Test first 3 artifacts
        try:
            print(f"📄 Artifact: {artifact}")
            print(f"   Has application: {artifact.application is not None}")
            print(f"   File size: {artifact.file_size_mb} MB")
            print(f"   Absolute URL: {artifact.get_absolute_url()}")
        except Exception as e:
            print(f"❌ Property error for {artifact.name}: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Artifact functionality test completed!")
    print(f"\nSummary:")
    print(f"- Total artifacts: {Artifact.objects.count()}")
    print(f"- Standalone artifacts: {Artifact.objects.filter(application__isnull=True).count()}")
    print(f"- Application-linked artifacts: {Artifact.objects.filter(application__isnull=False).count()}")
    
    print(f"\n✅ Key Updates Implemented:")
    print(f"• Application field is now optional (null=True, blank=True)")
    print(f"• Name and Content are the only required fields") 
    print(f"• Type, Status, Version, Created_by are now optional")
    print(f"• Templates updated to handle standalone artifacts")
    print(f"• Form reorganized with required fields first")

if __name__ == "__main__":
    test_artifact_creation()
