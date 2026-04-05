import re


class PIIScrubber:
    """
    A lightweight data privacy agent responsible for actively identifying and blocking
    sensitive PII data from traversing outside boundaries before reaching the inference arrays.
    """

    # Common PII Regex Vectors mapping Emails, IPv4, Credit Cards, Social Security strings
    PII_PATTERNS = {
        "EMAIL": r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",
        "IPV4": r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
        "CREDIT_CARD": r"\b(?:\d{4}[ -]?){3}\d{4}\b",
        "SSN": r"\b\d{3}-\d{2}-\d{4}\b",
    }

    @staticmethod
    def redact(text: str) -> str:
        """Sanitizes text by aggressively scrubbing deterministic PII vectors."""
        if not text:
            return text

        scrubbed_text = text
        for pii_type, pattern in PIIScrubber.PII_PATTERNS.items():
            scrubbed_text = re.sub(pattern, f"[REDACTED_{pii_type}]", scrubbed_text)

        return scrubbed_text
