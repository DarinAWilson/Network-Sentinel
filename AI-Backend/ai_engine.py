import json
import os

from openai import OpenAI
from ai_cache import get_cached_explanation, save_explanation


client = OpenAI()

MODEL = os.getenv("OPENAI_MODEL")

if not MODEL:
    raise RuntimeError("OPENAI_MODEL environment variable is required")


def should_analyze_alert(alert):
    """
    Decide whether an alert is noteworthy enough for AI analysis.
    """

    risk = alert.get("risk", "Unknown")
    title = alert.get("title", "").lower()

    # Always analyze higher-risk alerts.
    if risk in ["High", "Medium"]:
        return True

    # Allow certain suspicious low-risk patterns.
    noteworthy_keywords = [
        "scan",
        "malware",
        "trojan",
        "exploit",
        "command and control",
        "credential",
        "brute force",
        "suspicious",
    ]

    return any(keyword in title for keyword in noteworthy_keywords)


def generate_explanation(alert, force=False):
    """
    Analyze a Network Sentinel alert with OpenAI and return
    a structured plain-English security explanation.

    Reuses cached generic explanations when available.
    """

    title = alert.get("title", "Unknown Security Event")
    risk = alert.get("risk", "Unknown")
    source = alert.get("source", "Unknown")
    target = alert.get("target", "Unknown")

    if not force and not should_analyze_alert(alert):
        return {
            "title": title,
            "risk": risk,
            "source": source,
            "target": target,
            "analysis": (
                "This alert was not automatically sent for AI analysis "
                "because it did not meet the current noteworthy-alert threshold."
            ),
            "why_it_matters": (
                "Network Sentinel keeps lower-value alerts available for review "
                "without spending AI usage on every routine event."
            ),
            "recommended_actions": [
                "Review the alert if the activity is unexpected.",
                "Monitor for repeated or higher-risk related events."
            ],
            "ai_analyzed": False,
            "cache_hit": False
        }

    cached = get_cached_explanation(alert)

    if cached:
        return {
            "title": title,
            "risk": risk,
            "source": source,
            "target": target,
            "analysis": cached["analysis"],
            "why_it_matters": cached["why_it_matters"],
            "recommended_actions": cached["recommended_actions"],
            "ai_analyzed": True,
            "cache_hit": True
        }

    prompt = f"""
You are the security explanation engine for Network Sentinel.

Network Sentinel is designed for small-business IT administrators who may not
have dedicated cybersecurity staff.

Analyze the following Suricata alert:

Title: {title}
Risk: {risk}
Source: {source}
Target: {target}

Return ONLY valid JSON using exactly this structure:

{{
  "analysis": "A concise plain-English explanation of what happened.",
  "why_it_matters": "A concise explanation of why this may matter.",
  "recommended_actions": [
    "Action 1",
    "Action 2",
    "Action 3"
  ]
}}

Rules:
- Use clear language for a non-specialist IT administrator.
- Do not exaggerate the severity.
- Do not claim a system is compromised unless the alert proves it.
- Clearly acknowledge when an alert may have a benign explanation.
- Give no more than 3 recommended actions.
- Keep the response concise.
- Do not include source IP addresses, destination IP addresses, customer identifiers,
  hostnames, timestamps, or other event-specific identifiers in the explanation.
- Explain the alert generically so the explanation can safely be reused for another
  customer experiencing the same alert type.
"""

    try:
        response = client.responses.create(
            model=MODEL,
            input=prompt
        )

        ai_result = json.loads(response.output_text)

        reusable_explanation = {
            "analysis": ai_result.get(
                "analysis",
                "No analysis returned."
            ),
            "why_it_matters": ai_result.get(
                "why_it_matters",
                "No additional context returned."
            ),
            "recommended_actions": ai_result.get(
                "recommended_actions",
                []
            )
        }

        save_explanation(
            alert,
            reusable_explanation,
            MODEL
        )

        return {
            "title": title,
            "risk": risk,
            "source": source,
            "target": target,
            "analysis": reusable_explanation["analysis"],
            "why_it_matters": reusable_explanation["why_it_matters"],
            "recommended_actions": reusable_explanation["recommended_actions"],
            "ai_analyzed": True,
            "cache_hit": False
        }

    except Exception as exc:
        return {
            "title": title,
            "risk": risk,
            "source": source,
            "target": target,
            "analysis": "AI analysis is temporarily unavailable.",
            "why_it_matters": (
                "The underlying security alert is still available even though "
                "the AI explanation service could not complete the request."
            ),
            "recommended_actions": [
                "Review the original Suricata alert.",
                "Try the AI analysis again later."
            ],
            "ai_analyzed": False,
            "cache_hit": False,
            "ai_error": str(exc)
        }