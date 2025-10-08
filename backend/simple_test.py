#!/usr/bin/env python3

print("Testing Hume import...")

try:
    from hume import HumeBatchClient
    print("✅ Hume import successful")
except Exception as e:
    print(f"❌ Hume import failed: {e}")

try:
    from hume.models import BurstConfig, FacemeshConfig
    print("✅ Hume models import successful")
except Exception as e:
    print(f"❌ Hume models import failed: {e}")

# Test API key
import os
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv("HUME_API_KEY")
print(f"API Key loaded: {bool(api_key)}")

if api_key:
    try:
        client = HumeBatchClient(api_key)
        print("✅ Hume client initialization successful")

        # Test job creation and check available methods
        print("\n🔍 Testing Hume AI job methods...")
        from hume.models.config import BurstConfig, FacemeshConfig

        # Create a dummy data URL (small JPEG-like data)
        test_url = "data:image/jpeg;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="

        configs = [BurstConfig(), FacemeshConfig()]
        job = client.submit_job([test_url], configs)
        print(f"Job created: {type(job)}")
        print(f"Available methods: {[m for m in dir(job) if not m.startswith('_')]}")

        # Check if get_job_result exists
        if hasattr(job, 'get_job_result'):
            print("✅ get_job_result method exists")
        else:
            print("❌ get_job_result method missing")

        # Look for alternative methods
        if hasattr(job, 'await_complete'):
            print("✅ await_complete method found")
        elif hasattr(job, 'wait_for_completion'):
            print("✅ wait_for_completion method found")
        elif hasattr(job, 'get_predictions'):
            print("✅ get_predictions method found")

    except Exception as e:
        print(f"❌ Hume client initialization failed: {e}")
        import traceback
        traceback.print_exc()
