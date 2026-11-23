"""Conservative preflight warnings for obvious cross-industry contradictions.

This is not semantic validation. Users can explicitly confirm an intentional cross-industry use.
"""
import re

AVIATION = re.compile(r"\b(?:aircraft|airframe|airline|aviation|aerospace|apu|engine overhaul|mro|flight maintenance)\b", re.I)
RETAIL = re.compile(r"\b(?:retail|grocery|point.of.sale|\bpos\b|stockout|store inventory|merchandise|sku)\b", re.I)

def context_warnings(organization: str, industry: str, challenge: str, context: str):
    label = f"{organization} {industry}".lower()
    problem = challenge.strip()
    details = context.strip()
    warnings = []
    if re.search(r"\b(?:retail|grocery|supermarket|merchandis)\w*\b",label) and AVIATION.search(problem) and not RETAIL.search(problem):
        warnings.append("The organization/industry appears retail, but the strategic challenge focuses on aviation. Confirm that this is intentional.")
    if re.search(r"\b(?:aviation|aerospace|airline|aircraft|mro)\b",label) and RETAIL.search(problem) and not AVIATION.search(problem):
        warnings.append("The organization/industry appears aviation, but the strategic challenge focuses on retail. Confirm that this is intentional.")
    if re.search(r"\b(?:aviation|aerospace|airline|aircraft|mro)\b",label) and re.search(r"\b(?:retail point.of.sale|retail pos)\b",details, re.I):
        warnings.append("The context mentions retail point-of-sale systems for an aviation organization. Verify the system requirements.")
    return warnings
