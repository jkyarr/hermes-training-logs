#!/usr/bin/env python3
"""
Simple Prompt Router for early token cost reduction.

Lightweight, rule-based router to handle common/repetitive queries without calling the LLM.

Designed for the mental health clinic app context (HARNESS, workbooks, appointments, etc.).

Can be extended with more rules or a small ML classifier later.
"""

import re
from typing import Tuple, Optional

# Routes: list of (pattern or keywords, response)
# Using simple keyword matching for speed and simplicity (no LLM needed).

ROUTES = [
    # Greetings and meta
    {
        "name": "greeting",
        "keywords": ["hello", "hi", "hey", "good morning", "good afternoon"],
        "response": "Hello! I'm here to help with your mental health journey using the app's tools and resources. How can I assist you today?"
    },
    {
        "name": "meta_what_can_you_do",
        "keywords": ["what can you do", "help me", "capabilities", "features"],
        "response": "I can answer questions about the app, guide you through workbooks (e.g. anxiety, co-parenting), help with assessments, and provide evidence-based suggestions from the clinical manuals. For complex or personal issues, I may suggest consulting your therapist or the full resources."
    },
    # App specific - appointments
    {
        "name": "book_appointment",
        "keywords": ["book appointment", "schedule session", "make appointment", "book a session"],
        "response": "To book an appointment, open the app, go to the 'Schedule' tab, select an available slot with your preferred clinician, and confirm. You can also call the clinic front desk for assistance."
    },
    {
        "name": "cancel_appointment",
        "keywords": ["cancel appointment", "reschedule", "change appointment"],
        "response": "To cancel or reschedule, go to 'My Appointments' in the app, select the appointment, and choose cancel or reschedule. Please give at least 24 hours notice when possible to avoid fees."
    },
    # Login / account
    {
        "name": "reset_password",
        "keywords": ["reset password", "forgot password", "can't login", "account issue"],
        "response": "To reset your password, on the login screen tap 'Forgot Password?', enter your email, and follow the instructions sent to you. If you don't receive the email, check spam or contact support@clinic.example.com."
    },
    # General app
    {
        "name": "how_to_use_workbook",
        "keywords": ["how to use workbook", "start workbook", "workbook guide"],
        "response": "To start a workbook (e.g. Anxiety or Co-Parenting), go to the 'Resources' or 'Workbooks' section in the app. Choose a module, read the content, and complete the interactive exercises. Progress is saved automatically."
    },
    {
        "name": "privacy_data",
        "keywords": ["privacy", "data security", "hipaa", "my data"],
        "response": "Your data is stored locally on your device and in our secure, self-hosted systems. We follow strict privacy practices aligned with clinical standards. No data is shared with third parties without your consent. See the app's Privacy Policy for full details."
    },
]

def route_prompt(user_prompt: str) -> Tuple[Optional[str], bool]:
    """
    Route the prompt. Returns (response_text or None, used_llm: bool)
    If response_text is not None, it was handled without LLM.
    """
    if not user_prompt or not user_prompt.strip():
        return "I didn't receive a question. How can I help?", False

    prompt_lower = user_prompt.lower().strip()

    for route in ROUTES:
        for kw in route["keywords"]:
            if kw in prompt_lower:
                return route["response"], False

    # No match - needs LLM
    return None, True

def get_route_explanation() -> str:
    """For debugging or admin view."""
    return "Router uses simple keyword matching on " + str(len(ROUTES)) + " routes for common queries."

if __name__ == "__main__":
    # Quick self test
    tests = [
        "Hello there!",
        "How do I book an appointment?",
        "What can you do?",
        "Tell me about the anxiety workbook",
        "What is the meaning of life?"  # should route to LLM
    ]
    for t in tests:
        resp, used_llm = route_prompt(t)
        print(f"Prompt: {t}")
        print(f"  Routed: {not used_llm} | Response: {resp[:80]}..." if resp else "  Needs LLM")
        print()