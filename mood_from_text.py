from __future__ import annotations
import re


def detect_mood(text: str) -> str:
    t = (text or "").lower().strip()

    # relax
    if re.search(r"stres|anx|panic|calm|relax|linist|chill|obosit|tired|sleep", t):
        return "relax"

    # sad
    if re.search(r"trist|sad|deprim|down|plang|heartbreak|singur|melanc", t):
        return "sad"

    # angry
    if re.search(r"nervos|furios|angry|rage|frustrat|hate|agresiv|descarc", t):
        return "angry"

    # focus
    if re.search(r"invat|study|focus|concentr|munca|work|licenta|proiect", t):
        return "focus"

    # happy (default la vibes bune)
    if re.search(r"fericit|happy|party|chef|energie|upbeat|buna dispoz", t):
        return "happy"

    # fallback
    return "happy"