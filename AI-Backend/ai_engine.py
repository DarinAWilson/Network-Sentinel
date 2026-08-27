import json
import os

from openai import OpenAI

from ai_cache import get_cached_explanation, save_explanation
from ai_usage import can_make_ai_request, record_ai_request


client = OpenAI()

MODEL = os.getenv("OPENAI_MODEL")

MAX_OUTPUT_TOKENS = int(
    os.getenv("AI_MAX_OUTPUT_TOKENS", "800")
)

if not MODEL:
    raise RuntimeError("OPENAI_MODEL environment variable is required")


def should_analyze_alert(alert):
    """
    Decide whether an alert is noteworthy enough for AI analysis.
    """

    risk = alert.get("risk", "Unknown")
    title = alert.get("title", "").lower()

    threat_intel = alert.get("threat_intel", {})
    known_bad_match = threat_intel.get(
        "known_bad_match",
        False
    )

    # A threat-intelligence match is always noteworthy.
    if known_bad_match:
        return True

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

    return any(
        keyword in title
        for keyword in noteworthy_keywords
    )


def generate_explanation(alert, force=False):
    """
    Analyze a Network Sentinel alert with OpenAI and return
    a structured plain-English security explanation.

    Reuses cached generic explanations when available.
    """

    title = alert.get(
        "title",
        "Unknown Security Event"
    )

    risk = alert.get(
        "risk",
        "Unknown"
    )

    source = alert.get(
        "source",
        "Unknown"
    )

    target = alert.get(
        "target",
        "Unknown"
    )

    threat_intel = alert.get(
        "threat_intel",
        {}
    )

    known_bad_match = threat_intel.get(
        "known_bad_match",
        False
    )

    threat_intel_source = threat_intel.get(
        "source_name",
        "Configured threat-intelligence feed"
    )


    if not force and not should_analyze_alert(alert):
        return {
            "title": title,
            "risk": risk,
            "source": source,
            "target": target,
            "known_bad_match": known_bad_match,
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
            "cache_hit": False,
            "usage_limited": False
        }


    cached = get_cached_explanation(alert)

    if cached:
        return {
            "title": title,
            "risk": risk,
            "source": source,
            "target": target,
            "known_bad_match": known_bad_match,
            "analysis": cached["analysis"],
            "why_it_matters": cached["why_it_matters"],
            "recommended_actions": cached["recommended_actions"],
            "ai_analyzed": True,
            "cache_hit": True,
            "usage_limited": False
        }


    if not can_make_ai_request():
        return {
            "title": title,
            "risk": risk,
            "source": source,
            "target": target,
            "known_bad_match": known_bad_match,
            "analysis": (
                "AI analysis is temporarily unavailable because the daily "
                "Network Sentinel AI usage limit has been reached."
            ),
            "why_it_matters": (
                "The underlying security alert is still available for review. "
                "The usage limit prevents unexpected API spending."
            ),
            "recommended_actions": [
                "Review the original Suricata alert.",
                "Try the AI analysis again after the daily limit resets."
            ],
            "ai_analyzed": False,
            "cache_hit": False,
            "usage_limited": True
        }


    prompt = f"""
You are the security explanation engine for Network Sentinel.

Network Sentinel is designed for small-business IT administrators who may not
have dedicated cybersecurity staff.

Analyze the following security alert:

Title: {title}
Risk: {risk}
Threat Intelligence Match: {known_bad_match}
Threat Intelligence Source: {threat_intel_source}

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
- Do not claim a system is compromised unless the evidence proves it.
- Clearly acknowledge when an alert may have a benign explanation.
- Give no more than 3 recommended actions.
- Keep the response concise.
- Do not include source IP addresses, destination IP addresses,
  customer identifiers, hostnames, timestamps, or other
  event-specific identifiers in the explanation.
- Explain the alert generically so the explanation can safely
  be reused for another customer experiencing the same alert type.
- If Threat Intelligence Match is true, explain that the source
  or destination matched the configured known-bad threat-intelligence feed.
- Treat a known-bad match as meaningful additional context,
  but do not claim compromise solely because of the match.
- If Threat Intelligence Match is false, do not mention
  threat intelligence.
"""


    try:
        response = client.responses.create(
            model=MODEL,
            input=prompt,
            max_output_tokens=MAX_OUTPUT_TOKENS
        )

        usage = getattr(
            response,
            "usage",
            None
        )

        input_tokens = (
            getattr(usage, "input_tokens", 0)
            if usage else 0
        )

        output_tokens = (
            getattr(usage, "output_tokens", 0)
            if usage else 0
        )

        total_tokens = (
            getattr(usage, "total_tokens", 0)
            if usage else 0
        )


        ai_result = json.loads(
            response.output_text
        )


        if not isinstance(ai_result, dict):
            raise ValueError(
                "AI response was not a JSON object"
            )


        analysis = ai_result.get(
            "analysis"
        )

        why_it_matters = ai_result.get(
            "why_it_matters"
        )

        recommended_actions = ai_result.get(
            "recommended_actions"
        )


        if (
            not isinstance(analysis, str)
            or not analysis.strip()
        ):
            raise ValueError(
                "AI response missing valid analysis"
            )


        if (
            not isinstance(why_it_matters, str)
            or not why_it_matters.strip()
        ):
            raise ValueError(
                "AI response missing valid why_it_matters"
            )


        if not isinstance(
            recommended_actions,
            list
        ):
            raise ValueError(
                "AI response recommended_actions was not a list"
            )


        clean_actions = [
            action.strip()
            for action in recommended_actions
            if isinstance(action, str)
            and action.strip()
        ][:3]


        if not clean_actions:
            raise ValueError(
                "AI response contained no valid recommended actions"
            )


        reusable_explanation = {
            "analysis": analysis.strip(),
            "why_it_matters": why_it_matters.strip(),
            "recommended_actions": clean_actions
        }


        record_ai_request(
            model=MODEL,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            success=True
        )


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
            "known_bad_match": known_bad_match,
            "analysis": reusable_explanation["analysis"],
            "why_it_matters": reusable_explanation["why_it_matters"],
            "recommended_actions": reusable_explanation[
                "recommended_actions"
            ],
            "ai_analyzed": True,
            "cache_hit": False,
            "usage_limited": False
        }


    except Exception as exc:
        record_ai_request(
            model=MODEL,
            success=False
        )

        return {
            "title": title,
            "risk": risk,
            "source": source,
            "target": target,
            "known_bad_match": known_bad_match,
            "analysis": (
                "AI analysis is temporarily unavailable."
            ),
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
            "usage_limited": False,
            "ai_error": str(exc)
        }