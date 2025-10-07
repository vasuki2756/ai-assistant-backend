#!/usr/bin/env python3
"""
Simple Test Script for Student AI Agent Testing in Terminal
Run this to test different inputs with agents!
"""

import json
import requests
from typing import Dict, Any

def test_agent_with_input(user_input: str, student_id: str = "test_student") -> Dict[str, Any]:
    """Test the agent system with custom input."""
    try:
        url = "http://127.0.0.1:8000/study-plan"
        payload = {
            "user_input": user_input,
            "student_id": student_id
        }

        print("🤖 Sending request to agent system...")
        print(f"Input: {user_input}")
        print("-" * 50)

        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()

        data = response.json()
        return data

    except requests.exceptions.ConnectionError:
        print("❌ Error: Cannot connect to agent server. Make sure it's running on port 8000.")
        print("   Run: uvicorn backend.main:app --reload")
        return {}
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return {}

def format_response(data: Dict[str, Any]) -> None:
    """Format and display the agent response."""
    if not data:
        return

    print("\n🤖 STUDENT AI ASSISTANT RESPONSE:")
    print("=" * 60)

    # Greeting
    if 'greeting' in data:
        print(f"🙋 {data['greeting']}")
        print()

    # Study Plan
    if 'study_plan' in data and data['study_plan']:
        sp = data['study_plan']
        print('📅 STUDY PLAN:')
        print(f"   Subject: {sp.get('topic', 'Unknown')}")
        print(f"   Duration: {sp.get('duration', 'Unknown')}")
        print(f"   Difficulty: {sp.get('difficulty', 'Unknown')}")
        sessions = sp.get('sessions', [])
        if sessions:
            print("   Sessions:")
            for session in sessions[:3]:  # Show first 3
                print(f"     - {session.get('day', 'Day')}: {session.get('topic', 'Topic')} ({session.get('duration', '1h')})")
        print()

    # Learning Resources
    if 'learning_resources' in data and data['learning_resources']:
        lr = data['learning_resources']
        resources = lr.get('resources', [])
        if resources:
            print('📚 RECOMMENDED LEARNING RESOURCES:')
            for i, res in enumerate(resources[:3], 1):  # Show top 3
                platform = res.get('platform', 'Unknown')
                title = res.get('title', 'Untitled Resource')
                print(f'   {i}. [{platform}] {title}')
            print(f"   ⏱️  Estimated Time: {lr.get('estimated_time', '2 hours')}")
            print()

    # Assessment
    if 'assessment' in data and data['assessment']:
        assmt = data['assessment']
        if assmt.get('available_quiz'):
            print('🧠 ASSESSMENT:')
            print(f"   Quiz Available: Yes")
            print(f"   Questions: {assmt.get('question_count', 0)}")
            print(f"   Estimated Time: {assmt.get('estimated_time', '3 minutes')}")
            print()

    # Motivational Support
    if 'motivational_support' in data and data['motivational_support']:
        mot = data['motivational_support']
        primary_msg = mot.get('primary_message', 'You got this!')
        print('💪 MOTIVATIONAL SUPPORT:')
        print(f'   "{primary_msg}"')
        next_goal = mot.get('next_goal', {}).get('goal', 'Complete your first study session')
        print(f'   🎯 Next Goal: {next_goal}')
        print()

    # Wellness Insights
    if 'wellness_insights' in data and data['wellness_insights']:
        wellness = data['wellness_insights']
        print('🌱 WELLNESS INSIGHTS:')
        print(f"   Fatigue Level: {wellness.get('fatigue_level', 0.3):.1f}")
        print(f"   Emotional State: {wellness.get('emotional_state', 'focused')}")
        recommendations = wellness.get('recommendations', [])[:2]
        if recommendations:
            print("   💡 Recommendations:")
            for rec in recommendations:
                print(f"      - {rec}")
        print()

    print("-" * 60)

def interactive_test():
    """Run interactive testing."""
    print("🎯 STUDENT AI ASSISTANT - TERMINAL TESTER")
    print("=" * 60)
    print("Test different inputs with your AI agents!")
    print("Type 'quit' or 'exit' to stop.")
    print()

    while True:
        try:
            user_input = input("👤 Your request: ").strip()

            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye! Your AI agents are working perfectly!")
                break

            if not user_input:
                continue

            # Test the input
            response_data = test_agent_with_input(user_input)

            # Format and display
            format_response(response_data)

        except KeyboardInterrupt:
            print("\n👋 Test ended. Agents working well!")
            break
        except Exception as e:
            print(f"❌ Test error: {e}")

def demo_tests():
    """Run some demo tests."""
    test_inputs = [
        "Help me prepare for Python interview",
        "I need resources for learning machine learning",
        "Create a study plan for data structures",
        "What resources do you recommend for web development?"
    ]

    print("🎯 AGENT DEMO TESTS")
    print("=" * 60)

    for i, test_input in enumerate(test_inputs, 1):
        print(f"\nTest {i}: {test_input}")
        print("-" * 40)

        response_data = test_agent_with_input(test_input)
        format_response(response_data)

        # Small delay between tests
        import time
        time.sleep(1)

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        # Run demo tests
        demo_tests()
    else:
        # Run interactive mode
        interactive_test()
