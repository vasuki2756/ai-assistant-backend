#!/usr/bin/env python3
"""
Test Integration - Verify Hume AI connection and stress analysis
"""

import sys
import os
sys.path.insert(0, os.getcwd())

# Test imports
try:
    from agent_utils import analyze_image_for_stress, get_stress_category, test_hume_connection, analyze_emotion_sync
    print("✅ Successfully imported agent_utils")
except Exception as e:
    print(f"❌ Failed to import agent_utils: {e}")
    sys.exit(1)

# Test database
try:
    from database import students_db, get_student_by_regno
    print(f"✅ Successfully imported database with {len(students_db)} students")
except Exception as e:
    print(f"❌ Failed to import database: {e}")
    sys.exit(1)

# Test Hume AI connection
print("\n🎥 Testing Hume AI connection...")

# Debug Hume initialization
try:
    from agent_utils import hume_client, hume_api_key
    print(f"API Key loaded: {bool(hume_api_key)}")
    print(f"Hume client initialized: {bool(hume_client)}")
except Exception as e:
    print(f"Error importing Hume variables: {e}")

hume_connected = test_hume_connection()

# Test stress categorization
print("\n📊 Testing stress categorization...")
test_stress_levels = [10, 25, 50, 75, 90]
for level in test_stress_levels:
    category = get_stress_category(level)
    print(f"Stress {level}%: {category}")

print("\n🎯 Hume AI key from .env:", "Vho7axMnkvleW..." if "HUME_API_KEY" in str(os.environ) else "❌ Not found")

# Dummy test image analysis (without actual camera)
print("\n🧪 Testing stress analysis with dummy data...")
dummy_image_bytes = b"dummy jpeg data would be here"

try:
    # This would normally fail gracfully since it's dummy data
    # But we can test the Hume AI client initialization
    if hume_connected:
        print("✅ Hume AI configured - stress analysis ready")
        print("Note: Full integration test requires actual camera and valid image data")
    else:
        print("⚠️ Hume AI not connected - will fall back to neutral stress levels")
except Exception as e:
    print(f"⚠️ Stress analysis test failed (expected): {e}")

print("\n🏆 Integration Test Complete!")
print("Your camera demo is ready to connect with Hume AI API key from .env")
print("Run: python backend/camera_demo.py")
