import re
from collections import Counter

from src.config import settings

# ─── Prompt Injection Detection ───────────────────────────────────────

# Pre-compile regex patterns (faster than re.search() with a string each time)
_INJECTION_PATTERNS = [
    re.compile(r"ignore\s+(your\s+)?(all\s+)?(previous\s+)?instructions?", re.IGNORECASE),
    re.compile(r"you\s+are\s+(now\s+)?(DAN|a\s+new|no\s+longer)", re.IGNORECASE),
    re.compile(r"system\s*prompt", re.IGNORECASE),
    re.compile(r"pretend\s+you\s+are", re.IGNORECASE),
    re.compile(r"forget\s+(everything|your\s+training)", re.IGNORECASE),
]

# Zero-width and invisible Unicode characters (often used to hide instructions)
_ZERO_WIDTH_CHARS = re.compile(r"[\u200B\u200C\u200D\uFEFF\u200E\u200F]")

# Off-topic keywords (block if no resume keywords are present)
_OFF_TOPIC_KEYWORDS = [
    "hack", "exploit", "illegal", "bomb", "drug", "nsfw", "porn",
    "gambling", "malware", "phishing", "crack", "warez",
]

# Resume-related keywords (if present, the question is probably on-topic)
_RESUME_KEYWORDS = [
    "skill", "experience", "work", "job", "project", "resume", "cv",
    "background", "education", "role", "position", "career", "hire",
    "recruit", "qualification", "anh", "tran", "programming", "language",
    "framework", "tool", "company", "team", "software", "engineer",
    "developer", "backend", "frontend", "fullstack", "cloud",
]

# PII patterns (for output scrubbing)
_EMAIL_RE = re.compile(r"\b[\w.-]+@[\w.-]+\.\w+\b")
_PHONE_RE = re.compile(
    r"\b\+?\d{1,3}[-.\s]?\(?\d{2,4}\)?[-.\s]?\d{2,4}[-.\s]?\d{2,4}\b"
)

def check_prompt_injection(text: str) -> tuple[bool, str]:
    """
    Check user input for prompt injection attempts.
    Returns (True, "") if the text passes all checks.
    Returns (False, "reason") if the text is blocked.
    """
    # 1. Length check — prevent context-stuffing
    if len(text) > 2000:
        return False, "input_too_long"

    # 2. Strip zero-width characters (don't block — they're usually copy-paste artifacts)
    text = _ZERO_WIDTH_CHARS.sub("", text)

    # 3. Check for system prompt override patterns
    for pattern in _INJECTION_PATTERNS:
        if pattern.search(text):
            return False, "prompt_injection_detected"

    # 4. Repeated phrase detection (DoS prevention)
    words = text.lower().split()
    if words:
        wordCounts = Counter(words)
        mostCommonCount = wordCounts.most_common(1)[0][1]
        if mostCommonCount > 20:
            return False, "repeated_phrase_detected"

    return True, ""


def check_content_safety(text: str) -> tuple[bool, str]:
    """
    Check if the question is on-topic for a resume chatbot.
    Returns (True, "") if the text passes.
    Returns (False, "off_topic") if the text is blocked.
    """
    textLower = text.lower()

    # Check for off-topic keywords
    hasOffTopic = any(kw in textLower for kw in _OFF_TOPIC_KEYWORDS)
    hasResumeKw = any(kw in textLower for kw in _RESUME_KEYWORDS)

    # Block only if: off-topic keywords present AND no resume keywords
    if hasOffTopic and not hasResumeKw:
        return False, "off_topic"

    return True, ""

def _build_allowlist() -> tuple[set[str], set[str]]:
    """Parse comma-separated allowed emails/phones from settings."""
    emails = {e.strip() for e in settings.allowed_emails.split(",") if e.strip()}
    phones = {p.strip() for p in settings.allowed_phones.split(",") if p.strip()}
    return emails, phones


def check_pii_leak(text: str) -> str:
    """
    Redact potential PII from LLM output before sending to frontend.
    Returns the text with PII replaced by [REDACTED] markers.
    Emails/phones defined in ALLOWED_EMAILS / ALLOWED_PHONES are preserved.
    """
    allowedEmails, allowedPhones = _build_allowlist()

    # Replace each matched email individually — skip if in allowlist
    def _redact_email(m: re.Match) -> str:
        email = m.group(0)
        return email if email in allowedEmails else "[EMAIL REDACTED]"

    def _redact_phone(m: re.Match) -> str:
        phone = m.group(0)
        return phone if phone in allowedPhones else "[PHONE REDACTED]"

    text = _EMAIL_RE.sub(_redact_email, text)
    text = _PHONE_RE.sub(_redact_phone, text)
    return text
