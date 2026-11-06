import re
from typing import List, Tuple, Dict, Any

RULES: List[Tuple[str, re.Pattern, int]] = [
    ("Instruction override", re.compile(r"ignore\s+(all\s+|any\s+)?(the\s+)?(previous|prior|above)\s+instructions|disregard\s+(all\s+|your\s+)?(previous\s+)?(instructions|rules)", re.IGNORECASE), 45),
    ("Hidden prompt disclosure", re.compile(r"(reveal|show|print|leak).{0,30}(system\s+prompt|hidden\s+(system\s+)?(prompt|instructions)|your\s+instructions)", re.IGNORECASE), 40),
    ("Safety bypass attempt", re.compile(r"bypass|jailbreak|disregard\s+.{0,20}safety", re.IGNORECASE), 35),
    ("Privilege escalation", re.compile(r"unrestricted|act\s+as\s+.{0,15}admin", re.IGNORECASE), 30),
    ("Data exfiltration", re.compile(r"(send|email|export|upload).{0,40}(confidential|customer\s+records|sensitive|protected)", re.IGNORECASE), 50),
]

# Sensitive data patterns with non-capturing groups so the complete match is extracted
PII: List[Tuple[str, re.Pattern]] = [
    ("Email address", re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+", re.IGNORECASE)),
    ("Phone number", re.compile(r"\+?\d[\d\s-]{8,}\d")),
    ("API key-like", re.compile(r"\b(?:sk|pk|AKIA)[-_A-Za-z0-9]{12,}\b")),
    ("Token-like", re.compile(r"\b[A-Za-z0-9_-]{32,}\b")),
]

def mask_text(val: str, enable_mask: bool) -> str:
    """Masks sensitive values, ensuring secrets are never displayed or stored in plaintext."""
    if enable_mask:
        if len(val) <= 4:
            return "••••"
        return val[:2] + ("•" * max(4, len(val) - 4)) + val[-2:]
    else:
        if len(val) <= 8:
            return val
        return val[:4] + "…" + val[-4:]

def calculate_risk_level(score: int) -> str:
    if score < 30:
        return "Low"
    elif score < 60:
        return "Medium"
    elif score < 80:
        return "High"
    return "Critical"

def analyze_prompt(text: str, sensitivity: float = 1.0, auto_block: bool = True, high_risk_approval: bool = True, mask_pii: bool = True) -> Dict[str, Any]:
    score = 0
    hits: List[str] = []
    pii_found: List[List[str]] = []

    # Check instruction patterns
    for name, pattern, weight in RULES:
        if pattern.search(text):
            hits.append(name)
            score += weight

    # Check sensitive data patterns using finditer to capture the full matched string
    for name, pattern in PII:
        for match in pattern.finditer(text):
            full_match = match.group(0)
            masked_val = mask_text(full_match, mask_pii)
            pii_found.append([name, masked_val])
            score += 15

    # Scale score with sensitivity multiplier
    raw_score = score
    score = min(100, int(round(score * sensitivity)))
    level = calculate_risk_level(score)

    if score < 30:
        classification = "SAFE"
    elif score < 60:
        classification = "SUSPICIOUS"
    else:
        classification = "POTENTIAL PROMPT INJECTION"

    # Determine security decision based on active settings
    if level == "Critical":
        decision = "Blocked" if auto_block else "Approval required"
    elif level == "High":
        decision = "Approval required" if high_risk_approval else "Blocked"
    elif level == "Medium":
        decision = "Approval required"
    else:
        decision = "Allowed"

    # Explanations and remediations (never contains raw sensitive input)
    if hits and pii_found:
        explanation = f"Detected {len(hits)} suspicious pattern(s) and {len(pii_found)} sensitive data occurrence(s)."
    elif hits:
        explanation = f"Detected malicious pattern(s): {', '.join(hits)}."
    elif pii_found:
        explanation = f"Detected sensitive data pattern(s): {', '.join(p[0] for p in pii_found)}."
    else:
        explanation = "No predefined threat indicators or sensitive data patterns matched."

    if decision == "Allowed":
        remediation = "No action needed. Prompt satisfies baseline security policy."
    elif decision == "Blocked":
        remediation = "Block the request immediately and log the incident to audit records."
    else:
        remediation = "Route request to human reviewer for manual approval; mask sensitive values."

    return {
        "classification": classification,
        "risk_score": score,
        "risk_level": level,
        "detected_indicators": hits,
        "sensitive_data": pii_found,
        "decision": decision,
        "explanation": explanation,
        "remediation": remediation,
        "raw_score": raw_score,
    }
