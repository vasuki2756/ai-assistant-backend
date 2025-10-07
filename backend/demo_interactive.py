#!/usr/bin/env python3
"""
Student AI Assistant - Interactive Demo Script
Run this to interact with your multi-agent system!
"""

import os
from dotenv import load_dotenv
load_dotenv()

def main():
    print("🎯 STUDENT AI ASSISTANT - INTERACTIVE DEMO")
    print("=" * 60)
    print("Your complete multi-agent system is ready!")
    print("Type your request or 'quit' to exit.")
    print()

    try:
        # Initialize system
        print("🔧 Initializing multi-agent system...")
        from orchestrator import create_study_assistant
        orchestrator = create_study_assistant(os.getenv('GEMINI_API_KEY') or 'demo')
        print("✅ System ready! Start talking with your AI assistant.")
        print("-" * 60)

        while True:
            # Get user input
            user_input = input("👤 You: ").strip()

            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye! Your Student AI Assistant is always here to help!")
                break

            if not user_input:
                continue

            print()
            print("🤖 Assistant is thinking...")

            try:
                # Process request
                result = orchestrator.process_request(user_input, 'interactive_user')

                # Display results
                print("🤖 STUDENT AI ASSISTANT RESPONSE:")
                print("-" * 40)

                if 'greeting' in result:
                    print(f"🙋 {result['greeting']}")
                    print()

                # Learning resources
                if 'learning_resources' in result:
                    lr = result['learning_resources']
                    if 'resources' in lr and lr['resources']:
                        print('📚 RECOMMENDED LEARNING RESOURCES:')
                        for i, res in enumerate(lr['resources'][:3], 1):  # Show top 3
                            platform = res.get('platform', 'Unknown')
                            title = res.get('title', 'Untitled Resource')
                            print(f'  {i}. [{platform}] {title}')
                        print()

                # Study plan
                if 'study_plan' in result:
                    sp = result['study_plan']
                    if 'sessions' in sp and sp['sessions']:
                        print('📅 YOUR PERSONALIZED STUDY PLAN:')
                        for session in sp['sessions']:
                            day = session.get('day', 'Day 1')
                            topic = session.get('topic', 'General Topic')
                            duration = session.get('duration', '1 hour')
                            print(f'  📆 {day}: {topic} ({duration})')
                        print()

                # Motivation
                if 'motivation' in result:
                    mot = result['motivation']
                    if 'primary_message' in mot:
                        print('💪 ENCOURAGEMENT:')
                        print(f'  "{mot["primary_message"]}"')
                        if 'next_goal' in mot and 'goal' in mot['next_goal']:
                            print(f'  🎯 Next: {mot["next_goal"]["goal"]}')
                        print()

                print("-" * 60)

            except Exception as e:
                print(f"❌ Error processing request: {str(e)[:100]}...")
                print("The system may need API keys or there could be a temporary issue.")

    except KeyboardInterrupt:
        print("\n👋 Demo ended. Your system is working perfectly!")

    except Exception as e:
        print(f"\n❌ System initialization error: {str(e)[:150]}...")
        print("Make sure all dependencies are installed and API keys are configured.")

if __name__ == "__main__":
    main()
