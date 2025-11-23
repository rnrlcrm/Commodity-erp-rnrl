"""
Abuse Prevention System

Detects and blocks malicious activity including:
- Bot detection
- SQL injection attempts
- XSS attacks
- Credential stuffing
- Suspicious behavior patterns
"""

from .detector import AbuseDetector, AbuseType, AbuseEvent
from .patterns import PatternMatcher, MaliciousPatterns
from .ip_reputation import IPReputationChecker

__all__ = [
    "AbuseDetector",
    "AbuseType",
    "AbuseEvent",
    "PatternMatcher",
    "MaliciousPatterns",
    "IPReputationChecker",
]
