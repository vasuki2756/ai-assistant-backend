"""Assessment Agent - Generates quizzes and evaluates understanding."""

from typing import Dict, List, Any
import random
import json
import google.generativeai as genai

class AssessmentAgent:
    """Agent for creating assessments and evaluating student progress."""

    def __init__(self, gemini_api_key: str):
        genai.configure(api_key=gemini_api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')

    def generate_quiz(self, topic: str, learning_data: Dict[str, Any], num_questions: int = 5) -> Dict[str, Any]:
        """Generate a quiz based on learning resources and topic."""
        import asyncio

        # Create the event loop and run the async function
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If event loop is already running, use synchronous approach
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, self._generate_quiz_async(topic, learning_data, num_questions))
                    return future.result()
            else:
                return loop.run_until_complete(self._generate_quiz_async(topic, learning_data, num_questions))
        except:
            # Fallback to basic quiz generation if async fails
            return self._generate_basic_quiz(topic, learning_data, num_questions)

    async def _generate_quiz_async(self, topic: str, learning_data: Dict[str, Any], num_questions: int = 5) -> Dict[str, Any]:
        """Generate a quiz asynchronously."""
        resources = learning_data.get("resources", [])
        difficulty = learning_data.get("difficulty", "intermediate")

        quiz = {
            "topic": topic,
            "difficulty": difficulty,
            "questions": [],
            "total_questions": num_questions,
            "estimated_time": f"{num_questions * 2} minutes"
        }

        # Extract key concepts from resources
        concepts = self._extract_concepts(resources, topic)

        # Generate questions concurrently
        tasks = []
        for i in range(num_questions):
            question_type = self._choose_question_type(difficulty)
            task = self._create_question_async(question_type, concepts, topic)
            tasks.append(task)

        questions = await asyncio.gather(*tasks)
        quiz["questions"] = questions

        return quiz

    def _generate_basic_quiz(self, topic: str, learning_data: Dict[str, Any], num_questions: int = 5) -> Dict[str, Any]:
        """Generate a basic quiz as fallback."""
        concepts = self._extract_concepts(learning_data.get("resources", []), topic)

        questions = []
        for i in range(num_questions):
            concept = random.choice(concepts) if concepts else "programming"
            question_type = self._choose_question_type(learning_data.get("difficulty", "intermediate"))

            if question_type == "multiple_choice":
                question = {
                    "id": f"q_{random.randint(1000, 9999)}",
                    "type": "multiple_choice",
                    "topic": topic,
                    "question": f"What is {concept}?",
                    "options": ["Option A", "Option B", concept, "Option D"],
                    "correct_answer": 2,
                    "explanation": f"{concept} is a key concept."
                }
            else:
                question = {
                    "id": f"q_{random.randint(1000, 9999)}",
                    "type": question_type,
                    "topic": topic,
                    "question": f"{concept} is important in programming.",
                    "correct_answer": True,
                    "explanation": "This is a basic concept."
                }
            questions.append(question)

        return {
            "topic": topic,
            "difficulty": learning_data.get("difficulty", "intermediate"),
            "questions": questions,
            "total_questions": num_questions,
            "estimated_time": f"{num_questions * 2} minutes"
        }

    def _extract_concepts(self, resources: List[Dict], topic: str) -> List[str]:
        """Extract key concepts from learning resources."""
        concepts = []

        # Fallback concepts based on topic
        fallback_concepts = {
            "machine learning": [
                "supervised learning", "unsupervised learning", "reinforcement learning",
                "neural networks", "decision trees", "support vector machines",
                "regression", "classification", "clustering", "gradient descent"
            ],
            "data science": [
                "data cleaning", "feature engineering", "model evaluation",
                "cross-validation", "overfitting", "bias-variance tradeoff"
            ],
            "deep learning": [
                "convolutional neural networks", "recurrent neural networks",
                "transformers", "backpropagation", "activation functions"
            ]
        }

        topic_lower = topic.lower()
        for key, concepts_list in fallback_concepts.items():
            if key in topic_lower:
                concepts.extend(concepts_list)
                break

        if not concepts:
            # Generic concepts
            concepts = ["algorithms", "data structures", "problem solving", "analysis", "optimization"]

        return concepts[:10]  # Limit to 10 concepts

    def _choose_question_type(self, difficulty: str) -> str:
        """Choose appropriate question type based on difficulty."""
        if difficulty == "beginner":
            types = ["multiple_choice", "true_false", "multiple_choice"]
        elif difficulty == "intermediate":
            types = ["multiple_choice", "fill_blank", "true_false"]
        else:  # advanced
            types = ["fill_blank", "multiple_choice", "true_false", "fill_blank"]

        return random.choice(types)

    async def _create_question_async(self, q_type: str, concepts: List[str], topic: str) -> Dict[str, Any]:
        """Create a single question asynchronously."""
        question = {
            "id": f"q_{random.randint(1000, 9999)}",
            "type": q_type,
            "topic": topic
        }

        if q_type == "multiple_choice":
            question.update(await self._create_mc_question(topic, concepts))
        elif q_type == "true_false":
            question.update(await self._create_tf_question(topic, concepts))
        elif q_type == "fill_blank":
            question.update(await self._create_fb_question(topic, concepts))

        return question

    async def _create_mc_question(self, topic: str, concepts: List[str]) -> Dict[str, Any]:
        """Create multiple choice question using Gemini."""
        concept = random.choice(concepts)

        try:
            prompt = f"""Create a multiple choice question about {concept} in the context of {topic}.

Return a JSON object with:
- question: The question text
- options: Array of 4 options (A, B, C, D)
- correct_answer: Index (0-3) of the correct answer
- explanation: Brief explanation of why the answer is correct

Return ONLY the JSON object, no other text."""

            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=300
                )
            )

            content = response.text
            if content:
                try:
                    # Clean content if needed
                    content = content.strip()
                    if content.startswith('```json'):
                        content = content[7:]
                    if content.endswith('```'):
                        content = content[:-3]
                    content = content.strip()

                    q_data = json.loads(content)
                    return {
                        "question": q_data["question"],
                        "options": q_data["options"],
                        "correct_answer": q_data["correct_answer"],
                        "explanation": q_data.get("explanation", f"{concept} is a key concept in this topic.")
                    }
                except Exception as parse_error:
                    print(f"MC JSON parse error: {parse_error}")
                    pass
        except Exception as e:
            print(f"MC question generation error: {e}")

        # Fallback
        return {
            "question": f"What is the primary purpose of {concept}?",
            "options": ["Option A", "Option B", concept, "Option D"],
            "correct_answer": 2,
            "explanation": f"{concept} is a fundamental concept in this topic."
        }

    async def _create_tf_question(self, topic: str, concepts: List[str]) -> Dict[str, Any]:
        """Create true/false question using Gemini."""
        concept = random.choice(concepts)

        try:
            prompt = f"""Create a true/false question about {concept} in the context of {topic}.

Return a JSON object with:
- question: The true/false statement
- correct_answer: boolean (true/false)
- explanation: Brief explanation

Return ONLY the JSON object, no other text."""

            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=200
                )
            )

            content = response.text
            if content:
                try:
                    # Clean content if needed
                    content = content.strip()
                    if content.startswith('```json'):
                        content = content[7:]
                    if content.endswith('```'):
                        content = content[:-3]
                    content = content.strip()

                    q_data = json.loads(content)
                    return {
                        "question": q_data["question"],
                        "correct_answer": q_data["correct_answer"],
                        "explanation": q_data.get("explanation", f"This statement about {concept} is {'correct' if q_data.get('correct_answer', False) else 'incorrect'}.")
                    }
                except Exception as parse_error:
                    print(f"TF JSON parse error: {parse_error}")
                    pass
        except Exception as e:
            print(f"TF question generation error: {e}")

        # Fallback
        return {
            "question": f"{concept} is a fundamental concept in computer science.",
            "correct_answer": True,
            "explanation": f"This statement about {concept} is correct."
        }

    async def _create_fb_question(self, topic: str, concepts: List[str]) -> Dict[str, Any]:
        """Create fill in the blank question using Gemini."""
        concept = random.choice(concepts)

        try:
            prompt = f"""Create a fill-in-the-blank question about {concept} in the context of {topic}.

Return a JSON object with:
- question: Question with _____ where the blank should be
- correct_answer: The word/phrase that fills the blank
- explanation: Brief explanation of the answer

Return ONLY the JSON object, no other text."""

            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=200
                )
            )

            content = response.text
            if content:
                try:
                    # Clean content if needed
                    content = content.strip()
                    if content.startswith('```json'):
                        content = content[7:]
                    if content.endswith('```'):
                        content = content[:-3]
                    content = content.strip()

                    q_data = json.loads(content)
                    return {
                        "question": q_data["question"],
                        "correct_answer": q_data["correct_answer"],
                        "explanation": q_data.get("explanation", f"The correct answer describes {concept}.")
                    }
                except Exception as parse_error:
                    print(f"FB JSON parse error: {parse_error}")
                    pass
        except Exception as e:
            print(f"FB question generation error: {e}")

        # Fallback
        return {
            "question": f"{concept} is a technique used to _____.",
            "correct_answer": "solve computational problems",
            "explanation": f"{concept} is designed to solve computational problems."
        }

    def evaluate_answers(self, quiz: Dict[str, Any], student_answers: List[Any]) -> Dict[str, Any]:
        """Evaluate student answers and provide feedback."""
        questions = quiz["questions"]
        total_questions = len(questions)
        correct_count = 0
        detailed_feedback = []

        for i, (question, answer) in enumerate(zip(questions, student_answers)):
            is_correct = self._check_answer(question, answer)
            if is_correct:
                correct_count += 1

            feedback = {
                "question_id": question["id"],
                "correct": is_correct,
                "student_answer": answer,
                "correct_answer": question.get("correct_answer"),
                "explanation": question.get("explanation", "")
            }
            detailed_feedback.append(feedback)

        score_percentage = (correct_count / total_questions) * 100

        # Generate performance analysis
        performance = self._analyze_performance(score_percentage, quiz["difficulty"])

        return {
            "score": score_percentage,
            "correct_answers": correct_count,
            "total_questions": total_questions,
            "performance_level": performance["level"],
            "feedback": performance["feedback"],
            "recommendations": performance["recommendations"],
            "detailed_feedback": detailed_feedback
        }

    def _check_answer(self, question: Dict[str, Any], answer: Any) -> bool:
        """Check if student answer is correct."""
        correct_answer = question.get("correct_answer")

        if question["type"] == "multiple_choice":
            return answer == correct_answer
        elif question["type"] == "true_false":
            return answer == correct_answer
        elif question["type"] == "fill_blank":
            # Simple string matching (in real implementation would be more sophisticated)
            return answer.lower().strip() in correct_answer.lower()

        return False

    def _analyze_performance(self, score: float, difficulty: str) -> Dict[str, Any]:
        """Analyze student performance and provide feedback."""
        if difficulty == "beginner":
            thresholds = {"excellent": 90, "good": 75, "needs_work": 60}
        elif difficulty == "intermediate":
            thresholds = {"excellent": 85, "good": 70, "needs_work": 55}
        else:  # advanced
            thresholds = {"excellent": 80, "good": 65, "needs_work": 50}

        if score >= thresholds["excellent"]:
            level = "excellent"
            feedback = "Outstanding performance! You have a strong grasp of the material."
            recommendations = ["Consider advancing to more challenging material", "Help peers who are struggling"]
        elif score >= thresholds["good"]:
            level = "good"
            feedback = "Good work! You understand most concepts but could benefit from more practice."
            recommendations = ["Review the concepts you missed", "Practice with similar problems"]
        else:
            level = "needs_improvement"
            feedback = "Keep working on these concepts. Practice and review will help improve your understanding."
            recommendations = ["Revisit the learning resources", "Focus on fundamental concepts", "Ask for clarification on difficult topics"]

        return {
            "level": level,
            "feedback": feedback,
            "recommendations": recommendations
        }

def generate_quiz(topic: str, learning_data: Dict[str, Any], num_questions: int = 5, api_key: str = None) -> Dict[str, Any]:
    """Helper function to generate a quiz."""
    agent = AssessmentAgent(api_key)
    return agent.generate_quiz(topic, learning_data, num_questions)
