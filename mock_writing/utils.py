import openai
import re
from decimal import Decimal, InvalidOperation
from django.conf import settings

openai.api_key = settings.OPENAI_API_KEY

def check_writing_answer_with_ai(answer_text, task_number, writing_topic_or_data):
    if task_number not in [1, 2]:
        raise ValueError("Task number must be 1 or 2.")

    model = "gpt-4"

    # Task description
    if task_number == 1:
        task_description = "Describe, summarize or explain visual information such as a graph, chart, table, or process."
        prompt_topic = f"Information to analyze: {writing_topic_or_data}"
    else:
        task_description = "Present an argument or opinion in response to a point of view, problem, or issue."
        prompt_topic = f"Essay Topic: {writing_topic_or_data}"

    prompt = f"""
You are a certified IELTS writing examiner. Evaluate the essay below using official IELTS Writing Task {task_number} band descriptors.

First, analyze whether the essay addresses the expected requirements for Task {task_number}:
- If the essay answers the given prompt appropriately and thoroughly.

Then evaluate it using these four criteria (score each 0.0 to 9.0):

1. Task Response
2. Coherence and Cohesion
3. Lexical Resource
4. Grammatical Range and Accuracy

Finally, provide an Overall Band Score and constructive Feedback.

Use this format exactly:

Task Response: X.X – ...
Coherence and Cohesion: X.X – ...
Lexical Resource: X.X – ...
Grammatical Range and Accuracy: X.X – ...
Overall Band Score: X.X
Feedback: (your detailed suggestions)

Make sure to check if the essay directly addresses the given topic. If not, mention it in the feedback.

Essay Topic: {writing_topic_or_data}

Essay:
\"\"\"{answer_text}\"\"\" 
    """

    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[{"role": "system", "content": "You are a certified IELTS examiner."},
                      {"role": "user", "content": prompt}]
        )
        ai_reply = response.choices[0].message["content"]
        return ai_reply
    except openai.error.OpenAIError as e:
        return f"Error with OpenAI API: {e}"


def parse_ai_feedback(ai_text):
    result = {
        "task_response": {"score": None, "feedback": ""},
        "coherence_and_cohesion": {"score": None, "feedback": ""},
        "lexical_resource": {"score": None, "feedback": ""},
        "grammatical_range_and_accuracy": {"score": None, "feedback": ""},
        "overall_band": None,
        "overall_feedback": "",
        "topic_relevance": ""  # Add topic relevance feedback here
    }

    # Define regex patterns for extracting the feedback
    patterns = {
        "task_response": r"(?i)task response\s*[:\-]?\s*(\d(?:\.\d)?)\s*[-–—]?\s*(.*?)\n",
        "coherence_and_cohesion": r"(?i)coherence and cohesion\s*[:\-]?\s*(\d(?:\.\d)?)\s*[-–—]?\s*(.*?)\n",
        "lexical_resource": r"(?i)lexical resource\s*[:\-]?\s*(\d(?:\.\d)?)\s*[-–—]?\s*(.*?)\n",
        "grammatical_range_and_accuracy": r"(?i)grammatical range and accuracy\s*[:\-]?\s*(\d(?:\.\d)?)\s*[-–—]?\s*(.*?)\n",
        "overall_band": r"(?i)overall band score\s*[:\-]?\s*(\d(?:\.\d)?)",
        "overall_feedback": r"(?i)feedback\s*[:\-]?\s*(.*)",
        "topic_relevance": r"(?i)topic relevance\s*[:\-]?\s*(.*?)\n"  # Added topic relevance
    }

    total_score = 0
    num_criteria = 0

    # Search for each feedback part using regex
    for key, pattern in patterns.items():
        match = re.search(pattern, ai_text, re.DOTALL)
        if match:
            if key == "overall_band":
                try:
                    result[key] = round(Decimal(match.group(1).strip()) * 2) / 2
                except InvalidOperation:
                    result[key] = None
            elif key == "overall_feedback":
                result[key] = match.group(1).strip()
            elif key == "topic_relevance":
                result[key] = match.group(1).strip()  # Extract topic relevance feedback
            else:
                score = match.group(1).strip()
                feedback = match.group(2).strip()
                try:
                    score_value = Decimal(score)
                    result[key] = {"score": score_value, "feedback": feedback}
                    total_score += score_value
                    num_criteria += 1
                except InvalidOperation:
                    result[key] = {"score": None, "feedback": feedback}

    # Calculate the overall band score based on average of individual scores
    if num_criteria > 0:
        average_score = total_score / num_criteria
        result["overall_band"] = round(average_score * 2) / 2

    result = {
        "task_response": result["task_response"],
        "coherence_and_cohesion": result["coherence_and_cohesion"],
        "lexical_resource": result["lexical_resource"],
        "grammatical_range_and_accuracy": result["grammatical_range_and_accuracy"],
        "overall_band": result["overall_band"],
        "overall_feedback": result["overall_feedback"],
        "topic_relevance": result["topic_relevance"]  # Added topic relevance in final result
    }

    return result
